from sqlalchemy import select, update

from app.schemas.dept_schemas import DepartmentCreate
from app.models import Department as DepartmentModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.validators import (
    check_and_get_department_by_id, validate_unique_name_in_parent,
    validate_no_cycle,
)


async def create_and_get_department(dep_data: DepartmentCreate, session: AsyncSession):
    if dep_data.parent_id is not None:
        await check_and_get_department_by_id(dep_data.parent_id, session) #Error if department not exists
    await validate_unique_name_in_parent(dep_data.name, dep_data.parent_id, session) #Error if name already exists

    department = DepartmentModel(**dep_data.model_dump())
    session.add(department)
    await session.commit()
    await session.refresh(department)
    return department


async def update_and_get_department(dept_id: int, name: str | None,
                                    new_parent_id: int | None, session: AsyncSession):
    dep_db = await check_and_get_department_by_id(dept_id, session)
    values_for_update = dict()
    if name:
        await validate_unique_name_in_parent(name, dept_id, session)
        values_for_update |= {'name': name}

    if new_parent_id:
        await check_and_get_department_by_id(new_parent_id, session)
        await validate_no_cycle(dept_id, new_parent_id, session)
        values_for_update |= {'parent_id': new_parent_id}

    await session.execute(
        update(DepartmentModel)
        .where(DepartmentModel.id == dept_id)
        .values(**values_for_update)
    )
    await session.commit()
    await session.refresh(dep_db)
    return dep_db
