"""Reusable Streamlit components for CarbonLens."""

from __future__ import annotations

import streamlit as st

from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE


def render_brand() -> None:
    """Render CarbonLens branding inside the sidebar."""
    st.sidebar.title("CarbonLens")
    st.sidebar.caption("LLM Carbon Intelligence")


def render_sidebar_navigation() -> str:
    """Render sidebar navigation and return the selected destination."""
    render_brand()

    page = st.sidebar.radio(
        "Navigation",
        options=["Overview", "Analyze", "History"],
        label_visibility="collapsed",
    )

    st.sidebar.divider()

    st.sidebar.caption(
        "Environmental figures are published reference benchmarks, "
        "not direct measurements."
    )

    return page


def render_page_header(title: str, subtitle: str) -> None:
    """Render a consistent page title and subtitle."""
    st.title(title)
    st.caption(subtitle)


def render_kpi_card(
    label: str,
    value: str,
    detail: str,
) -> None:
    """Render a bordered KPI card using native Streamlit elements."""
    with st.container(border=True):
        st.caption(label)
        st.subheader(value)
        st.caption(detail)


def render_section_heading(
    title: str,
    subtitle: str,
) -> None:
    """Render a consistent section heading."""
    st.subheader(title)
    st.caption(subtitle)


def render_empty_state(
    title: str,
    message: str,
) -> None:
    """Render a clear empty state."""
    st.info(
        message,
        icon=":material/eco:",
        title=title,
    )


def apply_chart_theme(figure):
    """Apply CarbonLens colors to an existing Plotly figure."""
    figure.update_layout(
        paper_bgcolor="#0E1B27",
        plot_bgcolor="#0E1B27",
        font={"color": "#E7EEF3", "family": "Arial, sans-serif"},
        hoverlabel={
            "bgcolor": "#112331",
            "bordercolor": "#20313E",
            "font": {"color": "#E7EEF3"},
        },
        legend={
            "font": {"color": "#93A4B3"},
        },
        margin={"l": 10, "r": 10, "t": 25, "b": 10},
    )

    figure.update_xaxes(
        gridcolor="#20313E",
        linecolor="#20313E",
        tickfont={"color": "#93A4B3"},
        title_font={"color": "#93A4B3"},
    )

    figure.update_yaxes(
        gridcolor="#20313E",
        linecolor="#20313E",
        tickfont={"color": "#93A4B3"},
        title_font={"color": "#93A4B3"},
    )

    return figure


def render_reference_notice() -> None:
    """Display the benchmark methodology explanation."""
    st.info(
        (
            "Based on Google's published median Gemini Apps text-prompt "
            "benchmark from May 2025. Actual impact can differ because "
            "the serving hardware, infrastructure, workload, and "
            "electricity supply are not directly observable."
        ),
        icon=":material/info:",
        title="Reference, not measurement",
    )

    st.caption(
        f"Method: {GOOGLE_GEMINI_APPS_REFERENCE.method_name}"
    )