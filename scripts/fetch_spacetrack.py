# fetch_spacetrack_gp_history.py

from datetime import datetime, timedelta, timezone
from pathlib import Path
import os, time
import pandas as pd
from spacetrack import SpaceTrackClient
import spacetrack.operators as op
from dotenv import load_dotenv

# ---- Config -----------------------------------------------------
DAYS_BACK = 180
OUT_PATH = Path("../data/in/tle_gp_history_180days_20250906.csv")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_RETRIES = 3

# ---- Auth -------------------------------------------------------
load_dotenv()
USER = os.getenv("SPACETRACK_USERNAME")
PWD  = os.getenv("SPACETRACK_PASSWORD")
if not USER or not PWD:
    raise SystemExit("Missing SPACETRACK_USERNAME or SPACETRACK_PASSWORD in .env")

st = SpaceTrackClient(identity=USER, password=PWD)

# ---- Time window ------------------------------------------------
end_dt = datetime.now(timezone.utc)
start_dt = end_dt - timedelta(days=DAYS_BACK)

# ---- Bulk pull (gp_history with date-only epoch, fallback to tle) ----------
print("[1/2] Fetching elements in daily chunks…")

rows_raw = []
MAX_RETRIES = 2  # also falls back to 'tle', so 2 is enough here

def try_gp_history(day_start_str, day_end_str):
    # Date-only range; gp_history is picky about timestamp formats.
    kwargs = {
        "epoch": f">{day_start_str},<{day_end_str}",  # open interval
        "orderby": "EPOCH asc",
    }
    return st.gp_history(**kwargs)

def try_tle(day_start_str, day_end_str):
    # Bulk TLE pull for the same day; faster than per-sat looping.
    kwargs = {
        "epoch": f">{day_start_str},<{day_end_str}",
        "orderby": "EPOCH asc",
    }
    return st.tle(**kwargs)

def fetch_day_any(day_start, day_end):
    day_start_str = day_start.strftime("%Y-%m-%d")
    day_end_str   = day_end.strftime("%Y-%m-%d")

    # 1) Try gp_history
    for attempt in range(1, MAX_RETRIES+1):
        try:
            data = try_gp_history(day_start_str, day_end_str)
            # Space-Track sometimes returns an error dict instead of raising
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError(data["error"])
            return data, "gp_history"
        except Exception as e:
            wait = 2 * attempt
            print(f"  WARN(gp_history {day_start_str}): {e} → retry in {wait}s")
            time.sleep(wait)

    # 2) Fallback: tle
    for attempt in range(1, MAX_RETRIES+1):
        try:
            data = try_tle(day_start_str, day_end_str)
            if isinstance(data, dict) and data.get("error"):
                raise RuntimeError(data["error"])
            return data, "tle"
        except Exception as e:
            wait = 2 * attempt
            print(f"  WARN(tle {day_start_str}): {e} → retry in {wait}s")
            time.sleep(wait)

    return [], "none"

cursor = start_dt
pull_count = 0
while cursor < end_dt:
    day_start = cursor
    day_end = min(cursor + timedelta(days=1), end_dt)
    data, source = fetch_day_any(day_start, day_end)

    # Guard against error rows embedded in arrays
    valid = []
    for rec in data or []:
        if isinstance(rec, dict) and "error" in rec:
            print(f"  ERROR payload on {day_start.date()}: {rec['error']}")
        else:
            valid.append(rec)

    rows_raw.extend(valid)
    pull_count += len(valid)
    print(f"  …{day_start.date()} [{source}] → +{len(valid)} rows (total {pull_count})")
    cursor = day_end

if not rows_raw:
    raise SystemExit("No rows returned in the selected window (both gp_history and tle failed).")

# ---- Normalize (case-insensitive + broad aliases) -------------------------
df_raw = pd.DataFrame(rows_raw)
print("Raw columns:", sorted(df_raw.columns.tolist()))
print("Sample row:", df_raw.iloc[0].to_dict() if len(df_raw) else {})

def up(d): return { (k.upper() if isinstance(k,str) else k): v for k,v in d.items() }
rows_uc = [up(r) for r in rows_raw]

ALIASES = {
    "NORAD_CAT_ID": ["NORAD_CAT_ID","SATNO","CATNR","NORAD","NORAD_ID","NORADCATID"],
    "EPOCH":        ["EPOCH","EPOCHUTC","TLE_EPOCH","GP_EPOCH","EPOCHDT","EPOCH_DATE","EPOCHTIME"],
    "MEAN_MOTION":  ["MEAN_MOTION","N","MEANMO"],
    "ECCENTRICITY": ["ECCENTRICITY","ECC"],
    "INCLINATION":  ["INCLINATION","INCL"],
    "RA_OF_ASC_NODE":["RA_OF_ASC_NODE","RAAN","NODE_RAAN","NODE"],
    "ARG_OF_PERICENTER":["ARG_OF_PERICENTER","ARG_OF_PERIGEE","ARGP","AOP"],
    "BSTAR":        ["BSTAR","BSTAR_DRAG","BSTAR_DRAG_TERM"],
}

ALIASES.update({
    "OBJECT_TYPE": ["OBJECT_TYPE", "OBJTYPE", "TYPE"],
    "OBJECT_NAME": ["OBJECT_NAME", "SATNAME", "NAME"],      # optional but handy
    "OBJECT_ID":   ["OBJECT_ID", "INTLDES", "INTL_DESIGNATOR", "INTLDESIGNATOR"],  # optional
})

