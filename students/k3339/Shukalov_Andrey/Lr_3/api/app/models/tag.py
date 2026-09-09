from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.task import Task


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("owner_id", "name"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(7), default="#64748B")
    task_links: Mapped[list[TaskTag]] = relationship(
        back_populates="tag", cascade="all, delete-orphan", passive_deletes=True
    )


class TaskTag(Base):
    __tablename__ = "task_tags"
    __table_args__ = (CheckConstraint("relevance BETWEEN 1 AND 5", name="relevance_range"),)
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    # Relevance belongs to this specific association, not to the tag itself.
    relevance: Mapped[int] = mapped_column(default=3)
    task: Mapped[Task] = relationship(back_populates="tag_links")
    tag: Mapped[Tag] = relationship(back_populates="task_links")
