from fastapi import FastAPI

from backend.management_apis.auth import router as auth_router
from backend.management_apis.farms import router as farm_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(farm_router)