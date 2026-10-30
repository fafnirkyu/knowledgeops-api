# KnowledgeOps API

KnowledgeOps is a production-oriented document-processing and knowledge API built incrementally with FastAPI.

The project currently provides tested workspace and document APIs backed by PostgreSQL. Planned capabilities include asynchronous document ingestion, semantic search and RAG, application containerization, and AWS deployment.

## Implemented

- FastAPI application with health, workspace, and document endpoints
- PostgreSQL development database through Docker Compose
- Typed environment configuration with Pydantic Settings
- SQLAlchemy 2.x models, relationships, engine, and session management
- Versioned database migrations with Alembic
- Workspace create, list, retrieve, partial update, and delete operations
- Document create, workspace-scoped listing, and retrieval operations
- Workspace-to-document foreign-key relationship with cascading deletion
- Isolated schema, model, repository, and API tests using pytest and SQLite

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/workspaces` | Create a workspace |
| `GET` | `/workspaces` | List workspaces |
| `GET` | `/workspaces/{workspace_id}` | Retrieve one workspace |
| `PATCH` | `/workspaces/{workspace_id}` | Partially update a workspace |
| `DELETE` | `/workspaces/{workspace_id}` | Delete a workspace |
| `POST` | `/workspaces/{workspace_id}/documents` | Create a document in a workspace |
| `GET` | `/workspaces/{workspace_id}/documents` | List documents in a workspace |
| `GET` | `/documents/{document_id}` | Retrieve one document |

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
