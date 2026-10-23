"""Reusable Streamlit components."""

import streamlit as st

from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE


def render_reference_notice() -> None:
    """Display a clear explanation of the published environmental benchmark."""
    st.markdown(
        """
        <div class="reference-note">
            <strong>Reference, not measurement</strong><br>
            Based on Google's published median Gemini Apps text-prompt benchmark
            from May 2025. These values are not direct measurements of this API
            request. Actual impact may differ because serving hardware,
            infrastructure, workload, and electricity supply are not observable.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"Method: {GOOGLE_GEMINI_APPS_REFERENCE.method_name}"
    )