import functools
from dataclasses import dataclass

import pyotp
from aiograpi import Client

from app.domain.errors import UnauthorizedError


@dataclass(frozen=True)
class Credentials:
    login: str
    password: str
    secret: str | None


def catch_error(func):  # noqa: ANN001, ANN201
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        try:
            return await func(self, *args, **kwargs)
        except Exception as e:
            raise UnauthorizedError(e) from e

    return wrapper


@dataclass
class InstagramClient:
    cl: Client
    credentials: Credentials

    def __post_init__(self) -> None:
        self.cl.delay_range = [5, 7]

    @catch_error
    async def _login_with_session(self, session: dict) -> None:
        self.cl.set_settings(session)
        await self.cl.get_timeline_feed()

    @catch_error
    async def _login_with_credentials(self) -> dict:
        await self.cl.login(self.credentials.login, self.credentials.password)
        return self.cl.get_settings()

    @catch_error
    async def _login_with_2fa(self) -> dict:
        code = pyotp.TOTP(self.credentials.secret)
        await self.cl.login(
            self.credentials.login,
            self.credentials.password,
            verification_code=code.now(),
        )
        return self.cl.get_settings()

    async def login(self, session: dict | None) -> dict | None:
        if session:
            return await self._login_with_session(session)
        if self.credentials.secret:
            return await self._login_with_2fa()
        return await self._login_with_credentials()

    @catch_error
    async def send_message(self, text: str, username: str) -> None:
        user_id = await self.cl.user_id_from_username(username)
        await self.cl.direct_send(text=text, user_ids=[user_id])

    @catch_error
    async def follow_user(self, user_id: int) -> None:
        await self.cl.user_follow(user_id)

    @catch_error
    async def like_post(self, post_id: int) -> None:
        await self.cl.media_like(post_id)
