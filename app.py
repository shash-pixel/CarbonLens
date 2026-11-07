"""CarbonLens Streamlit application entry point."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from analytics.analytics_service import (
    daily_reference_emissions,
    daily_request_activity,
    filter_history_dataframe,
    history_summary,
    records_to_dataframe,
)
from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE
from frontend.components import (
    apply_chart_theme,
    render_empty_state,
    render_kpi_card,
    render_page_header,
    render_reference_notice,
    render_section_heading,
    render_sidebar_navigation,
)
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
    st.session_state.setdefault("last_record", None)
    st.session_state.setdefault("last_error", None)


def submit_prompt(
    prompt: str,
    model: str,
    repository: RequestRepository,
) -> None:
    """Call Gemini once, track the result, and persist safe metadata."""
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
    """Display the active-session response and associated metadata."""
    st.divider()
    render_section_heading(
        "Generated response",
        "Response content is displayed for this session only.",
    )

    st.write(record.response_text)

    latency_column, input_column, output_column = st.columns(3)

    with latency_column:
        render_kpi_card(
            "Request latency",
            f"{record.latency_ms:.0f} ms",
            "Application-side measurement",
        )

    with input_column:
        input_value = (
            str(record.input_tokens)
            if record.input_tokens is not None
            else "Not reported"
        )

        render_kpi_card(
            "Input tokens",
            input_value,
            "Provider-reported metadata",
        )

    with output_column:
        output_value = (
            str(record.output_tokens)
            if record.output_tokens is not None
            else "Not reported"
        )

        render_kpi_card(
            "Output tokens",
            output_value,
            "Provider-reported metadata",
        )

    st.caption(
        "Environmental reference context — not a direct measurement "
        "of this individual API request."
    )

    energy_column, emissions_column = st.columns(2)

    with energy_column:
        energy_value = (
            f"{record.reference_energy_wh:.2f} Wh"
            if record.reference_energy_wh is not None
            else "Unavailable"
        )

        render_kpi_card(
            "Published energy reference",
            energy_value,
            "Google Gemini Apps benchmark",
        )

    with emissions_column:
        emissions_value = (
            f"{record.reference_carbon_gco2e:.2f} g CO₂e"
            if record.reference_carbon_gco2e is not None
            else "Unavailable"
        )

        render_kpi_card(
            "Published emissions reference",
            emissions_value,
            "Reference benchmark, not measurement",
        )

    with st.expander("Methodology and request metadata"):
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


def get_filtered_dashboard_data(
    records: list[TrackedInference],
    key_prefix: str,
) -> tuple[pd.DataFrame, list[TrackedInference]]:
    """Render date/model filters and return matching dataframe and records."""
    dataframe = records_to_dataframe(records)

    if dataframe.empty:
        return dataframe, []

    timestamps = pd.to_datetime(
        dataframe["timestamp"],
        errors="coerce",
        utc=True,
    ).dropna()

    if timestamps.empty:
        return dataframe.iloc[0:0].copy(), []

    minimum_date = timestamps.min().date()
    maximum_date = timestamps.max().date()

    filter_column, model_column, refresh_column = st.columns(
        [2, 2, 1],
        vertical_alignment="bottom",
    )

    with filter_column:
        selected_dates = st.date_input(
            "Time range",
            value=(minimum_date, maximum_date),
            min_value=minimum_date,
            max_value=maximum_date,
            key=f"{key_prefix}_date_range",
        )

    with model_column:
        models = sorted(dataframe["model"].dropna().unique().tolist())

        selected_model = st.selectbox(
            "Model",
            options=["All models", *models],
            key=f"{key_prefix}_model",
        )

    with refresh_column:
        if st.button(
            "Refresh",
            key=f"{key_prefix}_refresh",
            width="stretch",
        ):
            st.rerun()

    if (
        isinstance(selected_dates, (tuple, list))
        and len(selected_dates) == 2
    ):
        start_date, end_date = selected_dates
    else:
        start_date = selected_dates
        end_date = selected_dates

    filtered_dataframe = filter_history_dataframe(
        dataframe=dataframe,
        start_date=start_date,
        end_date=end_date,
        model=selected_model,
    )

    matching_ids = set(filtered_dataframe["request_id"].tolist())

    filtered_records = [
        record
        for record in records
        if record.request_id in matching_ids
    ]

    return filtered_dataframe, filtered_records


def render_overview_page(repository: RequestRepository) -> None:
    """Render the main sustainability analytics dashboard."""
    render_page_header(
        "Overview",
        "Monitor Gemini usage, latency, and published environmental reference context.",
    )

    records = repository.list_recent(limit=500)

    if not records:
        render_empty_state(
            "No request history yet",
            "Go to Analyze, submit a Gemini prompt, and CarbonLens will "
            "create your first local record.",
        )

        st.divider()
        render_section_heading(
            "Methodology",
            "How CarbonLens presents environmental context.",
        )
        render_reference_notice()
        return

    dataframe, filtered_records = get_filtered_dashboard_data(
        records=records,
        key_prefix="overview",
    )

    if filtered_records:
        summary = history_summary(filtered_records)
    else:
        summary = history_summary([])

    total_carbon = (
        f"{summary.published_reference_carbon_total_gco2e:.2f} g CO₂e"
        if summary.published_reference_carbon_total_gco2e is not None
        else "Unavailable"
    )

    average_latency = (
        f"{summary.average_latency_ms:.0f} ms"
        if summary.average_latency_ms is not None
        else "Unavailable"
    )

    total_column, metadata_column, latency_column, carbon_column = (
        st.columns(4)
    )

    with total_column:
        render_kpi_card(
            "Recorded requests",
            str(summary.total_requests),
            f"{summary.successful_requests} successful",
        )

    with metadata_column:
        render_kpi_card(
            "Token metadata available",
            str(summary.token_metadata_count),
            "Successful requests with provider metadata",
        )

    with latency_column:
        render_kpi_card(
            "Average request latency",
            average_latency,
            "Successful requests only",
        )

    with carbon_column:
        render_kpi_card(
            "Published-reference CO₂e",
            total_carbon,
            "Benchmark total, not measured emissions",
        )

    st.divider()

    emissions_column, activity_column = st.columns(2)

    daily_emissions = daily_reference_emissions(dataframe)
    daily_activity = daily_request_activity(dataframe)

    with emissions_column:
        render_section_heading(
            "Environmental reference trend",
            "Aggregates Google’s published benchmark values only.",
        )

        if daily_emissions.empty:
            render_empty_state(
                "No reference trend available",
                "No eligible published-reference records exist in this filter range.",
            )
        else:
            emissions_chart = px.bar(
                daily_emissions,
                x="date",
                y="reference_carbon_gco2e",
                labels={
                    "date": "Date",
                    "reference_carbon_gco2e": (
                        "Published-reference total (g CO₂e)"
                    ),
                },
                color_discrete_sequence=["#38B779"],
            )

            emissions_chart.update_layout(height=300)

            st.plotly_chart(
                apply_chart_theme(emissions_chart),
                width="stretch",
                theme=None,
                alt=(
                    "Published-reference carbon dioxide equivalent totals "
                    "by day."
                ),
            )

    with activity_column:
        render_section_heading(
            "Request activity",
            "Actual CarbonLens records created over time.",
        )

        if daily_activity.empty:
            render_empty_state(
                "No activity data available",
                "Generate a Gemini response to begin building activity history.",
            )
        else:
            activity_chart = px.line(
                daily_activity,
                x="date",
                y="request_count",
                markers=True,
                labels={
                    "date": "Date",
                    "request_count": "Recorded requests",
                },
                color_discrete_sequence=["#82D9AE"],
            )

            activity_chart.update_layout(height=300)

            st.plotly_chart(
                apply_chart_theme(activity_chart),
                width="stretch",
                theme=None,
                alt="Recorded CarbonLens request activity by day.",
            )

    st.divider()

    recent_column, methodology_column = st.columns([3, 2])

    with recent_column:
        render_section_heading(
            "Recent request activity",
            "Latest persisted metadata. Prompts and responses are not stored.",
        )

        if dataframe.empty:
            render_empty_state(
                "No records in this range",
                "Change the filters or generate another response.",
            )
        else:
            recent_columns = [
                "timestamp",
                "model",
                "status",
                "latency_ms",
                "total_tokens",
                "reference_carbon_gco2e",
            ]

            st.dataframe(
                dataframe[recent_columns].head(5),
                width="stretch",
                hide_index=True,
                alt="Five most recent CarbonLens request metadata records.",
            )

    with methodology_column:
        render_section_heading(
            "Methodology insight",
            "Why values are labelled as published references.",
        )
        render_reference_notice()


def render_analyze_page(repository: RequestRepository) -> None:
    """Render the Gemini prompt-to-response workflow."""
    render_page_header(
        "Analyze",
        "Run a Gemini prompt and inspect its available inference metadata.",
    )

    analysis_column, reference_column = st.columns([3, 2])

    with analysis_column:
        render_section_heading(
            "Prompt workspace",
            "CarbonLens sends a request only when you select Generate response.",
        )

        model = st.selectbox(
            "Gemini model",
            options=["gemini-3.5-flash-lite"],
            help="CarbonLens currently supports Gemini text generation.",
        )

        prompt = st.text_area(
            "Prompt",
            placeholder="Ask a question or describe a task...",
            height=180,
            max_chars=20_000,
        )

        submitted = st.button(
            "Generate response",
            type="primary",
            width="stretch",
        )

        if submitted:
            if not prompt.strip():
                st.warning("Enter a prompt before generating a response.")

            elif not os.getenv("GEMINI_API_KEY"):
                st.error(
                    "GEMINI_API_KEY is not configured. "
                    "Add it to a local .env file and restart Streamlit."
                )

            else:
                submit_prompt(
                    prompt=prompt.strip(),
                    model=model,
                    repository=repository,
                )

    with reference_column:
        render_section_heading(
            "Environmental context",
            "Published reference values retained with eligible records.",
        )

        render_kpi_card(
            "Published energy reference",
            f"{GOOGLE_GEMINI_APPS_REFERENCE.energy_wh:.2f} Wh",
            "Google Gemini Apps benchmark",
        )

        render_kpi_card(
            "Published emissions reference",
            f"{GOOGLE_GEMINI_APPS_REFERENCE.carbon_gco2e:.2f} g CO₂e",
            "Reference benchmark, not measurement",
        )

        render_reference_notice()

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.last_record:
        render_result(st.session_state.last_record)


def render_local_data_controls(repository: RequestRepository) -> None:
    """Render the confirmation flow for clearing local metadata."""
    st.divider()
    render_section_heading(
        "Local data controls",
        "Clearing history permanently removes locally stored request metadata.",
    )

    confirmed = st.checkbox(
        "I understand that clearing local history cannot be undone.",
        key="clear_history_confirmation",
    )

    if st.button(
        "Clear local history",
        disabled=not confirmed,
    ):
        repository.clear_all()
        st.session_state.last_record = None
        st.success("Local history cleared.")
        st.rerun()


def render_history_page(repository: RequestRepository) -> None:
    """Render filtered request history and safe record details."""
    render_page_header(
        "History",
        "Review locally persisted request metadata and published reference context.",
    )

    records = repository.list_recent(limit=500)

    if not records:
        render_empty_state(
            "No history available",
            "Generate a Gemini response from Analyze to create the first record.",
        )
        return

    dataframe, filtered_records = get_filtered_dashboard_data(
        records=records,
        key_prefix="history",
    )

    if dataframe.empty:
        render_empty_state(
            "No matching records",
            "Change the selected date range or model filter.",
        )
        render_local_data_controls(repository)
        return

    render_section_heading(
        "Request history",
        "Only metadata is stored. Prompts and generated responses remain private.",
    )

    history_columns = [
        "timestamp",
        "provider",
        "model",
        "status",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "latency_ms",
        "reference_energy_wh",
        "reference_carbon_gco2e",
        "estimation_classification",
    ]

    st.dataframe(
        dataframe[history_columns],
        width="stretch",
        hide_index=True,
        alt="Filtered CarbonLens request metadata history.",
    )

    st.divider()
    render_section_heading(
        "Request details",
        "Inspect safe metadata for one stored request.",
    )

    records_by_id = {
        record.request_id: record
        for record in filtered_records
    }

    selected_request_id = st.selectbox(
        "Select a stored request",
        options=list(records_by_id.keys()),
        format_func=lambda request_id: (
            f"{records_by_id[request_id].timestamp.strftime('%Y-%m-%d %H:%M')} "
            f"— {records_by_id[request_id].model} "
            f"— {request_id[:8]}"
        ),
    )

    selected_record = records_by_id[selected_request_id]

    st.json(
        {
            "request_id": selected_record.request_id,
            "timestamp": selected_record.timestamp.isoformat(),
            "provider": selected_record.provider,
            "model": selected_record.model,
            "status": selected_record.status,
            "input_tokens": selected_record.input_tokens,
            "output_tokens": selected_record.output_tokens,
            "total_tokens": selected_record.total_tokens,
            "latency_ms": selected_record.latency_ms,
            "reference_energy_wh": selected_record.reference_energy_wh,
            "reference_carbon_gco2e": (
                selected_record.reference_carbon_gco2e
            ),
            "estimation_method": selected_record.estimation_method,
            "estimation_classification": (
                selected_record.estimation_classification
            ),
            "error_category": selected_record.error_category,
        }
    )

    render_local_data_controls(repository)


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
    page = render_sidebar_navigation()

    if page == "Overview":
        render_overview_page(repository)

    elif page == "Analyze":
        render_analyze_page(repository)

    else:
        render_history_page(repository)


if __name__ == "__main__":
    main()
