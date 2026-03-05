from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department as DepartmentModel


async def check_and_get_department_by_id(dept_id: int, session: AsyncSession):
    dep_stmt = (
        select(DepartmentModel).
        where(DepartmentModel.id == dept_id)
    )
    dep_db = (await session.scalars(dep_stmt)).one_or_none()
    if dep_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Department ID={dept_id} not found")
    return dep_db


async def validate_unique_name_in_parent(
        name: str,
        parent_id: int | None,
        session: AsyncSession,
):
    dep_stmt = (
        select(DepartmentModel)
        .where(DepartmentModel.id == parent_id,
               DepartmentModel.name == name)
    )
    dep_db = (await session.scalars(dep_stmt)).one_or_none()
    if dep_db is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Name '{name}' already exists in current parent")


async def validate_no_cycle(
        dept_id: int,
        new_parent_id: int | None,
        session: AsyncSession
) -> None:
    if new_parent_id is None or new_parent_id == dept_id:
        if new_parent_id == dept_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Self parent is unavailable")
        return

    result = await session.execute(
        text("""
            WITH RECURSIVE descendants AS (
                SELECT id FROM departments WHERE parent_id = :dept_id
                UNION ALL
                SELECT d.id 
                FROM departments d
                JOIN descendants ds ON d.parent_id = ds.id
            )
            SELECT 1 FROM descendants WHERE id = :new_parent_id
        """),
        {"dept_id": dept_id, "new_parent_id": new_parent_id}
    )

    if result.scalar():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot create circular reference")



