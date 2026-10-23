"""SQLite connection and schema setup."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    """Create SQLite connections and initialize CarbonLens tables."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self) -> sqlite3.Connection:
        """Return a connection whose rows can be accessed by column name."""
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        """Create the database folder, table, and safe schema upgrades."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS inference_records (
                    request_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL,
                    latency_ms REAL,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    total_tokens INTEGER,
                    provider_request_id TEXT,
                    reference_energy_wh REAL,
                    reference_carbon_gco2e REAL,
                    estimation_method TEXT,
                    estimation_classification TEXT,
                    estimation_note TEXT,
                    error_category TEXT,
                    error_message TEXT
                )
                """
            )

            existing_columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(inference_records)"
                ).fetchall()
            }

            if "estimation_classification" not in existing_columns:
                connection.execute(
                    """
                    ALTER TABLE inference_records
                    ADD COLUMN estimation_classification TEXT
                    """
                )