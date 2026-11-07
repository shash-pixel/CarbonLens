"""Smoke tests for CarbonLens page states without API or database calls."""

from streamlit.testing.v1 import AppTest


def analyze_page_showcase() -> None:
    """Render Analyze with a repository that will not be used."""
    from app import initialize_session_state, render_analyze_page

    class UnusedRepository:
        """Placeholder because no request is submitted in this test."""

    initialize_session_state()
    render_analyze_page(UnusedRepository())


def empty_overview_showcase() -> None:
    """Render Overview when no local metadata exists."""

    from app import initialize_session_state, render_overview_page

    class EmptyRepository:
        """Repository substitute with no persisted records."""

        def list_recent(self, limit: int = 500) -> list:
            return []

    initialize_session_state()
    render_overview_page(EmptyRepository())


def empty_history_showcase() -> None:
    """Render History when no local metadata exists."""

    from app import initialize_session_state, render_history_page

    class EmptyRepository:
        """Repository substitute with no persisted records."""

        def list_recent(self, limit: int = 500) -> list:
            return []

    initialize_session_state()
    render_history_page(EmptyRepository())


def test_analyze_page_warns_for_blank_prompt() -> None:
    """Analyze must not send a blank prompt."""
    app = AppTest.from_function(analyze_page_showcase).run()

    assert not app.exception

    app.text_area[0].set_value("   ")
    app.button[0].click().run()

    assert not app.exception
    assert app.warning


def test_overview_renders_empty_state_without_errors() -> None:
    """Overview should guide a new user when history is empty."""
    app = AppTest.from_function(empty_overview_showcase).run()

    assert not app.exception
    assert app.title[0].value == "Overview"
    assert app.info


def test_history_renders_empty_state_without_errors() -> None:
    """History should guide a new user when no records exist."""
    app = AppTest.from_function(empty_history_showcase).run()

    assert not app.exception
    assert app.title[0].value == "History"
    assert app.info