def pick(d, names):
    for n in names:
        if n in d and d[n] not in (None, ""):
            return d[n]
    return None

norm = []
for d in rows_uc:
    norm.append({
        "NORAD_CAT_ID":   pick(d, ALIASES["NORAD_CAT_ID"]),
        "EPOCH":          pick(d, ALIASES["EPOCH"]),
        "MEAN_MOTION":    pick(d, ALIASES["MEAN_MOTION"]),
        "ECCENTRICITY":   pick(d, ALIASES["ECCENTRICITY"]),
        "INCLINATION":    pick(d, ALIASES["INCLINATION"]),
        "RA_OF_ASC_NODE": pick(d, ALIASES["RA_OF_ASC_NODE"]),
        "ARG_OF_PERICENTER": pick(d, ALIASES["ARG_OF_PERICENTER"]),
        "BSTAR":          pick(d, ALIASES["BSTAR"]),
        "OBJECT_TYPE":       pick(d, ALIASES["OBJECT_TYPE"]),     # <-- new
        "OBJECT_NAME":       pick(d, ALIASES["OBJECT_NAME"]),     # optional
        "OBJECT_ID":         pick(d, ALIASES["OBJECT_ID"]),       # optional
    })
df = pd.DataFrame(norm)

# Coerce & basic checks
df["NORAD_CAT_ID"] = pd.to_numeric(df["NORAD_CAT_ID"], errors="coerce")
df["EPOCH"]        = pd.to_datetime(df["EPOCH"], utc=True, errors="coerce")

print(f"[debug] missing NORAD_CAT_ID: {df['NORAD_CAT_ID'].isna().sum()} / {len(df)}")
print(f"[debug] missing EPOCH: {df['EPOCH'].isna().sum()} / {len(df)}")

df = df.dropna(subset=["NORAD_CAT_ID","EPOCH"]).copy()
df["NORAD_CAT_ID"] = df["NORAD_CAT_ID"].astype("int64")

# --- Enrich OBJECT_TYPE from SATCAT for any missing values ------------------
missing_mask = df["OBJECT_TYPE"].isna() | (df["OBJECT_TYPE"] == "")
if missing_mask.any():
    need_ids = sorted(df.loc[missing_mask, "NORAD_CAT_ID"].unique().tolist())

    # Space-Track prefers batched IN() queries; keep batches modest to avoid URL limits
    def fetch_satcat_types(norad_ids, batch=500):
        out = []
        for i in range(0, len(norad_ids), batch):
            chunk = norad_ids[i:i+batch]
            # satcat fields: NORAD_CAT_ID, OBJECT_TYPE, OBJECT_NAME, OBJECT_ID, etc.
            sat = st.satcat(norad_cat_id=op.in_(chunk), fields=[
                "NORAD_CAT_ID","OBJECT_TYPE","OBJECT_NAME","OBJECT_ID"
            ])
            if isinstance(sat, dict) and sat.get("error"):
                raise RuntimeError(sat["error"])
            out.extend(sat or [])
        return pd.DataFrame(out)

    satcat_df = fetch_satcat_types(need_ids)
    if not satcat_df.empty:
        # normalize columns just in case
        satcat_df.columns = [c.upper() for c in satcat_df.columns]
        satcat_df["NORAD_CAT_ID"] = pd.to_numeric(satcat_df["NORAD_CAT_ID"], errors="coerce")
        satcat_df = satcat_df.dropna(subset=["NORAD_CAT_ID"]).copy()
        satcat_df["NORAD_CAT_ID"] = satcat_df["NORAD_CAT_ID"].astype("int64")

        # keep only the columns we need for merge
        sat_types = satcat_df[["NORAD_CAT_ID","OBJECT_TYPE"]].drop_duplicates()

        # left-merge to fill missing OBJECT_TYPE
        df = df.merge(sat_types, on="NORAD_CAT_ID", how="left", suffixes=("", "_SATCAT"))
        df["OBJECT_TYPE"] = df["OBJECT_TYPE"].where(df["OBJECT_TYPE"].notna() & (df["OBJECT_TYPE"]!=""),
                                                    df["OBJECT_TYPE_SATCAT"])
        df = df.drop(columns=["OBJECT_TYPE_SATCAT"])
    else:
        print("[warn] SATCAT enrichment returned no rows")

# Canonicalize to upper-case labels and fill any remaining gaps with 'UNKNOWN'
df["OBJECT_TYPE"] = df["OBJECT_TYPE"].astype("string").str.upper().fillna("UNKNOWN")
# Optionally convert to a categorical with expected values
df["OBJECT_TYPE"] = pd.Categorical(df["OBJECT_TYPE"],
                                   categories=["PAYLOAD","DEBRIS","ROCKET BODY","UNKNOWN"],
                                   ordered=False)

# Final ordering and save
df = df.sort_values(["NORAD_CAT_ID","EPOCH"]).reset_index(drop=True)

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT_PATH, index=False)
print(f"[2/2] Wrote {OUT_PATH} with {len(df)} rows across {df['NORAD_CAT_ID'].nunique()} satellites "
      f"(types: {sorted(df['OBJECT_TYPE'].astype(str).unique().tolist())})")

