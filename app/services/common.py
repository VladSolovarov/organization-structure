from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Department as DepartmentModel, Employee as EmployeeModel
from app.validators import check_department_exists, check_employee_exists


async def get_model_by_id(model_id: int,
                          model_class: type[EmployeeModel] | type[DepartmentModel],
                          session: AsyncSession):
    stmt = (
        select(model_class).
        where(model_class.id == model_id)
    )
    model_db = (await session.scalars(stmt)).one_or_none()

    if model_class is DepartmentModel:
        check_department_exists(model_db)

    elif model_class is EmployeeModel:
        check_employee_exists(model_db)

    return model_db


async def get_department_by_id(dept_id: int, session: AsyncSession):
    return await get_model_by_id(dept_id, DepartmentModel, session)


async def get_employee_by_id(emp_id: int, session: AsyncSession):
    return await get_model_by_id(emp_id, EmployeeModel, session)


async def get_employees_by_department_id(dept_id: int, session: AsyncSession):
    await get_department_by_id(dept_id, session)
    emp_stmt = (
        select(EmployeeModel)
        .where(EmployeeModel.department_id == dept_id)
        .order_by(asc(EmployeeModel.full_name))
    )
    emp_db = (await session.scalars(emp_stmt)).all()
    return emp_db
