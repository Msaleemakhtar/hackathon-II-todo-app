from typing import Optional

from sqlmodel import Field, SQLModel


class TaskTagLink(SQLModel, table=True):
    __tablename__ = "task_tag_link"

    task_id: Optional[int] = Field(
        default=None, foreign_key="tasks.id", primary_key=True
    )
    tag_id: Optional[int] = Field(
        default=None, foreign_key="tags.id", primary_key=True
    )