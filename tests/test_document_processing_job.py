import uuid
from unittest.mock import MagicMock, Mock

from app.jobs import document_processing


def test_process_document_job_orchestrates_processing(
    monkeypatch,
):
    document_id = uuid.uuid4()

    engine = Mock()
    session = Mock()

    session_context = MagicMock()
    session_context.__enter__.return_value = session

    session_factory = Mock(
        return_value=session_context,
    )

    document = Mock(id=document_id)
    processed_document = Mock(id=document_id)
    embedding_provider = Mock()

    get_document = Mock(
        return_value=document,
    )
    process_document = Mock(
        return_value=processed_document,
    )

    monkeypatch.setattr(
        document_processing,
        "Settings",
        Mock(return_value=Mock()),
    )
    monkeypatch.setattr(
        document_processing,
        "create_db_engine",
        Mock(return_value=engine),
    )
    monkeypatch.setattr(
        document_processing,
        "create_session_factory",
        Mock(return_value=session_factory),
    )
    monkeypatch.setattr(
        document_processing,
        "get_document",
        get_document,
    )
    monkeypatch.setattr(
        document_processing,
        "get_embedding_provider",
        Mock(return_value=embedding_provider),
    )
    monkeypatch.setattr(
        document_processing,
        "process_document",
        process_document,
    )

    result = document_processing.process_document_job(
        str(document_id),
    )

    assert result == str(document_id)

    get_document.assert_called_once_with(
        session,
        document_id,
    )

    process_document.assert_called_once_with(
        session,
        document,
        embedding_provider=embedding_provider,
    )

    engine.dispose()