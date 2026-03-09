from typing import Sequence

from sqlalchemy import select, update

from app.schemas import DepartmentDeleteMode, DepartmentCreate
from app.models import Department as DepartmentModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.common import (
    get_department_by_id,
    get_employees_by_department_id,
    reassign_employees_to_department,
)

from app.validators import (
    validate_unique_name_in_parent,
    validate_no_cycle, validate_reassign_mode,
    validate_no_child_department,
)


async def get_recursive_department_detail(
        dept_id: int,
        depth: int,
        include_employees: bool,
        session: AsyncSession,
) -> dict[str, str | int | Sequence | list]:
    dept_db = await get_department_by_id(dept_id, session)
    base = {
        'id': dept_db.id,
        'name': dept_db.name,
        'parent_id': dept_db.parent_id,
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

    if under_departments:
        base |= {'children': under_departments}

    return base


async def delete_department_by_id(
        dept_id: int,
        mode: DepartmentDeleteMode,
        reassign_to_dept_id: int | None,
        session: AsyncSession
) -> None:
    dept = await get_department_by_id(dept_id, session)

    if mode == DepartmentDeleteMode.REASSIGN:
        await get_department_by_id(reassign_to_dept_id, session)
        validate_reassign_mode(dept_id, reassign_to_dept_id)
        await validate_no_child_department(dept_id, reassign_to_dept_id, session)
        await reassign_employees_to_department(dept_id, reassign_to_dept_id, session)

    await session.delete(dept)
    await session.commit()


async def get_children_by_id(dept_id: int,
                             session: AsyncSession) -> Sequence[DepartmentModel]:
    dept_stmt = (
        select(DepartmentModel)
        .where(DepartmentModel.parent_id == dept_id)
    )
    return (await session.scalars(dept_stmt)).all()


async def create_and_get_department(dept_data: DepartmentCreate,
                                    session: AsyncSession):
    if dept_data.parent_id is not None:
        await get_department_by_id(dept_data.parent_id, session) # Error if department not found
    await validate_unique_name_in_parent(dept_data.name, dept_data.parent_id, session) # Error if name already exists in the same parent

    department = DepartmentModel(**dept_data.model_dump())
    session.add(department)
    await session.commit()
    await session.refresh(department)
    return department


async def update_and_get_department(
        dept_id: int,
        name: str | None,
        new_parent_id: int | None,
        session: AsyncSession,
):
    dept_db = await get_department_by_id(dept_id, session)
    values_for_update = dict()
    if name is not None:
        await validate_unique_name_in_parent(name, dept_id, session)
        values_for_update |= {'name': name}

    if new_parent_id is not None:
        await get_department_by_id(new_parent_id, session)
        await validate_no_cycle(dept_id, new_parent_id, session)
        values_for_update |= {'parent_id': new_parent_id}

    await session.execute(
        update(DepartmentModel)
        .where(DepartmentModel.id == dept_id)
        .values(**values_for_update)
    )
    await session.commit()
    await session.refresh(dept_db)
    return dept_db


