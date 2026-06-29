from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.db.session import Base


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    instagram_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    instagram_password: Mapped[str] = mapped_column(String(120), nullable=False)
    instagram_secret: Mapped[str | None] = mapped_column(String(32), nullable=True)

    status: Mapped[str] = mapped_column(String, nullable=False, default="active")


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    instagram_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    instagram_thread_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    instagram_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    status: Mapped[str] = mapped_column(String, nullable=False, default="active")

    worker_name: Mapped[str] = mapped_column(
        String, ForeignKey("workers.instagram_name"), nullable=False
    )
    worker: Mapped[Worker] = relationship(Worker)
