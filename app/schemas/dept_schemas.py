from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class DepartmentBase(BaseModel):
    name: Annotated[str, Field(
        min_length=1,
        max_length=200,
        description="Department name"
    )]
    parent_id: Annotated[int | None, Field(description="Parent id")]


class Department(DepartmentBase):
    id: Annotated[int, Field(description="Unique department id")]
    created_at: Annotated[datetime, Field(
        default_factory=datetime.now,
        description="Timestamp when employee was created"
    )]

    model_config = ConfigDict(from_attributes=True,
                              str_strip_whitespace=True)


class DepartmentCreate(DepartmentBase):
    pass
