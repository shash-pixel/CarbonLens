"""Smoke tests for reusable CarbonLens Streamlit components."""

from streamlit.testing.v1 import AppTest


def component_showcase() -> None:
    """Render each shared component in a small isolated Streamlit page."""
    import plotly.express as px
    import streamlit as st

    from frontend.components import (
        apply_chart_theme,
        render_empty_state,
        render_kpi_card,
        render_page_header,
        render_reference_notice,
        render_section_heading,
        render_sidebar_navigation,
    )

    render_sidebar_navigation()
    render_page_header(
        "Component check",
        "Verifying CarbonLens reusable interface elements.",
    )

    first_column, second_column = st.columns(2)

    with first_column:
        render_kpi_card(
            "Published energy reference",
            "0.24 Wh",
            "Reference benchmark, not measurement",
        )

    with second_column:
        render_empty_state(
            "No data yet",
            "This is an isolated component test.",
        )

    render_section_heading(
        "Methodology",
        "Published environmental context.",
    )
    render_reference_notice()

    chart = px.bar(
        x=["Reference"],
        y=[0.03],
        labels={"x": "Classification", "y": "g CO₂e"},
    )

    st.plotly_chart(
        apply_chart_theme(chart),
        width="stretch",
        theme=None,
        alt="A published-reference carbon dioxide equivalent chart.",
    )


def test_reusable_components_render_without_errors() -> None:
    """Native CarbonLens components should render in Streamlit."""
    app = AppTest.from_function(component_showcase).run()

    assert not app.exception
    assert app.title[0].value == "Component check"
    assert len(app.info) == 2
