from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from .user import User
    from .task import Task


class TagBase(SQLModel):
    name: str = Field(max_length=50, index=True)
    color: Optional[str] = Field(
        default=None, regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )  # Hex color code, e.g., #RRGGBB or #RGB

    user_id: str = Field(foreign_key="users.id", index=True)


class Tag(TagBase, table=True):
    __tablename__ = "tags"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    user: "User" = Relationship(back_populates="tags")
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        sa_relationship_kwargs={"secondary": "task_tag_link"}
    )

    # Unique constraint on (name, user_id)
    __table_args__ = (UniqueConstraint("name", "user_id", name="uq_tag_name_user"),)


class TagRead(TagBase):
    id: int
    user_id: str


class TagCreate(TagBase):
    pass


class TagUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(
        default=None, regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    )