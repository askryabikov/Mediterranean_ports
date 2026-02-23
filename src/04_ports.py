# This script:
# 1. Loads the generated route geometry (pair_points) and enriched ports data
# 2. Extracts origin and destination port IDs from the composite pair_id
# 3. Maps human-readable port labels to the points and exports the final enriched dataset

from pathlib import Path
import pandas as pd

# --- Config ---
# Resolve paths relative to the script location
# Navigate up two levels to the project root directory
BASE_DIR = Path(__file__).resolve().parents[1]   # .../Project1_Mediterranean_ports
DATA_DIR = BASE_DIR / "data_out"

# Define input and output file paths
pair_points_path = DATA_DIR / "pair_points.csv"
ports_enriched_path = DATA_DIR / "ports_enriched.csv"
out_path = DATA_DIR / "pair_points_enriched.csv"

def main() -> None:
    print(f"Loading geometry points from: {pair_points_path}")
    
    # Load the datasets
    pp = pd.read_csv(pair_points_path)
    ports = pd.read_csv(ports_enriched_path)

    # Extract 'from_id' and 'to_id' by splitting the 'pair_id' string
    # Example: 'P01__P02' -> 'P01' and 'P02'
    pp["from_id"] = pp["pair_id"].str.split("__").str[0]
    pp["to_id"]   = pp["pair_id"].str.split("__").str[1]

    # Create a dictionary to map port IDs to their readable labels
    # Example: {'P01': 'Odesa', 'P02': 'Istanbul'}
    port_map = ports.set_index("port_id")["port_label"].to_dict()
    
    # Apply the mapping to add readable labels for origin and destination ports
    # This enrichment is crucial for creating readable tooltips in Tableau
    pp["from_port_label"] = pp["from_id"].map(port_map)
    pp["to_port_label"]   = pp["to_id"].map(port_map)

    # Export the enriched geometry dataset
    # Using utf-8-sig encoding ensures special characters display correctly in Excel and Tableau
    pp.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"Done! Enriched geometry saved to: {out_path}")

if __name__ == "__main__":
    main()