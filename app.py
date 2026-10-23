"""CarbonLens Streamlit application entry point."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from analytics.analytics_service import (
    history_summary,
    records_to_dataframe,
)
from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE
from frontend.components import render_reference_notice
from frontend.styles import apply_theme
from integrations.gemini_client import GeminiClient, ProviderError
from storage.database import Database
from storage.repository import RequestRepository
from tracking.usage_tracker import (
    TrackedInference,
    build_failed_record,
    build_success_record,
)

PROJECT_ROOT = Path(__file__).parent

load_dotenv(PROJECT_ROOT / ".env")


@st.cache_resource
def get_repository() -> RequestRepository:
    """Create the local SQLite repository once per Streamlit server."""
    database = Database(PROJECT_ROOT / "data" / "carbonlens.db")
    database.initialize()

    return RequestRepository(database)


def initialize_session_state() -> None:
    """Create session variables only during the user's first app visit."""
    if "last_record" not in st.session_state:
        st.session_state.last_record = None

    if "last_error" not in st.session_state:
        st.session_state.last_error = None


def submit_prompt(
    prompt: str,
    model: str,
    repository: RequestRepository,
) -> None:
    """Call Gemini once, create a tracked record, and persist safe metadata."""
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        with st.spinner("Generating response with Gemini..."):
            provider_result, latency_ms = client.generate(
                prompt=prompt,
                model=model,
            )

        record = build_success_record(
            provider_result=provider_result,
            latency_ms=latency_ms,
        )

        repository.save(record)

        st.session_state.last_record = record
        st.session_state.last_error = None

    except ProviderError as error:
        failed_record = build_failed_record(
            provider="google",
            model=model,
            error_category=error.category,
            error_message=str(error),
        )

        repository.save(failed_record)

        st.session_state.last_record = None
        st.session_state.last_error = str(error)


def render_result(record: TrackedInference) -> None:
    """Display the current response and request-specific safe metadata."""
    st.divider()
    st.subheader("Gemini response")
    st.write(record.response_text)

    latency_column, input_column, output_column = st.columns(3)

    latency_column.metric(
        "Request latency",
        f"{record.latency_ms:.0f} ms",
    )

    input_column.metric(
        "Input tokens",
        record.input_tokens
        if record.input_tokens is not None
        else "Not reported",
    )

    output_column.metric(
        "Output tokens",
        record.output_tokens
        if record.output_tokens is not None
        else "Not reported",
    )

    st.caption(
        "Environmental reference context — not a direct measurement "
        "of this individual API request."
    )

    energy_column, emissions_column = st.columns(2)

    energy_column.metric(
        "Published energy reference",
        f"{record.reference_energy_wh:.2f} Wh"
        if record.reference_energy_wh is not None
        else "Unavailable",
    )

    emissions_column.metric(
        "Published emissions reference",
        f"{record.reference_carbon_gco2e:.2f} g CO₂e"
        if record.reference_carbon_gco2e is not None
        else "Unavailable",
    )

    with st.expander("Request methodology and metadata"):
        st.write(record.estimation_note)

        st.json(
            {
                "request_id": record.request_id,
                "timestamp": record.timestamp.isoformat(),
                "provider": record.provider,
                "model": record.model,
                "status": record.status,
                "total_tokens": record.total_tokens,
                "estimation_method": record.estimation_method,
                "estimation_classification": (
                    record.estimation_classification
                ),
            }
        )


def render_analysis_page(repository: RequestRepository) -> None:
    """Render the prompt-to-response workflow."""
    st.title("CarbonLens")
    st.caption(
        "Gemini inference tracking with transparent environmental reference context."
    )

    analysis_column, reference_column = st.columns([2, 1])

    with analysis_column:
        st.subheader("Ask Gemini")

        model = st.selectbox(
            "Gemini model",
            options=["gemini-3.5-flash-lite"],
            help="CarbonLens currently supports Gemini text generation.",
        )

        prompt = st.text_area(
            "Prompt",
            placeholder="Ask a question or describe a task...",
            height=160,
            max_chars=20_000,
        )

        submitted = st.button(
            "Generate response",
            type="primary",
            use_container_width=True,
        )

        if submitted:
            if not prompt.strip():
                st.warning("Enter a prompt before generating a response.")

            elif not os.getenv("GEMINI_API_KEY"):
                st.error(
                    "GEMINI_API_KEY is not configured. "
                    "Add it to a local .env file and try again."
                )

            else:
                submit_prompt(
                    prompt=prompt.strip(),
                    model=model,
                    repository=repository,
                )

    with reference_column:
        st.subheader("Environmental context")

        st.metric(
            "Published energy reference",
            f"{GOOGLE_GEMINI_APPS_REFERENCE.energy_wh:.2f} Wh",
        )

        st.metric(
            "Published emissions reference",
            f"{GOOGLE_GEMINI_APPS_REFERENCE.carbon_gco2e:.2f} g CO₂e",
        )

        render_reference_notice()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.last_record:
        render_result(st.session_state.last_record)


