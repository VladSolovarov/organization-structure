from sqlalchemy import select, update

from app.schemas.dept_schemas import DepartmentCreate
from app.models import Department as DepartmentModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.common import get_department_by_id, get_employees_by_department_id
from app.validators import (
    validate_unique_name_in_parent,
    validate_no_cycle,
)


async def get_recursive_department_detail(
        dept_id: int,
        depth: int,
        include_employees: bool,
        session: AsyncSession,
):

    dep_db = await get_department_by_id(dept_id, session)
    base = {
        'id': dep_db.id,
        'name': dep_db.name,
        'parent_id': dep_db.parent_id,
    }
    if include_employees:
        base |= {'employees': await get_employees_by_department_id(dept_id, session)}

    if depth <= 1:
        return base

    children = await get_children_by_id(dept_id, session)
    under_departments = list()
    for child in children:
        under_departments.append(
            await get_recursive_department_detail(
                child.id, depth - 1, include_employees, session)
        )
    base['children'] = under_departments
    return base



async def get_children_by_id(dept_id: int, session: AsyncSession):
    dep_stmt = (
        select(DepartmentModel)
        .where(DepartmentModel.parent_id == dept_id)
    )
    return (await session.scalars(dep_stmt)).all()


async def create_and_get_department(dep_data: DepartmentCreate, session: AsyncSession):
    if dep_data.parent_id is not None:
        await get_department_by_id(dep_data.parent_id, session) # Error if department not found
    await validate_unique_name_in_parent(dep_data.name, dep_data.parent_id, session) # Error if name already exists in the same parent

    department = DepartmentModel(**dep_data.model_dump())
    session.add(department)
    await session.commit()
    await session.refresh(department)
    return department


async def update_and_get_department(dept_id: int, name: str | None,
                                    new_parent_id: int | None, session: AsyncSession):
    dep_db = await get_department_by_id(dept_id, session)
    values_for_update = dict()
    if name:
        await validate_unique_name_in_parent(name, dept_id, session)
        values_for_update |= {'name': name}

    if new_parent_id:
        await get_department_by_id(new_parent_id, session)
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
