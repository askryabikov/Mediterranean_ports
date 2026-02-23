# Interactive Port Network (Mediterranean)
**Shortest-route cost on a synthetic shipping graph using Dijkstra + Tableau visualization**

This is a small DS&A pet project built after completing the **Basic Algorithms & Data Structures** module (Python) at Neoversity. 
Goal: model container shipping routing trade-offs in the Mediterranean using **sea-time** + **port-time** and visualize two alternative 5-port rotations in **Tableau**.

> NDA note: no real vessel/company/route data. Ports are public (Natural Earth). Port time is a transparent proxy (placeholder) inspired by port efficiency concepts (planned: CPPI-based mapping).

---

## 🔗 Project Links

* 📊 **[Interactive Tableau Dashboard](https://public.tableau.com/app/profile/oleksandr.skriabikov/viz/Skriabikov-Mediterranean_ports/Dashboard)** — Explore route sensitivity and cost modeling.
* 🤝 **[Connect with me on LinkedIn](https://www.linkedin.com/in/askryabikov)** — For collaboration in maritime AI and logistics optimization.

---

## What this project shows

* **Graph modeling** (ports as nodes, sea legs as directed edges)

* **Cost function design** for routing:
  * Sea time is derived from nautical distance / speed
  * Port time is an arrival penalty (proxy)

* **Scenario & Sensitivity analysis**
  * Schedule pressure scenarios: `Low / Medium / High`
  * Dynamic calculation of fuel costs and speed adjustments

* **Tableau dashboard**
  * Ports on an interactive map with sequential numbering
  * Two alternative 5-port rotations (A vs B)
  * Dynamic Stacked Bars: Sea hours vs Port hours
  * Tornado Charts: Sensitivity analysis for fuel price and speed changes


---

## Data sources

* **Ports (geometry + names):** Natural Earth "Ports" shapefile  
  (Public domain; used only for coordinates and labels)

* **Sea routes / distances (no land crossings):** computed in Python with `searoute`  
  (Generates sea polylines + nautical miles for visualization)

Planned improvement:

* Replace synthetic `port_time_hours` with a CPPI-based mapping and/or per-port overrides.

---

## Project structure


```text
Project1_Mediterranean_ports/
  data_raw/
    ports/                       # Файли Natural Earth (.shp, .dbf, .shx)
  data_out/
    ports_mediterranean.csv      # 40 портів (lat/lon)
    ports_enriched.csv           # порти + port_time_h (proxy)
    pairs.csv                    # всі пари A->B (distance_nm, sea_time_h)
    pair_points.csv              # точки поліліній для кожної пари A->B
    pairs_scenarios.csv          # сценарії Low/Medium/High
    pair_points_enriched.csv     # фінальні точки з назвами портів для Tableau
  src/
    01_ports_clean.py            # фільтрація портів (Середземне море)
    02_pair_routes.py            # розрахунок морських маршрутів (A->B)
    03_rotation_export.py        # додавання сценаріїв та port_time_h
    04_ports.py                  # збагачення геометрії назвами портів
  requirements.txt
  README.md
```

---

## How to run (Python)

### 1. Install dependencies

Make sure you use the same Python interpreter for install and run.


```bash
# Встановлення необхідних бібліотек
python -m pip install -r requirements.txt
```

Example `requirements.txt`:

```txt
pandas
geopandas
pyproj
shapely
searoute
numpy
```


### 2. Build the datasets

From the project root:

```bash
# Запуск скриптів по черзі для генерації даних
python src/01_ports_clean.py
python src/02_pair_routes.py
python src/03_rotation_export.py
python src/04_ports.py
```

Outputs will be written to `data_out/`.

---

## Tableau dashboard (high level)

Tableau uses the exported CSVs to build a full interactive simulator:

* `ports_enriched.csv` → port points + port_time_h
* `pair_points_enriched.csv` → sea polylines (Line marks) with valid tooltips
* `pairs_scenarios.csv` → core metrics under each scenario


Dashboard UI concept:

* Parameter Controls: Scenario (Low/Medium/High), Speed Change, Fuel Price Change
* Route Selectors: Rotation A (5 ports) vs Rotation B (5 ports)
* Output 1: Map with numbered ports and two balanced route overlays
* Output 2: Delta Summary block (Time, Distance, Cost differences)
* Output 3: Stacked Bar Charts (Sea Time vs Port Time ratio)
* Output 4: Tornado Charts (Financial sensitivity analysis)

---

## Notes / assumptions

* Vessel speed and fuel prices are adjustable via Tableau parameters to calculate dynamic deltas.
* Port time is currently a deterministic proxy in the range ~10–100 hours.  
* This is a teaching/demo model, not an operational routing engine.
  
---

## Next improvements (optional)

* CPPI integration (container port performance proxy → port_time_h)
* k-nearest neighbor edges (sparser graph) + Dijkstra for "network routing"
* Live data integration (congestion / berth availability) via a backend service
* Comparing alternative routes using a simple additive cost:
`total_cost_hours = sea_time_hours + α * port_time_hours`
Where:
  a. `sea_time_hours` = `distance_nm / (vessel_speed_knots + speed_change_knots)`
  b. `port_time_hours` = expected time spent in port on arrival (proxy; placeholder)
  c. `α` is not shown as "alpha" in the UI. Instead we expose **Schedule pressure**:
      * `Low`  → α = 0.5  
      * `Medium` → α = 1.0  
      * `High` → α = 5.0  
Interpretation:
- Low: port delays matter, but sea-time dominates
- Medium: 1 hour in port ≈ 1 hour at sea
- High: port delays dominate; willing to detour at sea to avoid slow ports

---

## License

Code: MIT  
Data: Natural Earth is public domain.
