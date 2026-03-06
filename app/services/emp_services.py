from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Employee as EmployeeModel
from app.schemas import EmployeeCreate
from app.services.common import get_department_by_id


async def create_and_get_employee(emp: EmployeeCreate, session: AsyncSession):
    await get_department_by_id(emp.department_id, session)

    employee = EmployeeModel(**emp.model_dump())
    session.add(employee)
    await session.commit()
    await session.refresh(employee)
    return employee


