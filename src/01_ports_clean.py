# This script:
# 1. Reads a ports dataset from Natural Earth (Shapefile)
# 2. Filters ports to the Mediterranean bounding box
# 3. Exports a clean CSV for the rest of the pipeline

import pandas as pd
import geopandas as gpd

# Mediterranean bounding box
MIN_LON, MAX_LON = -6.5, 36.5
MIN_LAT, MAX_LAT = 30.0, 46.5
TARGET_N = 40
SEED = 42

# Path to the Natural Earth ports shapefile
# After unzipping, you should point this to the .shp file inside the folder.
INPUT_SHP = "data_raw/ports/ne_10m_ports.shp"

# Clean CSV
OUTPUT_CSV = "data_out/ports_mediterranean.csv"

def main() -> None:
    # Read shapefile as GeoDataFrame
    gdf = gpd.read_file(INPUT_SHP)

    # Ensure we have geographic coordinates (WGS84)
    # Natural Earth is typically already EPSG:4326, but we enforce it anyway
    gdf = gdf.to_crs(epsg=4326)

    # Extract lon/lat from geometry (points)
    gdf["lon"] = gdf.geometry.x
    gdf["lat"] = gdf.geometry.y

    # Filter by bounding box (Mediterranean area)
    gdf_med = gdf[
        (gdf["lon"] >= MIN_LON) & (gdf["lon"] <= MAX_LON) &
        (gdf["lat"] >= MIN_LAT) & (gdf["lat"] <= MAX_LAT)
    ].copy()

    # Keep only the fields we need (field names may differ; we will adjust after you unzip)
    # Common Natural Earth fields include: name, scalerank, etc.
    # We'll create our own stable IDs.
    gdf_med = gdf_med.reset_index(drop=True)
    gdf_med["port_id"] = gdf_med.index.map(lambda i: f"P{i+1:02d}")

    # Try to pick a human-readable name column (may be 'name' or similar)
    name_col = "name" if "name" in gdf_med.columns else None
    if name_col is None:
        # Fallback: create a placeholder name if dataset has different schema
        gdf_med["port_name"] = gdf_med["port_id"]
    else:
        gdf_med["port_name"] = gdf_med[name_col].astype(str)

    # Select final columns
    out = gdf_med[["port_id", "port_name", "lat", "lon"]].copy()

    # If there are too many ports in the bbox, sample a fixed-size set for a clean demo
    if len(out) > TARGET_N:
        out = out.sample(n=TARGET_N, random_state=SEED).reset_index(drop=True)

    # Rebuild stable IDs after sampling (so they are P01..P40)
    out["port_id"] = [f"P{i+1:02d}" for i in range(len(out))]

    # Export
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(out)} ports to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
