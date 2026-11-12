from sqlalchemy.orm import Session

from app.core.embedding import EMBEDDING_DIMENSIONS
from app.repositories.document import create_document
from app.repositories.document_chunk import create_document_chunks
from app.repositories.workspace import create_workspace
from app.schemas.document import DocumentCreate
from app.schemas.workspace import WorkspaceCreate
from app.services.text_chunker import chunk_text


def test_create_document_chunks_persists_all_chunks(
    db_session: Session,
):
    workspace = create_workspace(
        db_session,
        WorkspaceCreate(
            name="Chunking Workspace",
            description=None,
        ),
    )

    document = create_document(
        db_session,
        workspace.id,
        DocumentCreate(
            title="Chunking Test",
            content="ABCDEFGHIJ",
            source_url=None,
        ),
    )

    chunks = chunk_text(
        document.content,
        chunk_size=4,
        overlap=1,
    )

    embeddings = [
        [float(index)] * EMBEDDING_DIMENSIONS
        for index in range(len(chunks))
    ]

    stored_chunks = create_document_chunks(
        db_session,
        document,
        chunks,
        embeddings,
    )

    assert len(stored_chunks) == 3
    assert [chunk.chunk_index for chunk in stored_chunks] == [
        0,
        1,
        2,
    ]
    assert all(
        chunk.document_id == document.id
        for chunk in stored_chunks
    )

    assert [
        stored_chunk.content
        for stored_chunk in stored_chunks
    ] == [
        chunk.content
        for chunk in chunks
    ]
    assert [
        (stored_chunk.start_offset, stored_chunk.end_offset)
        for stored_chunk in stored_chunks
    ] == [
        (chunk.start_offset, chunk.end_offset)
        for chunk in chunks
    ]
    assert [
        stored_chunk.embedding
        for stored_chunk in stored_chunks
    ] == embeddings