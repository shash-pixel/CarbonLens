# CarbonLens

CarbonLens is a Python and Streamlit project for running Gemini prompts, recording available inference metadata, and presenting transparent environmental context.

## Current status

Module 1 establishes the project foundation and methodology.

It does not yet include:

- Gemini API integration
- Streamlit interface
- SQLite persistence
- Request history
- Dashboard charts

## Environmental reference

CarbonLens uses Google's published median Gemini Apps text-prompt benchmark from its May 2025 analysis:

- Published energy reference: **0.24 Wh**
- Published emissions reference: **0.03 g CO₂e**

These are reference benchmarks, not direct measurements of an individual Gemini API request. CarbonLens will not multiply them by token count or latency.

Read [the methodology](docs/estimation_methodology.md) for details.

## Planned technology

- Python 3.11+
- Streamlit
- Google GenAI SDK
- SQLite
- Pandas
- Plotly
- pytest
- Ruff