"""Shared Streamlit styling for CarbonLens."""

import streamlit as st


def apply_theme() -> None:
    """Apply the dark sustainability-themed CarbonLens appearance."""
    st.markdown(
        """
        <style>
            .stApp {
                background-color: #071019;
                color: #E7EEF3;
            }

            [data-testid="stSidebar"] {
                background-color: #0A1520;
                border-right: 1px solid #20313E;
            }

            [data-testid="stMetric"] {
                background-color: #0E1B27;
                border: 1px solid #20313E;
                border-radius: 8px;
                padding: 1rem;
            }

            .reference-note {
                background-color: #112331;
                border-left: 3px solid #38B779;
                border-radius: 4px;
                color: #C4D1DA;
                font-size: 0.9rem;
                line-height: 1.5;
                padding: 1rem;
            }

            .stButton > button[kind="primary"] {
                background-color: #38B779;
                border-color: #38B779;
                color: #071019;
                font-weight: 600;
            }

            .stButton > button[kind="primary"]:hover {
                background-color: #82D9AE;
                border-color: #82D9AE;
                color: #071019;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )