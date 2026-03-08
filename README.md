## Rehabi - Outil de rehabilitation energetique

Outil Python pour comparer des scenarios de renovation energetique avec un modele thermique coherent.

Sorties principales:

- Besoin de chauffage
- Besoin de climatisation
- Consommation annuelle estimee
- Cout energetique annuel
- Emissions CO2
- Economies apres renovation
- Temps de retour sur investissement

## Installation

```bash
pip install -r requirements.txt
```

## Lancement CLI

```bash
python main.py --input example_input_algeria.json --output outputs
```

Fichiers generes:

- `outputs/results.json`
- `outputs/report.md`
- `outputs/report.pdf` (si `reportlab` est installe)
- `outputs/report_audit_pro.pdf` (version audit pro structuree)

## Interface web pas-a-pas

```bash
python web_app.py
```

Puis ouvrir `http://127.0.0.1:5000`.

Workflow web:

1. Choisir type batiment, annee, wilaya, surface.
2. Lancer le pre-remplissage intelligent.
3. Ajuster les hypotheses techniques/economiques si besoin.
4. Simuler et comparer les 5 scenarios.
5. Recuperer les chemins des rapports Markdown/PDF dans `web_outputs/`.
6. Recuperer aussi `report_audit_pro.pdf` (page de garde, hypotheses, tableau comparatif, recommandations priorisees).

## Approche de calcul

- Transmission: `Q_trans = U * A * dT`
- Ventilation/infiltration: `Q_vent = 0.34 * n * V * dT`
- Coefficient global: `H = sum(U*A) + 0.34*n*V` en W/K
- Besoins annuels:
  - `Q_chauffage = H * DJU * 24 / 1000 - apports_utiles`
  - `Q_clim = H * DJR * 24 / 1000 + apports_penalisants`

Niveau 2 simplifie:

- Apports solaires (orientation + facteur solaire vitrage)
- Apports internes (occupation)

## Scenarios inclus

1. Isolation des murs
2. Isolation de la toiture
3. Remplacement des fenetres
4. Remplacement chauffage par PAC
5. Renovation globale combinee

## Calibration Algerie (wilaya/projet)

Le moteur inclut des valeurs par defaut calibrees pour l'Algerie:

- DJU18 / DJR26 par wilaya (jeu de valeurs d'ingenierie)
- Ensoleillement annuel
- Coefficients d'apports chauffage/clim adaptes au climat
- Prix energie par defaut en DZD/kWh
- Facteurs CO2 par defaut

Surcharges projet possibles dans le JSON d'entree:

- `economics.energy_price_eur_kwh`
- `economics.co2_factor_kg_kwh`
- `economics.renovation_cost_eur`
- `economics.subsidies_eur`
- `economics.currency`

Note compatibilite: les noms de champs suffixes `_eur` sont conserves pour compatibilite, mais la devise est pilotee par `economics.currency`.

Trace des hypotheses et sources:

- `CALIBRATION_ALGERIA.md`

## Score multicritere (audit pro)

Le classement des recommandations audit pro est base sur un score multicritere /100:

- Energie (gain kWh/an)
- Cout (economie annuelle)
- CO2 (reduction annuelle)
- Confort ete (reduction du besoin de climatisation)

Ponderations par defaut:

- Energie: 0.25
- Cout: 0.35
- CO2: 0.25
- Confort ete: 0.15

Personnalisation possible dans l'entree JSON:

```json
"multicriteria_weights": {
  "energy": 0.25,
  "cost": 0.35,
  "co2": 0.25,
  "summer_comfort": 0.15
}
```

Dans l'interface web, ces pondérations sont aussi modifiables avant simulation.
