from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE
from integrations.base import ProviderResult
from tracking.usage_tracker import build_failed_record, build_success_record


def test_success_record_keeps_reference_values_unscaled() -> None:
    provider_result = ProviderResult(
        provider="google",
        model="gemini-2.5-flash",
        response_text="A Gemini response",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
    )

    record = build_success_record(
        provider_result=provider_result,
        latency_ms=123.4,
    )

    assert record.status == "success"
    assert record.reference_energy_wh == GOOGLE_GEMINI_APPS_REFERENCE.energy_wh
    assert (
        record.reference_carbon_gco2e
        == GOOGLE_GEMINI_APPS_REFERENCE.carbon_gco2e
    )
    assert record.total_tokens == 150
    assert record.latency_ms == 123.4


def test_failed_record_has_no_reference_values() -> None:
    record = build_failed_record(
        provider="google",
        model="gemini-2.5-flash",
        error_category="timeout",
        error_message="Gemini request timed out.",
    )

    assert record.status == "failed"
    assert record.reference_energy_wh is None
    assert record.reference_carbon_gco2e is None
    assert record.estimation_method == "unavailable"