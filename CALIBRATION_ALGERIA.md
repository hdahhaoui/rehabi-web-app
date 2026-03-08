## Calibration Algeria - Hypotheses (Mars 2026)

Ce document trace les hypotheses de calibration integrees dans l'outil.

## 1) Prix energie (DZD/kWh)

Valeurs par defaut utilisees:

- Electricite (residentiel): `5.65`
- Gaz naturel (residentiel): `0.384`

Source de reference (dernieres valeurs disponibles dans la source):

- GlobalPetrolPrices, Algerie electricite menages (donnees juin 2025): https://www.globalpetrolprices.com/Algeria/electricity_prices/
- GlobalPetrolPrices, Algerie gaz naturel menages (donnees juin 2025): https://www.globalpetrolprices.com/Algeria/natural_gas_prices/

## 2) Facteurs CO2 (kgCO2/kWh)

Valeurs par defaut utilisees:

- Electricite: `0.50`
- Gaz naturel: `0.202`

Justification:

- Electricite: valeur d'ingenierie conservative, coherente avec un mix electrique tres majoritairement fossile en Algerie.
- Gaz: facteur de combustion standard du gaz naturel (~56.1 kgCO2/GJ), soit environ 0.202 kgCO2/kWh PCI.

References de contexte:

- Our World in Data (dataset Ember/Energy Institute) - carbon intensity of electricity generation: https://archive.ourworldindata.org/20250624-125417/grapher/carbon-intensity-electricity.html
- GlobalPetrolPrices (mix electrique indique comme fortement fossile): https://www.globalpetrolprices.com/Algeria/electricity_prices/

## 3) Climat par wilaya (DJU18, DJR26, solaire)

Le modele inclut un jeu de valeurs d'ingenierie par wilaya (fichier `rehabi/calibration_dz.py`), utile pour les etudes de prefaisabilite.

Important:

- Les DJU/DJR par wilaya sont des valeurs de calibration pragmatiques, pas une base meteorologique officielle unique.
- Pour un projet d'execution, remplacez ces valeurs par vos donnees locales (station meteo, EPW, normes internes, historique exploitation).

## 4) Surcharge projet recommandee

Les hypotheses peuvent etre surchargees dans l'entree JSON:

- `economics.energy_price_eur_kwh`
- `economics.co2_factor_kg_kwh`
- `general.city` (wilaya)
- et, si necessaire, vos DJU/DJR via extension du mapping dans `rehabi/calibration_dz.py`.
