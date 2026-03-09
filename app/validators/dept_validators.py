from fastapi import HTTPException, status
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department as DepartmentModel


def check_department_exists(dept_db: DepartmentModel | None) -> None:
    if dept_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Department not found")


async def validate_unique_name_in_parent(
        name: str,
        parent_id: int | None,
        session: AsyncSession,
) -> None:
    dept_stmt = (
        select(DepartmentModel)
        .where(
            DepartmentModel.parent_id == parent_id,
            DepartmentModel.name == name)
    )
    dept_db = (await session.scalars(dept_stmt)).one_or_none()
    if dept_db is not None:
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



def validate_reassign_mode(dept_id: int,
                                 reassign_to_dept_id: int):
    if not type(reassign_to_dept_id) is int:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="'reassign mode' requires reassign to department id (integer)")

    if dept_id == reassign_to_dept_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='cannot reassign to itself')


async def validate_no_child_department(
        parent_id: int,
        child_id: int,
        session: AsyncSession
) -> None:
    child_exception = HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='cannot reassign to child department')

    if parent_id == child_id:
        raise child_exception

    child = await session.get(DepartmentModel, child_id)
    while child and child.parent_id:
        if child.parent_id == parent_id:
            raise child_exception
        child = await session.get(DepartmentModel, child.parent_id)

