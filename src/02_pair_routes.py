# This script:
# 1. Reads the enriched ports dataset with corrected coordinates
# 2. Generates all possible ordered pairs of ports (A -> B)
# 3. Calculates the shortest sea route and distance for each pair using the searoute library
# 4. Exports the route summaries (pairs) and the detailed route geometry (points) into CSV files

# FIXED VERSION: Uses absolute paths to locate 'data_out' correctly
import itertools
from typing import Dict, Tuple, List
import pandas as pd
import searoute as sr
from pathlib import Path  # Added library for robust file path handling

# Config
# Define paths relative to the location of THIS script.
# The script is located in /src/, so we need to move one level up to the project root.
BASE_DIR = Path(__file__).resolve().parent.parent 
DATA_DIR = BASE_DIR / "data_out"

# Now Python will reliably find the files using the absolute path
PORTS_CSV = DATA_DIR / "ports_enriched.csv"
OUT_PAIRS_CSV = DATA_DIR / "pairs.csv"
OUT_POINTS_CSV = DATA_DIR / "pair_points.csv"

SPEED_KNOTS = 14.0

def nm_to_hours(distance_nm: float, speed_knots: float) -> float:
    """Calculates transit time in hours given distance in nautical miles and speed in knots."""
    return distance_nm / speed_knots

def main() -> None:
    print(f"Reading ports from: {PORTS_CSV}")
    
    # Check if the file exists to provide a clear error message
    if not PORTS_CSV.exists():
        print(f"ERROR: File not found at {PORTS_CSV}")
        print("Please check if 'ports_enriched.csv' is inside the 'data_out' folder.")
        return

    ports = pd.read_csv(PORTS_CSV)

    # Build lookup dictionary: port_id -> (lon, lat)
    # Using coordinates from the corrected enriched file (including Izmir and Limassol adjustments)
    pos: Dict[str, Tuple[float, float]] = {
        row.port_id: (float(row.lon), float(row.lat))
        for row in ports.itertuples(index=False)
    }

    port_ids: List[str] = ports["port_id"].tolist()

    pair_rows = []
    point_rows = []

    print(f"Generating routes for {len(port_ids)} ports...")

    # Create ordered pairs: A->B and B->A are treated as separate routes
    for a, b in itertools.permutations(port_ids, 2):
        a_lon, a_lat = pos[a]
        b_lon, b_lat = pos[b]

        # Calculate the sea route using the searoute library
        try:
            route = sr.searoute((a_lon, a_lat), (b_lon, b_lat), units="naut")
        except Exception as e:
            print(f"Warning: Could not route {a}->{b}. Using direct line. Error: {e}")
            # Fallback to a direct line (distance 0 placeholder) if searoute fails
            distance_nm = 0.0 
            coords = [[a_lon, a_lat], [b_lon, b_lat]]
        else:
            # Extract the calculated distance and geometry
            distance_nm = float(route["properties"]["length"])
            coords = route["geometry"]["coordinates"]

        # Calculate transit time based on distance and base speed
        sea_time_h = nm_to_hours(distance_nm, SPEED_KNOTS)
        pair_id = f"{a}__{b}"

        # Append the summary data for the route pair
        pair_rows.append({
            "pair_id": pair_id,
            "from_id": a,
            "to_id": b,
            "distance_nm": distance_nm,
            "sea_time_h": sea_time_h,
        })

        # Append the geographic points forming the route line for visualization
        for seq, (lon, lat) in enumerate(coords):
            point_rows.append({
                "pair_id": pair_id,
                "seq": seq,
                "lon": lon,
                "lat": lat
            })

    # Export the final datasets to CSV
    pd.DataFrame(pair_rows).to_csv(OUT_PAIRS_CSV, index=False)
    pd.DataFrame(point_rows).to_csv(OUT_POINTS_CSV, index=False)
    print(f"Done! Saved route geometry to {OUT_POINTS_CSV}")

if __name__ == "__main__":
    main()