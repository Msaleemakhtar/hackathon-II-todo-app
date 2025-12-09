from sqlmodel import Field, SQLModel


class TaskTagLink(SQLModel, table=True):
    """Junction table for many-to-many Task-Tag relationship."""

    __tablename__ = "task_tag_link"

    task_id: int = Field(
        foreign_key="tasks.id", primary_key=True, description="Task reference"
    )
    tag_id: int = Field(
        foreign_key="tags.id", primary_key=True, description="Tag reference"
    )
