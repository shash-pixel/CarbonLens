"""Shared Streamlit styling for CarbonLens."""

from textwrap import dedent

import streamlit as st


def apply_theme() -> None:
    """Apply the premium dark CarbonLens dashboard design system."""
    st.markdown(
        dedent(
            """
            <style>
                :root {
                    --carbon-bg: #080F17;
                    --carbon-sidebar: #0D1722;
                    --carbon-surface: #111D29;
                    --carbon-surface-raised: #162433;
                    --carbon-border: #263747;
                    --carbon-text: #F1F5F9;
                    --carbon-text-secondary: #9AAABC;
                    --carbon-text-muted: #718096;
                    --carbon-accent: #36C58A;
                    --carbon-accent-soft: #83DDB4;
                }

                .stApp,
                [data-testid="stAppViewContainer"] {
                    background: var(--carbon-bg);
                    color: var(--carbon-text);
                }

                [data-testid="stMainBlockContainer"] {
                    max-width: 1540px;
                    padding: 2rem 2.35rem 2.75rem;
                }

                [data-testid="stSidebar"] {
                    background: var(--carbon-sidebar);
                    border-right: 1px solid var(--carbon-border);
                }

                [data-testid="stSidebar"] > div:first-child {
                    padding: 1.65rem 1rem;
                }

                h1, h2, h3, p, span, label, button, input, textarea {
                    font-family: Inter, Manrope, "Segoe UI", sans-serif;
                }

                h1 {
                    color: var(--carbon-text);
                    font-size: 2rem !important;
                    font-weight: 650 !important;
                    letter-spacing: -0.035em;
                    margin-bottom: 0.2rem !important;
                }

                h2, h3 {
                    color: var(--carbon-text);
                    font-weight: 600 !important;
                    letter-spacing: -0.02em;
                }

                [data-testid="stCaptionContainer"] {
                    color: var(--carbon-text-secondary);
                }

                [data-testid="stMetric"],
                [data-testid="stVerticalBlockBorderWrapper"] {
                    background: var(--carbon-surface);
                    border: 1px solid var(--carbon-border);
                    border-radius: 12px;
                }

                [data-testid="stMetric"] {
                    min-height: 120px;
                    padding: 1.1rem 1.2rem;
                }

                [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMetric"] {
                    background: transparent;
                    border: 0;
                    min-height: auto;
                    padding: 0;
                }

                [data-testid="stMetricLabel"] {
                    color: var(--carbon-text-secondary);
                    font-size: 0.82rem;
                    font-weight: 550;
                }

                [data-testid="stMetricValue"] {
                    color: var(--carbon-text);
                    font-weight: 650;
                    letter-spacing: -0.035em;
                }

                .stButton > button {
                    min-height: 2.65rem;
                    border-radius: 8px;
                    border: 1px solid var(--carbon-border);
                    font-weight: 600;
                    transition: background-color 160ms ease, border-color 160ms ease,
                        transform 160ms ease;
                }

                .stButton > button:hover {
                    border-color: #3C5264;
                    transform: translateY(-1px);
                }

                .stButton > button[kind="primary"] {
                    background: var(--carbon-accent);
                    border-color: var(--carbon-accent);
                    color: #07120E;
                }

                .stButton > button[kind="primary"]:hover {
                    background: var(--carbon-accent-soft);
                    border-color: var(--carbon-accent-soft);
                    color: #07120E;
                }

                [data-baseweb="select"] > div,
                [data-baseweb="input"] > div,
                [data-baseweb="textarea"] > div {
                    background: var(--carbon-surface-raised) !important;
                    border-color: var(--carbon-border) !important;
                    border-radius: 8px !important;
                    color: var(--carbon-text) !important;
                }

                textarea, input {
                    color: var(--carbon-text) !important;
                }

                [data-testid="stDataFrame"] {
                    border: 1px solid var(--carbon-border);
                    border-radius: 10px;
                    overflow: hidden;
                }

                [data-testid="stDataFrame"] [role="columnheader"] {
                    background: #162433;
                    color: var(--carbon-text-secondary);
                    font-size: 0.76rem;
                    font-weight: 650;
                    letter-spacing: 0.02em;
                }

                [data-testid="stDataFrame"] [role="gridcell"] {
                    border-bottom-color: #1D2C39;
                }

                [data-testid="stExpander"] {
                    background: var(--carbon-surface);
                    border: 1px solid var(--carbon-border);
                    border-radius: 10px;
                }

                [data-testid="stAlert"] {
                    border-radius: 10px;
                    border: 1px solid var(--carbon-border);
                }

                [data-testid="stDivider"] {
                    border-color: var(--carbon-border);
                    margin: 1.75rem 0;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label {
                    border-left: 2px solid transparent;
                    border-radius: 8px;
                    margin: 0.2rem 0;
                    padding: 0.48rem 0.5rem;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label:hover {
                    background: #162433;
                }

                [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
                    background: #162433;
                    border-left-color: var(--carbon-accent);
                    color: var(--carbon-text);
                }

                [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {
                    color: var(--carbon-accent-soft);
                    font-weight: 650;
                }

                @media (max-width: 780px) {
                    [data-testid="stMainBlockContainer"] {
                        padding: 1.4rem 1rem 2rem;
                    }

                    h1 {
                        font-size: 1.7rem !important;
                    }

                    [data-testid="stMetric"] {
                        min-height: auto;
                    }
                }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )
