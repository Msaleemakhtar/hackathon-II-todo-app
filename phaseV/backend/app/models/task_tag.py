from sqlmodel import Field, SQLModel


class TaskTags(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between tasks and tags.
    Allows tasks to have multiple tags and tags to be applied to multiple tasks.
    """

    __tablename__ = "task_tags"

    task_id: int = Field(foreign_key="tasks_phaseiii.id", primary_key=True, nullable=False)
    tag_id: int = Field(foreign_key="tags_phasev.id", primary_key=True, nullable=False)
