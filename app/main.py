from fastapi import FastAPI

from app.routers import answers, documents, health, search, workspaces

app = FastAPI()

app.include_router(health.router)
app.include_router(workspaces.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(answers.router)