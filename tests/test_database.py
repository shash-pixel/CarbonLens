from datetime import UTC, datetime

from storage.database import Database
from storage.repository import RequestRepository
from tracking.usage_tracker import TrackedInference


def make_record(
    request_id: str = "request-1",
    status: str = "success",
) -> TrackedInference:
    return TrackedInference(
        request_id=request_id,
        timestamp=datetime.now(UTC),
        provider="google",
        model="gemini-2.5-flash",
        status=status,
        latency_ms=120.5 if status == "success" else None,
        input_tokens=10 if status == "success" else None,
        output_tokens=20 if status == "success" else None,
        total_tokens=30 if status == "success" else None,
        reference_energy_wh=0.24 if status == "success" else None,
        reference_carbon_gco2e=0.03 if status == "success" else None,
        estimation_method=(
            "Google published benchmark"
            if status == "success"
            else "unavailable"
        ),
        estimation_classification=(
            "reference_benchmark"
            if status == "success"
            else "unavailable"
        ),
        estimation_note="Test record",
        response_text="This response must not be stored.",
    )


def test_repository_saves_safe_metadata_not_response_text(tmp_path) -> None:
    database = Database(tmp_path / "carbonlens.db")
    database.initialize()
    repository = RequestRepository(database)

    repository.save(make_record())

    stored_record = repository.list_recent()[0]

    assert stored_record.request_id == "request-1"
    assert stored_record.total_tokens == 30
    assert stored_record.reference_energy_wh == 0.24
    assert stored_record.response_text is None
    assert stored_record.estimation_classification == "reference_benchmark"
    assert stored_record.response_text is None


def test_schema_has_no_prompt_or_response_columns(tmp_path) -> None:
    database = Database(tmp_path / "carbonlens.db")
    database.initialize()

    with database.connect() as connection:
        columns = connection.execute(
            "PRAGMA table_info(inference_records)"
        ).fetchall()

    column_names = {column["name"] for column in columns}

    assert "prompt" not in column_names
    assert "response_text" not in column_names


def test_clear_all_removes_local_history(tmp_path) -> None:
    database = Database(tmp_path / "carbonlens.db")
    database.initialize()
    repository = RequestRepository(database)

    repository.save(make_record(request_id="request-1"))
    repository.save(make_record(request_id="request-2"))

    repository.clear_all()

    assert repository.list_recent() == []