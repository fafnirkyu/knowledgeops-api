from fastapi import FastAPI

from app.routers import health, workspaces

app = FastAPI()

app.include_router(health.router)
app.include_router(workspaces.router)
