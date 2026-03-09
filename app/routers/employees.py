from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_depends import get_async_session
from app.models import Employee as EmployeeModel
from app.schemas import Employee as EmployeeSchema, EmployeeCreate
from app.services import get_employee_by_id, create_and_get_employee

router = APIRouter(tags=['employees'])


@router.get('/employees/{employee_id}', response_model=EmployeeSchema)
async def get_employee(
        employee_id: int,
        session: AsyncSession = Depends(get_async_session)
):
    employee_db = await get_employee_by_id(employee_id, session)
    return employee_db


@router.post('/departments/{department_id}/employees/', response_model=EmployeeSchema, status_code=201)
async def create_employee_in_department(
        employee: EmployeeCreate,
        session: AsyncSession = Depends(get_async_session)
):
    employee_db = await create_and_get_employee(employee, session)
    return employee_db