def render_history_page(repository: RequestRepository) -> None:
    """Render the persisted request dashboard and local history."""
    st.title("Dashboard & history")

    records = repository.list_recent(limit=200)
    summary = history_summary(records)

    requests_column, references_column, carbon_column, latency_column = (
        st.columns(4)
    )

    requests_column.metric(
        "Recorded requests",
        summary.total_requests,
    )

    references_column.metric(
        "Requests with references",
        summary.reference_benchmark_count,
    )

    carbon_column.metric(
        "Published-reference total",
        (
            f"{summary.published_reference_carbon_total_gco2e:.2f} g CO₂e"
            if summary.published_reference_carbon_total_gco2e is not None
            else "Unavailable"
        ),
    )

    latency_column.metric(
        "Average latency",
        (
            f"{summary.average_latency_ms:.0f} ms"
            if summary.average_latency_ms is not None
            else "Unavailable"
        ),
    )

    st.caption(
        "Published-reference totals are not measured emissions of your "
        "individual Gemini API requests."
    )

    if not records:
        st.info(
            "No requests are stored yet. Generate a Gemini response to create "
            "your first local record."
        )
        return

    dataframe = records_to_dataframe(records)

    reference_dataframe = dataframe[
        (dataframe["status"] == "success")
        & (
            dataframe["estimation_classification"]
            == "reference_benchmark"
        )
        & dataframe["reference_carbon_gco2e"].notna()
    ].copy()

    if not reference_dataframe.empty:
        reference_dataframe["date"] = pd.to_datetime(
            reference_dataframe["timestamp"]
        ).dt.date

        daily_reference_totals = (
            reference_dataframe.groupby(
                "date",
                as_index=False,
            )["reference_carbon_gco2e"]
            .sum()
        )

        st.subheader("Published-reference emissions over time")

        chart = px.bar(
            daily_reference_totals,
            x="date",
            y="reference_carbon_gco2e",
            labels={
                "date": "Date",
                "reference_carbon_gco2e": (
                    "Published-reference total (g CO₂e)"
                ),
            },
            template="plotly_dark",
        )

        chart.update_layout(
            height=320,
            margin={"left": 0, "right": 0, "top": 20, "bottom": 0},
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
        )

    st.subheader("Recent request history")

    display_columns = [
        "timestamp",
        "provider",
        "model",
        "status",
        "latency_ms",
        "input_tokens",
        "output_tokens",
        "reference_energy_wh",
        "reference_carbon_gco2e",
        "estimation_classification",
        "error_category",
    ]

    st.dataframe(
        dataframe[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Local data controls")

    st.warning(
        "Clearing history permanently removes locally stored CarbonLens "
        "request metadata."
    )

    confirmed = st.checkbox(
        "I understand that clearing local history cannot be undone.",
    )

    if st.button(
        "Clear local history",
        disabled=not confirmed,
    ):
        repository.clear_all()
        st.session_state.last_record = None
        st.success("Local history cleared.")
        st.rerun()


def main() -> None:
    """Configure and render CarbonLens."""
    st.set_page_config(
        page_title="CarbonLens",
        page_icon="◌",
        layout="wide",
    )

    apply_theme()
    initialize_session_state()

    repository = get_repository()

    page = st.sidebar.radio(
        "Navigate",
        options=["Analyze", "Dashboard & history"],
    )

    st.sidebar.caption("Inference reference estimator")

    if page == "Analyze":
        render_analysis_page(repository)
    else:
        render_history_page(repository)


if __name__ == "__main__":
    main()