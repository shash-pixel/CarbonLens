from estimation.methodology import GOOGLE_GEMINI_APPS_REFERENCE


def test_google_reference_uses_published_benchmark_values() -> None:
    reference = GOOGLE_GEMINI_APPS_REFERENCE

    assert reference.energy_wh == 0.24
    assert reference.carbon_gco2e == 0.03


def test_google_reference_explains_its_limitation() -> None:
    reference = GOOGLE_GEMINI_APPS_REFERENCE

    assert "not direct measurements" in reference.explanation
    assert "token count" in reference.explanation