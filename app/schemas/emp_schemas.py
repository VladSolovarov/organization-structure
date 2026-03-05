from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class EmployeeBase(BaseModel):
    department_id: Annotated[int, Field(description="Department id")]
    full_name: Annotated[str, Field(
        min_length=1,
        max_length=200,
        description="Employee's full name (first and last)"
    )]
    position: Annotated[str, Field(
        min_length=1,
        max_length=200,
        description="Employee's position"
    )]
    hired_at: Annotated[datetime | None, Field(
        default=None,
        description="Timestamp when employee hired at (or null)"
    )]


class Employee(EmployeeBase):
    id: Annotated[int, Field(description="Unique department id")]
    created_at: Annotated[datetime, Field(
        default_factory=datetime.now,
        description="Timestamp when employee was created")]

    model_config = ConfigDict(from_attributes=True)


class EmployeeCreate(EmployeeBase):
    pass
