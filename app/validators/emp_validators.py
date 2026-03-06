from fastapi import HTTPException, status

from app.models import Employee as EmployeeModel

def check_employee_exists(emp_db: EmployeeModel):
    if emp_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Employee not found')