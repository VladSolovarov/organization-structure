from fastapi import FastAPI
#from app.routers import departments, employees

app = FastAPI(
    title="Тестовое задание Hitalent: API организационной структуры.",
)

#app.include_router(departments.router)
#app.include_router(employees.router)