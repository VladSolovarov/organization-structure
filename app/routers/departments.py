from app.db_depends import get_async_session
from fastapi import APIRouter, Query, Body, Depends

from app.schemas import (
    Department as DepartmentSchema,
    DepartmentCreate,
    DepartmentDeleteMode
)

from app.services import (
    create_and_get_department, update_and_get_department,
    get_recursive_department_detail, delete_department_by_id
)


router = APIRouter(
    prefix='/departments',
    tags=['departments']
)


@router.post('/', response_model=DepartmentSchema, status_code=201)
async def create_department(
        department: DepartmentCreate,
        session = Depends(get_async_session)
):
    department_db = await create_and_get_department(department, session)
    return department_db


@router.get('/{department_id}')
async def get_department_detail(
        department_id: int,
        depth: int = Query(default=1, le=5, description="Depth of nested departments"),
        include_employees: bool = Query(default=True, description="Show employees in response"),
        session = Depends(get_async_session)
):
    response = await get_recursive_department_detail(department_id, depth, include_employees, session)
    return response


@router.patch('/{department_id}', response_model=DepartmentSchema)
async def update_department(
        department_id: int,
        name: str | None = Body(default=None, min_length=1, max_length=200),
        parent_id: int | None = Body(default=None),
        session = Depends(get_async_session)
):
    if name is not None:
        name = name.strip()
    department_db = await update_and_get_department(department_id, name, parent_id, session)
    return department_db


@router.delete('/{department_id}')
async def delete_department(
        department_id: int,
        mode: DepartmentDeleteMode,
        reassign_to_department_id: int | None = None,
        session = Depends(get_async_session)
):
    await delete_department_by_id(department_id, mode, reassign_to_department_id, session)
    return {"status": "success",
            "message": "department has been deleted"}
