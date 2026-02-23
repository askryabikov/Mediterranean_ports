# This script prepares Tableau-ready tables:
# 1. ports_enriched.csv: ports + synthetic port_time_h (10..100h)
# 2. pairs_scenarios.csv: for each ordered pair A->B and each scenario (Low/Medium/High),
#    compute total_cost_h = sea_time_h + alpha * to_port_time_h
#
# Notes:
# - Port time is a placeholder proxy (deterministic) until you replace it with real CPPI-based values.
# - This keeps the project moving while keeping the model transparent in README.

import hashlib
from typing import Dict

import pandas as pd


PORTS_IN = "data_out/ports_mediterranean.csv"
PAIRS_IN = "data_out/pairs.csv"

PORTS_OUT = "data_out/ports_enriched.csv"
PAIRS_SCEN_OUT = "data_out/pairs_scenarios.csv"

# Schedule pressure scenarios (do NOT call it alpha in the UI)
SCENARIOS = {
    "Low": 0.5,
    "Medium": 1.0,
    "High": 5.0,
}

# We want port time to be realistically "can be long" in Med: 10..100 hours
PORT_TIME_MIN_H = 10.0
PORT_TIME_MAX_H = 100.0


def stable_score_0_1(text: str) -> float:
    """
    Deterministic pseudo-random score in [0, 1) based on a stable hash.
    Used only as a placeholder until CPPI is integrated.
    """
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    # Take first 8 hex chars -> int -> normalize
    val = int(h[:8], 16)
    return (val % 10_000_000) / 10_000_000.0


def map_score_to_port_time_h(score_0_1: float) -> float:
    return PORT_TIME_MIN_H + score_0_1 * (PORT_TIME_MAX_H - PORT_TIME_MIN_H)


def main() -> None:
    ports = pd.read_csv(PORTS_IN)
    pairs = pd.read_csv(PAIRS_IN)

    # Build port_time_h placeholder (deterministic)
    # Later you will replace this column using CPPI data / manual overrides.
    ports["port_time_h"] = ports.apply(
        lambda r: map_score_to_port_time_h(stable_score_0_1(f"{r.port_id}|{r.port_name}")),
        axis=1
    )

    # Save enriched ports
    ports.to_csv(PORTS_OUT, index=False)
    print(f"Saved: {PORTS_OUT} rows={len(ports)}")

    # Attach to_port_time_h to each pair (cost is paid on arrival to 'to_id')
    port_time_map: Dict[str, float] = dict(zip(ports["port_id"], ports["port_time_h"]))
    pairs["to_port_time_h"] = pairs["to_id"].map(port_time_map)

    # Expand pairs by scenarios (long format for Tableau)
    out_rows = []
    for scenario, alpha in SCENARIOS.items():
        tmp = pairs.copy()
        tmp["scenario"] = scenario
        tmp["alpha"] = alpha
        tmp["total_cost_h"] = tmp["sea_time_h"] + tmp["alpha"] * tmp["to_port_time_h"]
        out_rows.append(tmp)

    pairs_scen = pd.concat(out_rows, ignore_index=True)

    # Rounding for Tableau display
    pairs_scen["distance_nm"] = pairs_scen["distance_nm"].round(2)
    pairs_scen["sea_time_h"] = pairs_scen["sea_time_h"].round(2)
    pairs_scen["to_port_time_h"] = pairs_scen["to_port_time_h"].round(2)
    pairs_scen["total_cost_h"] = pairs_scen["total_cost_h"].round(2)

    pairs_scen.to_csv(PAIRS_SCEN_OUT, index=False)
    print(f"Saved: {PAIRS_SCEN_OUT} rows={len(pairs_scen)}")
    print("Scenarios:", SCENARIOS)


if __name__ == "__main__":
    main()
