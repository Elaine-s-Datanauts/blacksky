# fetch_ucs.py

import pandas as pd
import requests
from io import BytesIO

def main():
    # Download the Excel file from UCS
    url = "https://www.ucs.org/media/11492"
    response = requests.get(url)
    response.raise_for_status()

    # Read Excel directly from memory
    ucs = pd.read_excel(BytesIO(response.content), sheet_name="Sheet1")

    # --- Clean launch date ---
    ucs["Date of Launch"] = (
        ucs["Date of Launch"]
        .astype(str)
        .str.strip()
        .str.replace(r"//+", "/", regex=True)
    )
    ucs["Date of Launch"] = pd.to_datetime(ucs["Date of Launch"], errors="coerce")
    ucs = ucs.dropna(subset=["Date of Launch"]).reset_index(drop=True)

    # --- Normalize NORAD Number ---
    ucs["NORAD Number"] = (
        ucs["NORAD Number"]
        .astype(str)
        .str.strip()
        .str.replace(r"[^\d]", "", regex=True)
    )
    ucs["NORAD Number"] = pd.to_numeric(ucs["NORAD Number"], errors="coerce").astype("Int64")

    # --- Sort and dedupe ---
    ucs_sorted = ucs.sort_values(["NORAD Number", "Date of Launch"])
    ucs_latest = (
        ucs_sorted
        .drop_duplicates(subset=["NORAD Number"], keep="last")
        .reset_index(drop=True)
    )

    # --- Print shapes only ---
    print("Original shape:", ucs.shape)
    print("After dedupe shape:", ucs_latest.shape)

    # --- Rename for consistency ---
    ucs_latest = ucs_latest.rename(
        columns={"Name of Satellite, Alternate Names": "Name of Satellite"}
    )

    # --- Save cleaned file ---
    ucs_latest.to_csv("../data/out/ucs.csv", index=False)


if __name__ == "__main__":
    main()