from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict

from rehabi.models import BuildingInput, EnvelopeElement, HeatingSystem


def _insulate_walls(building: BuildingInput) -> BuildingInput:
    envelope = replace(
        building.envelope,
        walls=EnvelopeElement(
            material="Mur isole",
            thickness_m=max(building.envelope.walls.thickness_m, 0.3),
            u_value_w_m2k=min(building.envelope.walls.u_value_w_m2k, 0.3),
        ),
    )
    return replace(building, envelope=envelope)


def _insulate_roof(building: BuildingInput) -> BuildingInput:
    envelope = replace(
        building.envelope,
        roof=EnvelopeElement(
            material="Toiture isolee",
            thickness_m=max(building.envelope.roof.thickness_m, 0.35),
            u_value_w_m2k=min(building.envelope.roof.u_value_w_m2k, 0.2),
        ),
    )
    return replace(building, envelope=envelope)


def _replace_windows(building: BuildingInput) -> BuildingInput:
    envelope = replace(
        building.envelope,
        windows=EnvelopeElement(
            material="Double/Triple vitrage performant",
            thickness_m=max(building.envelope.windows.thickness_m, 0.024),
            u_value_w_m2k=min(building.envelope.windows.u_value_w_m2k, 1.3),
        ),
        window_solar_factor_g=min(building.envelope.window_solar_factor_g, 0.5),
    )
    ventilation = replace(building.ventilation, air_change_rate_ach=max(0.25, building.ventilation.air_change_rate_ach * 0.85))
    return replace(building, envelope=envelope, ventilation=ventilation)


def _heat_pump(building: BuildingInput) -> BuildingInput:
    heating = replace(
        building.systems.heating,
        system_type="Pompe a chaleur air/eau",
        efficiency=max(building.systems.heating.efficiency, 3.2),
        nominal_power_kw=building.systems.heating.nominal_power_kw,
        energy_carrier="electricity",
    )
    systems = replace(building.systems, heating=heating)
    return replace(building, systems=systems)


def _global_combined(building: BuildingInput) -> BuildingInput:
    b = _insulate_walls(building)
    b = _insulate_roof(b)
    b = _replace_windows(b)
    b = _heat_pump(b)
    ventilation = replace(b.ventilation, air_change_rate_ach=max(0.2, b.ventilation.air_change_rate_ach * 0.85))
    return replace(b, ventilation=ventilation)


SCENARIO_FUNCTIONS: Dict[str, Callable[[BuildingInput], BuildingInput]] = {
    "Isolation des murs": _insulate_walls,
    "isolation_toiture": _insulate_roof,
    "remplacement_fenetres": _replace_windows,
    "pac_chauffage": _heat_pump,
    "renovation_globale": _global_combined,
}

