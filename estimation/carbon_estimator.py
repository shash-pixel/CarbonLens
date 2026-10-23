"""Carbon conversion for future compatible energy and intensity inputs."""


def carbon_gco2e(
    energy_wh: float,
    carbon_intensity_gco2e_per_kwh: float,
) -> float:
    """Convert energy in Wh and carbon intensity in gCO2e/kWh to gCO2e.

    This function is only appropriate when the energy estimate and the
    carbon-intensity factor have compatible system boundaries.
    """
    if energy_wh < 0:
        raise ValueError("Energy must be non-negative.")

    if carbon_intensity_gco2e_per_kwh < 0:
        raise ValueError("Carbon intensity must be non-negative.")

    return energy_wh / 1000 * carbon_intensity_gco2e_per_kwh