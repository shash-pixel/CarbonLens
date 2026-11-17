"""Reusable Streamlit components for CarbonLens."""

from __future__ import annotations

from typing import Any

import streamlit as st

from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE


NAVIGATION_LABELS = {
    "Overview": ":material/dashboard: Overview",
    "Analyze": ":material/insights: Analyze",
    "History": ":material/history: History",
}


def render_brand() -> None:
    """Render CarbonLens branding inside the sidebar."""
    st.sidebar.title("CarbonLens")
    st.sidebar.caption(":material/eco: Environmental intelligence")
    st.sidebar.caption("LLM inference reference dashboard")


def render_sidebar_navigation() -> str:
    """Render sidebar navigation and return the selected destination."""
    render_brand()
    st.sidebar.divider()
    st.sidebar.caption("WORKSPACE")

    page = st.sidebar.radio(
        "Navigation",
        options=list(NAVIGATION_LABELS),
        format_func=lambda option: NAVIGATION_LABELS[option],
        label_visibility="collapsed",
    )

    st.sidebar.divider()
    st.sidebar.caption("CARBONLENS")
    st.sidebar.caption(
        "Environmental figures are published reference benchmarks, "
        "not direct measurements."
    )

    return page


def render_page_header(title: str, subtitle: str) -> None:
    """Render a consistent page title, product label, and subtitle."""
    st.caption(":material/eco: CARBONLENS WORKSPACE")
    st.title(title)
    st.caption(subtitle)


def render_kpi_card(
    label: str,
    value: str,
    detail: str,
    *,
    icon: str | None = None,
    accent_color: str | None = None,
) -> None:
    """Render a consistent dashboard KPI using native Streamlit elements."""
    del accent_color

    metric_label = (
        f":material/{icon}: {label}"
        if icon is not None
        else label
    )

    with st.container(border=True):
        st.metric(
            metric_label,
            value,
            border=False,
        )
        st.caption(detail)


def render_section_heading(title: str, subtitle: str) -> None:
    """Render a consistent hierarchy for a dashboard section."""
    st.subheader(title)
    st.caption(subtitle)


def render_empty_state(title: str, message: str) -> None:
    """Render a clear empty state with appropriate environmental context."""
    st.info(message, icon=":material/eco:", title=title)


def apply_chart_theme(figure: Any) -> Any:
    """Apply the CarbonLens visual system to a Plotly figure."""
    figure.update_layout(
        paper_bgcolor="#111D29",
        plot_bgcolor="#111D29",
        font={"color": "#F1F5F9", "family": "Inter, Manrope, sans-serif"},
        hoverlabel={
            "bgcolor": "#162433",
            "bordercolor": "#263747",
            "font": {"color": "#F1F5F9"},
        },
        legend={"font": {"color": "#9AAABC"}, "orientation": "h"},
        margin={"l": 12, "r": 12, "t": 30, "b": 12},
        hovermode="x unified",
    )

    figure.update_xaxes(
        gridcolor="#1D2C39",
        linecolor="#263747",
        tickfont={"color": "#9AAABC"},
        title_font={"color": "#9AAABC"},
        zeroline=False,
    )

    figure.update_yaxes(
        gridcolor="#1D2C39",
        linecolor="#263747",
        tickfont={"color": "#9AAABC"},
        title_font={"color": "#9AAABC"},
        zeroline=False,
    )

    return figure


def render_reference_notice() -> None:
    """Display the benchmark methodology explanation without overclaiming."""
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
    st.caption(f"Method: {GOOGLE_GEMINI_APPS_REFERENCE.method_name}")
