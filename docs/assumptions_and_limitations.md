# Assumptions and Limitations

CarbonLens can measure application-side request latency and record metadata returned by the Gemini API.

CarbonLens cannot directly observe the infrastructure behind an individual hosted Gemini request, including:

- Accelerator type and count
- Hardware utilisation
- Request batching
- Model routing
- Cache behaviour
- Data-centre PUE
- Serving location
- Electricity-grid carbon intensity

Therefore, the published 0.24 Wh and 0.03 g CO₂e figures are not measurements of a specific API request.

Actual environmental impact may differ from the published benchmark.

The initial scope covers inference-related environmental context only. It excludes:

- Model training emissions
- Hardware manufacturing
- Network transfer
- User-device energy consumption
- Full life-cycle assessment