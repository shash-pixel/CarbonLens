# CarbonLens

CarbonLens is a Python and Streamlit application that sends prompts to Gemini, records available inference metadata, and presents transparent environmental reference context.

## Features

- Gemini text-generation integration through the official Google GenAI SDK
- Application-side request latency measurement
- Provider-reported input, output, and total token metadata when available
- Google's published Gemini Apps environmental reference benchmark:
  - 0.24 Wh published energy reference
  - 0.03 g CO₂e published emissions reference
- SQLite request-history persistence
- Dashboard summary metrics and emissions-reference chart
- Privacy-first storage: prompts and responses are not stored by default
- Automated tests and Ruff linting

## Important methodology note

The displayed 0.24 Wh and 0.03 g CO₂e values are Google's published median Gemini Apps text-prompt benchmark from its May 2025 analysis.

They are not direct measurements of an individual Gemini API request.

CarbonLens does not multiply these values by tokens, words, or latency. The dashboard labels aggregated values as published-reference totals rather than measured emissions.

See [the estimation methodology](docs/estimation_methodology.md).

## Technology stack

- Python 3.11+
- Streamlit
- Google GenAI SDK
- SQLite
- Pandas
- Plotly
- pytest
- Ruff

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1