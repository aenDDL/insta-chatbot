from dataclasses import dataclass

from app.adapters.files import Files
from app.adapters.instagram_client import InstagramAuth
from app.domain.errors import UnauthorizedError


@dataclass(frozen=True)
class Credentials:
    login: str
    password: str
    secret: str | None


@dataclass
class InstagramLoginService:
    auth: InstagramAuth
    credentials: Credentials
    files: Files

    async def login(self) -> None:
        session = await self.files.load_instagram_session()
        if session:
            try:
                return await self.auth.login_with_session(session)
            except UnauthorizedError:
                pass

        if self.credentials.secret:
            session = await self.auth.login_with_2fa(
                self.credentials.login,
                self.credentials.password,
                self.credentials.secret,
            )
        else:
            session = await self.auth.login_with_credentials(
                self.credentials.login,
                self.credentials.password,
            )

        return await self.files.save_instagram_session(session)
