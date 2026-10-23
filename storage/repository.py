"""Repository functions for persisted CarbonLens request metadata."""

from __future__ import annotations

from datetime import datetime

from storage.database import Database
from tracking.usage_tracker import TrackedInference


class RequestRepository:
    """Save and retrieve safe inference metadata."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, record: TrackedInference) -> None:
        """Persist metadata while deliberately excluding session-only response text."""
        values = {
            "request_id": record.request_id,
            "timestamp": record.timestamp.isoformat(),
            "provider": record.provider,
            "model": record.model,
            "status": record.status,
            "latency_ms": record.latency_ms,
            "input_tokens": record.input_tokens,
            "output_tokens": record.output_tokens,
            "total_tokens": record.total_tokens,
            "provider_request_id": record.provider_request_id,
            "reference_energy_wh": record.reference_energy_wh,
            "reference_carbon_gco2e": record.reference_carbon_gco2e,
            "estimation_method": record.estimation_method,
            "estimation_classification": record.estimation_classification,
            "estimation_note": record.estimation_note,
            "error_category": record.error_category,
            "error_message": record.error_message,
        }

        with self.database.connect() as connection:
            connection.execute(
                """
                INSERT INTO inference_records (
                    request_id,
                    timestamp,
                    provider,
                    model,
                    status,
                    latency_ms,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    provider_request_id,
                    reference_energy_wh,
                    reference_carbon_gco2e,
                    estimation_method,
                    estimation_classification,
                    estimation_note,
                    error_category,
                    error_message
                )
                VALUES (
                    :request_id,
                    :timestamp,
                    :provider,
                    :model,
                    :status,
                    :latency_ms,
                    :input_tokens,
                    :output_tokens,
                    :total_tokens,
                    :provider_request_id,
                    :reference_energy_wh,
                    :reference_carbon_gco2e,
                    :estimation_method,
                    :estimation_classification,
                    :estimation_note,
                    :error_category,
                    :error_message
                )
                """,
                values,
            )

    def list_recent(self, limit: int = 100) -> list[TrackedInference]:
        """Return newest records first, without response text."""
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM inference_records
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [self._record_from_row(row) for row in rows]

    def clear_all(self) -> None:
        """Delete all locally stored request metadata."""
        with self.database.connect() as connection:
            connection.execute("DELETE FROM inference_records")

    @staticmethod
    def _record_from_row(row: object) -> TrackedInference:
        """Convert one SQLite row back into the tracking model."""
        values = dict(row)
        values["timestamp"] = datetime.fromisoformat(values["timestamp"])

        return TrackedInference(
            **values,
            response_text=None,
        )