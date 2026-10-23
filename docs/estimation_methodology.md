# CarbonLens Estimation Methodology

## Purpose

CarbonLens provides environmental context for LLM inference. It does not directly measure the electricity consumed by an individual Gemini API request.

## Initial reference benchmark

CarbonLens uses Google's published benchmark for a median Gemini Apps text-generation prompt from its May 2025 analysis:

- Published energy reference: **0.24 Wh**
- Published emissions reference: **0.03 g CO₂e**

These values are reference benchmarks, not direct measurements of an individual Gemini API request.

## How CarbonLens will use this benchmark

For each successful Gemini request, CarbonLens will display the published values as environmental reference context.

CarbonLens will also record:

- Provider-reported input, output, and total token counts when available
- Application-measured request latency
- The Gemini model identifier
- The published benchmark source and explanation

CarbonLens will not multiply 0.24 Wh or 0.03 g CO₂e by token count, latency, or number of words.

## Why token counts are not enough

Token counts describe the size of the workload, but they do not reveal the actual infrastructure used to serve a request. For a hosted Gemini API request, CarbonLens cannot observe:

- Accelerator type and number of accelerators
- Hardware utilisation
- Request batching
- Model routing
- Data-centre overhead
- Serving location
- Electricity-grid carbon intensity

Therefore, token counts and latency cannot be converted into reliable request-specific energy values without an applicable, documented methodology.

## Carbon conversion for future compatible estimates

If CarbonLens later has both:

1. A defensible energy estimate in Wh, and
2. A compatible carbon-intensity factor in g CO₂e/kWh,

it may calculate:

`CO₂e (g) = Energy (Wh) / 1000 × Carbon intensity (g CO₂e/kWh)`

The carbon-intensity factor must identify its source, geographic coverage, time period, units, and emissions boundary.

## Scope and limitations

CarbonLens initially focuses on inference-related environmental context only.

The initial scope excludes:

- Model training emissions
- Hardware manufacturing emissions
- Network and end-user device emissions
- Direct measurement of Gemini provider infrastructure

## Sources

- Google research paper: https://arxiv.org/abs/2508.15734
- Google Cloud methodology overview: https://cloud.google.com/blog/products/infrastructure/measuring-the-environmental-impact-of-ai-inference
- Gemini API documentation: https://ai.google.dev/api/generate-content.md