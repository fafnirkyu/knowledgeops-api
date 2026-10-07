# KnowledgeOps API

KnowledgeOps is a production-oriented document-processing and knowledge API built incrementally with FastAPI.

The project currently provides a tested workspace API backed by PostgreSQL. Planned capabilities include asynchronous document ingestion, semantic search and RAG, containerization, and AWS deployment.

## Implemented

- FastAPI application with health and workspace endpoints
- PostgreSQL development database through Docker Compose
- Typed environment configuration with Pydantic Settings
- SQLAlchemy 2.x models, engine, and session management
- Alembic database migrations
- Workspace create, list, retrieve, partial update, and delete operations
- Isolated repository and API tests using pytest and SQLite

## Workspace endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/workspaces` | Create a workspace |
| `GET` | `/workspaces` | List workspaces |
| `GET` | `/workspaces/{workspace_id}` | Retrieve one workspace |
| `PATCH` | `/workspaces/{workspace_id}` | Partially update a workspace |
| `DELETE` | `/workspaces/{workspace_id}` | Delete a workspace |

Interactive API documentation is available at `/docs` while the application is running.

## Local development

Create a local `.env` file from `.env.example`, then start PostgreSQL and apply the migrations:

```powershell
docker compose up -d db
alembic upgrade head
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

Run the test suite:

```powershell
python -m pytest -q
```
