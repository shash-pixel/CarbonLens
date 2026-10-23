import pytest

from estimation.carbon_estimator import carbon_gco2e


def test_carbon_conversion_converts_wh_to_kwh() -> None:
    result = carbon_gco2e(
        energy_wh=250,
        carbon_intensity_gco2e_per_kwh=400,
    )

    assert result == 100


@pytest.mark.parametrize(
    ("energy_wh", "carbon_intensity"),
    [
        (-1, 400),
        (1, -400),
    ],
)
def test_carbon_conversion_rejects_negative_inputs(
    energy_wh: float,
    carbon_intensity: float,
) -> None:
    with pytest.raises(ValueError):
        carbon_gco2e(energy_wh, carbon_intensity)