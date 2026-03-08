from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class WilayaCalibration:
    wilaya: str
    hdd18: float
    cdd26: float
    annual_horizontal_solar_kwh_m2: float
    heating_gains_utilization: float = 0.62
    cooling_gains_fraction: float = 0.58


# Engineering defaults for Algeria by wilaya (can be overridden per project).
# Values are intentionally conservative for rehabilitation pre-studies.
ALGERIA_WILAYA_CLIMATE: Dict[str, WilayaCalibration] = {
    "alger": WilayaCalibration("Alger", 1150, 360, 1850),
    "oran": WilayaCalibration("Oran", 1000, 420, 1900),
    "constantine": WilayaCalibration("Constantine", 1650, 320, 1780),
    "annaba": WilayaCalibration("Annaba", 1200, 320, 1760),
    "setif": WilayaCalibration("Setif", 1900, 300, 1750),
    "batna": WilayaCalibration("Batna", 2050, 350, 1800),
    "blida": WilayaCalibration("Blida", 1300, 360, 1820),
    "tlemcen": WilayaCalibration("Tlemcen", 1450, 330, 1780),
    "bejaia": WilayaCalibration("Bejaia", 1150, 300, 1780),
    "tiaret": WilayaCalibration("Tiaret", 1800, 360, 1840),
    "djelfa": WilayaCalibration("Djelfa", 2100, 430, 1900),
    "msila": WilayaCalibration("M'Sila", 1600, 560, 1980),
    "biskra": WilayaCalibration("Biskra", 850, 900, 2120),
    "ghardaia": WilayaCalibration("Ghardaia", 700, 1120, 2200),
    "laghouat": WilayaCalibration("Laghouat", 1200, 740, 2050),
    "bechar": WilayaCalibration("Bechar", 820, 980, 2200),
    "ouargla": WilayaCalibration("Ouargla", 500, 1320, 2250),
    "adrar": WilayaCalibration("Adrar", 420, 1420, 2320),
    "el oued": WilayaCalibration("El Oued", 650, 1180, 2200),
    "tamanrasset": WilayaCalibration("Tamanrasset", 620, 720, 2400),
    "tindouf": WilayaCalibration("Tindouf", 520, 1240, 2260),
}


ALGERIA_DEFAULT_ENERGY_PRICES_DZD_KWH: Dict[str, float] = {
    "electricity": 5.65,
    "gas": 0.384,
    "dhw": 0.384,
}


ALGERIA_DEFAULT_CO2_KG_KWH: Dict[str, float] = {
    "electricity": 0.50,
    "gas": 0.202,
    "dhw": 0.202,
}


def normalize_wilaya(name: str) -> str:
    return (
        name.strip()
        .lower()
        .replace("é", "e")
        .replace("è", "e")
        .replace("ê", "e")
        .replace("à", "a")
        .replace("ï", "i")
        .replace("'", "")
    )


def get_wilaya_calibration(wilaya: str) -> WilayaCalibration | None:
    key = normalize_wilaya(wilaya)
    return ALGERIA_WILAYA_CLIMATE.get(key)

