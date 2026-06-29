from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from app.domain.models import InstagramCredentials, InstagramThread, Target, Worker
from app.infrastructure import db_models


def target_to_domain(orm_obj: db_models.Target) -> Target:
    mapper = inspect(orm_obj.__class__)
    data = {attr.key: getattr(orm_obj, attr.key) for attr in mapper.column_attrs}
    return Target(**data)


def worker_to_domain(orm_obj: db_models.Worker) -> Worker:
    mapper = inspect(orm_obj.__class__)
    data = {attr.key: getattr(orm_obj, attr.key) for attr in mapper.column_attrs}
    return Worker(**data)


class TargetsRepo:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_worker(self, instagram_name: str) -> db_models.Worker | None:
        stmt = select(db_models.Worker).where(
            db_models.Worker.instagram_name == instagram_name
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_target(self, thread_id: str) -> Target | None:
        stmt = select(db_models.Target).where(
            db_models.Target.instagram_thread_id == thread_id
        )
        result = await self.db.execute(stmt)
        target = result.scalars().first()
        if target:
            return target_to_domain(target)
        return None

    async def add_target(self, data: InstagramThread, worker_username: str) -> Target:
        target = db_models.Target(
            instagram_user_id=data.sender_id,
            instagram_thread_id=data.thread_id,
            instagram_name=data.sender_username,
            worker=await self._get_worker(worker_username),
        )
        self.db.add(target)
        await self.db.commit()
        await self.db.refresh(target)
        return target_to_domain(target)

    async def update_target_status(self, thread_id: str, status: str) -> Target:
        target: db_models.Target = await self.get_target(thread_id)
        target.status = status
        await self.db.commit()
        await self.db.refresh(target)
        return target_to_domain(target)


class WorkersRepo:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_worker(self, username: str) -> Worker | None:
        stmt = select(db_models.Worker).where(
            db_models.Worker.instagram_name == username
        )
        result = await self.db.execute(stmt)
        worker = result.scalars().first()
        if worker:
            return worker_to_domain(worker)
        return None

    async def add_worker(self, credentials: InstagramCredentials) -> Worker:
        worker = db_models.Worker(
            instagram_name=credentials.username,
            instagram_password=credentials.password,
            instagram_secret=credentials.secret,
        )
        self.db.add(worker)
        await self.db.commit()
        await self.db.refresh(worker)
        return worker_to_domain(worker)
