# CarbonLens Implementation Plan

## Module 1: Foundation and methodology

- Create project configuration files.
- Document the Google Gemini Apps reference benchmark.
- Add a small published-reference model.
- Add a unit-safe carbon conversion helper.
- Add focused tests.

## Module 2: Gemini integration and request tracking

- Create the Gemini client module.
- Load `GEMINI_API_KEY` from `.env`.
- Submit one prompt through the Gemini API.
- Measure request latency.
- Parse available token metadata.
- Handle provider errors safely.

## Module 3: SQLite persistence

- Create the database schema.
- Save safe request metadata.
- Do not store prompts or responses by default.
- Add repository tests.

## Module 4: Streamlit analysis screen

- Add prompt input and Generate button.
- Show the Gemini response.
- Show latency and available token metadata.
- Show Google’s published reference benchmark with clear limitations.

## Module 5: Dashboard and history

- Display recent requests.
- Add basic summary metrics.
- Add a meaningful Plotly emissions-reference-over-time chart.
- Add a confirmed action for clearing local history.

## Module 6: Validation

- Run pytest.
- Run Ruff.
- Test success, failure, missing metadata, and database persistence.
- Verify the app launches with `streamlit run app.py`.