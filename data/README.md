![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Project-Active-brightgreen)
![Built With](https://img.shields.io/badge/Built%20With-Orbital%20Mechanics%20%26%20ML-purple)
![Datathon](https://img.shields.io/badge/Datathon-Women%20in%20Data%202025-black)

# 🛰️ Project BlackSky: Watching the Watchers

> _"Suspicious skies, revealed."_

## 📦 Data Sources

- [Unified Data Library (UDL)](https://udl.ussf.cdao.mil/) – TLEs, state vectors
- [Space-Track.org](https://www.space-track.org/)
- [UCS Satellite Database](https://www.ucsusa.org/resources/satellite-database)

## 📂 Input (Used in Jupyter notebook)

Run `python fetch_spacetrack.py` in ../scripts to generate this file:

- ../data/in/tle_gp_history_180days_20250906.csv

## 📂 Output (Used in Power BI report)

- anomalous_rows.csv
- dailies.csv
- scores.csv
- ucs.csv - run `python fetch_ucs.py` in ../scripts to generate this file.

## 📑 Data Dictionaries

### anomalous_rows.csv

| Column                | Type        | Description                                                                  |
| --------------------- | ----------- | ---------------------------------------------------------------------------- |
| **norad_id**          | Integer     | Unique NORAD catalog identifier for the satellite/object.                    |
| **epoch**             | Datetime    | Timestamp of the orbital element set (observation time).                     |
| **period_min**        | Float       | Orbital period in minutes.                                                   |
| **a_km**              | Float       | Semi-major axis (average orbital radius) in kilometers.                      |
| **apo_km**            | Float       | Apogee altitude (farthest point from Earth) in kilometers.                   |
| **per_km**            | Float       | Perigee altitude (closest point to Earth) in kilometers.                     |
| **mean_motion**       | Float       | Revolutions per day (satellite’s orbital speed).                             |
| **ecc**               | Float       | Orbital eccentricity (0 = circular, closer to 1 = elongated).                |
| **incl**              | Float       | Inclination angle in degrees (tilt of orbit relative to Earth’s equator).    |
| **bstar**             | Float       | Atmospheric drag term from TLE (proxy for drag effects).                     |
| **d_mean_motion**     | Float       | Change in mean motion compared to baseline/previous epoch.                   |
| **mean_motion_rate**  | Float       | Rate of change of mean motion.                                               |
| **d_ecc**             | Float       | Change in eccentricity compared to baseline/previous epoch.                  |
| **ecc_rate**          | Float       | Rate of change of eccentricity.                                              |
| **d_incl**            | Float       | Change in inclination compared to baseline/previous epoch.                   |
| **incl_rate**         | Float       | Rate of change of inclination.                                               |
| **raan_rate_resid**   | Float       | Residual difference between observed RAAN drift and expected J2-based drift. |
| **raan_resid_std**    | Float       | Standard deviation of RAAN residuals (variability of drift).                 |
| **mm_std**            | Float       | Standard deviation of mean motion across the window.                         |
| **incl_std**          | Float       | Standard deviation of inclination across the window.                         |
| **ecc_std**           | Float       | Standard deviation of eccentricity across the window.                        |
| **bstar_std**         | Float       | Standard deviation of bstar (drag term).                                     |
| **regime**            | String      | Orbital regime classification (e.g., LEO, MEO, GEO, HEO, SSO, UNKNOWN).      |
| **anomaly_score**     | Float       | Computed anomaly score for this observation.                                 |
| **anomaly_label**     | Integer     | Label assigned by model/algorithm (-1 = anomaly, 1 = normal).                |
| **is_anomaly**        | Boolean/Int | Binary flag (1 = anomaly, 0 = normal).                                       |
| **sat_7d_latch**      | Integer     | Binary flag indicating if any anomaly occurred in last 7 days.               |
| **sat_7d_anom_count** | Integer     | Number of anomalies detected in the last 7 days.                             |
| **sat_7d_anom_frac**  | Float       | Fraction of anomalous epochs in the last 7 days.                             |

### dailies.csv

| Column                | Type        | Description                                                             |
| --------------------- | ----------- | ----------------------------------------------------------------------- |
| **norad_id**          | Integer     | Unique NORAD catalog identifier for the satellite/object.               |
| **regime**            | String      | Orbital regime classification (e.g., LEO, MEO, GEO, HEO, SSO, UNKNOWN). |
| **day**               | Date        | Calendar date of the observation summary (daily aggregation).           |
| **n_obs_day**         | Integer     | Number of total observations recorded for the satellite on that day.    |
| **n_anom_day**        | Integer     | Number of anomalous observations detected on that day.                  |
| **frac_anom_day**     | Float       | Fraction of anomalous observations (`n_anom_day / n_obs_day`).          |
| **mean_score_day**    | Float       | Average anomaly score across all observations for that day.             |
| **min_score_day**     | Float       | Minimum anomaly score observed for that satellite on that day.          |
| **max_score_day**     | Float       | Maximum anomaly score observed for that satellite on that day.          |
| **any_anom_day**      | Boolean/Int | Flag (1/0) indicating if **any anomaly** occurred on that day.          |
| **day_7d_latch**      | Boolean/Int | Flag (1/0) indicating if any anomaly was detected in the last 7 days.   |
| **day_7d_anom_count** | Integer     | Total number of anomalies detected in the last 7 days (rolling window). |
| **day_7d_anom_frac**  | Float       | Fraction of anomalies in the last 7 days relative to observations.      |

### scores.csv

| Column                 | Type        | Description                                                                    |
| ---------------------- | ----------- | ------------------------------------------------------------------------------ |
| **norad_id**           | Integer     | Unique NORAD catalog identifier for the satellite/object.                      |
| **regime**             | String      | Orbital regime classification (e.g., LEO, MEO, GEO, HEO, SSO, UNKNOWN).        |
| **mean_score**         | Float       | Average anomaly score across all observations.                                 |
| **std_score**          | Float       | Standard deviation of anomaly scores across all observations.                  |
| **n_obs**              | Integer     | Total number of observations for the satellite.                                |
| **anom_k**             | Integer     | Count of anomalous observations (exceeding anomaly threshold).                 |
| **frac_anom**          | Float       | Fraction of anomalous observations (`anom_k / n_obs`).                         |
| **last_epoch**         | Datetime    | Timestamp of the most recent observation.                                      |
| **recent_latch**       | Integer     | Binary flag (0/1) indicating if any anomaly was detected in the recent window. |
| **recent_anom_count**  | Integer     | Number of anomalies detected in the recent time window (e.g., last 7 days).    |
| **recent_anom_frac**   | Float       | Fraction of anomalies relative to total observations in the recent window.     |
| **frac_anom_wlb**      | Float       | Weighted long-baseline fraction of anomalies.                                  |
| **mean_score_cut**     | Float       | Mean anomaly score after applying cutoff/threshold.                            |
| **frac_wlb_cut**       | Float       | Weighted long-baseline anomaly fraction after cutoff.                          |
| **recent_frac_cut**    | Float       | Fraction of anomalies in recent window after cutoff.                           |
| **flag_score_tail**    | Boolean/Int | Indicator if anomaly score lies in distribution tail (rare/high values).       |
| **flag_frac_high**     | Boolean/Int | Indicator if fraction of anomalies is above a defined threshold.               |
| **flag_recent**        | Boolean/Int | Indicator if recent anomaly activity is significant.                           |
| **risk_points_regime** | Integer     | Risk points assigned based on regime-specific rules.                           |
| **suspiciousness**     | Float       | Final suspiciousness score, combining multiple anomaly and risk indicators.    |
