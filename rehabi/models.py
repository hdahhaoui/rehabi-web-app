from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class GeneralData:
    building_type: str
    construction_year: int
    city: str
    climate_zone: Optional[str]
    habitable_area_m2: float
    floors: int
    ceiling_height_m: float
    country: str = "France"


@dataclass
class Geometry:
    wall_area_m2: float
    roof_area_m2: float
    floor_area_m2: float
    window_area_m2: float
    orientation: str
    volume_m3: Optional[float] = None


@dataclass
class EnvelopeElement:
    material: str
    thickness_m: float
    u_value_w_m2k: float


@dataclass
class Envelope:
    walls: EnvelopeElement
    roof: EnvelopeElement
    floor: EnvelopeElement
    windows: EnvelopeElement
    window_solar_factor_g: float = 0.55


@dataclass
class Ventilation:
    ventilation_type: str
    air_change_rate_ach: float
    airtightness_level: str


@dataclass
class HeatingSystem:
    system_type: str
    efficiency: float
    nominal_power_kw: float
    energy_carrier: str


@dataclass
class CoolingSystem:
    system_type: str
    cop_eer: float
    nominal_power_kw: float
    energy_carrier: str


@dataclass
class Systems:
    heating: HeatingSystem
    cooling: CoolingSystem
    dhw_energy_kwh_year: float


@dataclass
class Occupancy:
    occupants: int
    heating_setpoint_c: float
    cooling_setpoint_c: float
    occupied_hours_per_day: float


@dataclass
class Economics:
    energy_price_eur_kwh: Dict[str, float]
    co2_factor_kg_kwh: Dict[str, float]
    currency: str = "EUR"
    renovation_cost_eur: Dict[str, float] = field(default_factory=dict)
    subsidies_eur: Dict[str, float] = field(default_factory=dict)


@dataclass
class BuildingInput:
    general: GeneralData
    geometry: Geometry
    envelope: Envelope
    ventilation: Ventilation
    systems: Systems
    occupancy: Occupancy
    economics: Economics


@dataclass
class ThermalResults:
    h_trans_w_k: float
    h_vent_w_k: float
    h_total_w_k: float
    annual_heating_need_kwh: float
    annual_cooling_need_kwh: float
    annual_final_energy_kwh: float
    annual_cost_eur: float
    annual_co2_kg: float
    energy_class_estimate: str


@dataclass
class ScenarioResults:
    scenario_name: str
    baseline: ThermalResults
    renovated: ThermalResults
    annual_savings_kwh: float
    annual_savings_eur: float
    annual_co2_reduction_kg: float
    renovation_cost_eur: float
    subsidies_eur: float
    net_investment_eur: float
    payback_years: Optional[float]
    notes: List[str] = field(default_factory=list)
