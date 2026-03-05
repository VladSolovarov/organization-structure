from app.db_depends import get_async_session
from fastapi import APIRouter, Query, Body, Depends
from app.schemas import Department as DepartmentSchema, DepartmentCreate

from app.services import (
    create_and_get_department, update_and_get_department,
)
from app.validators import validate_no_cycle, check_and_get_department_by_id

router = APIRouter(
    prefix='/departments',
    tags=['departments']
)


@router.post('/', response_model=DepartmentSchema, status_code=201)
async def create_department(
        name: str = Query(min_length=1, max_length=200),
        parent_id: int | None = None,
        session = Depends(get_async_session)
):
    department = DepartmentCreate(name=name.strip(), parent_id=parent_id)
    department_db = await create_and_get_department(department, session)
    return department_db



@router.get('/{department_id}')
async def get_department_detail(
        department_id: int,
        depth: int = Query(default=1, le=5, description="Depth of nested departments"),
        include_employees: bool = Query(default=True, description="Show employees in response"),
        session = Depends(get_async_session)
) -> dict:
    department_db = await check_and_get_department_by_id(department_id, session)
    return {
        'department': department_db,
        'employees': '',
        'children': ''
    }


@router.patch('/{department_id}', response_model=DepartmentSchema)
async def update_department(
        department_id: int,
        name: str | None = Body(default=None, min_length=1, max_length=200),
        parent_id: int | None = Body(default=None),
        session = Depends(get_async_session)
):
    department_db = await update_and_get_department(department_id, name.strip(), parent_id, session)
    return department_db


@router.delete('/{department_id}', status_code=204)
async def delete_department(
        department_id: int,
        mode: str = Query(pattern=r"^(cascade|reassign)$"),
        reassign_to_department_id: int | None = None,
        session = Depends(get_async_session)
):
    ...