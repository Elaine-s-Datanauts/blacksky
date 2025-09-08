![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Project-Active-brightgreen)
![Built With](https://img.shields.io/badge/Built%20With-Orbital%20Mechanics%20%26%20ML-purple)
![Datathon](https://img.shields.io/badge/Datathon-Women%20in%20Data%202025-black)

# 🛰️ Project BlackSky: Watching the Watchers

> _"Suspicious skies, revealed."_

## 📌 Overview

BlackSky+ leverages orbital data and machine learning to **detect cyber and behavioral threats in satellites**, revealing which systems are suspicious, most vulnerable, and/or at risk.

The goal: fingerprint suspicious satellites by combining orbital anomaly detection with contextual information, enabling analysts to monitor, investigate, and respond to potentially spoofed or adversarial activity in space.

## 🚀 Problem Statement

Satellites are critical infrastructure for communications, navigation, and surveillance. Yet, some satellites exhibit **spoofed, deceptive, or anomalous orbital patterns** that may indicate interference or hidden purposes.

BlackSky builds a **suspiciousness scoring system** to:

- Detect satellites with out-of-family orbital behavior
- Quantify anomaly levels per satellite and regime
- Correlate satellite disruptions with **space weather events**
- Provide an interactive dashboard for monitoring

## 📦 Data Sources

- [Unified Data Library (UDL)](https://udl.ussf.cdao.mil/)
- [Space-Track.org](https://www.space-track.org/)
- [UCS Satellite Database](https://www.ucsusa.org/resources/satellite-database)

> **Space Weather Context**  
> _Impact of Space Weather on GNSS Signal Quality and Availability_: Analyze station-level signal quality and outages, and understand satellite broadcast behavior over daily cycles.  
> The behaviour is influenced by many factors, one of them is **space weather**.

## 🧮 Methods

1. **Data Engineering**

   - Fetch and clean TLE/GP history (12+ days).
   - Deduplicate by NORAD ID and latest epoch.
   - Merge with UCS metadata.

2. **Feature Engineering**

   - Calculate anomaly scores (Isolation Forest / One-Class SVM).
   - Derive rolling 7-day anomaly counts and fractions.
   - Assign orbital regimes (LEO, MEO, GEO, HEO, SSO).
   - Correlate anomalies with **space weather and GNSS disruptions**.

3. **Suspiciousness Scoring**

   - Weighted scoring across regimes.
   - Flags for recent anomaly bursts, tail risk, and sustained deviations.
   - Risk points converted into a `suspiciousness` index.

4. **Outputs**
   - `scores.csv`: Latest suspiciousness scores per satellite.
   - `dailies.csv`: Daily anomaly time series.
   - `anomalous_rows.csv` : Detailed event-level records of anomalies.

## 📊 Power BI Dashboard

The dashboard provides:

- **High-Level KPIs**
  - Number of suspicious satellites in the last 7 days
  - Regime breakdowns
  - GNSS outages correlated with solar activity
- **Trend Visualizations**
  - Anomaly fractions over time
  - Rolling anomaly windows
  - GNSS signal availability vs. space weather
- **Investigative Views**
  - Satellite-level detail with metadata
  - Heatmaps of anomalies by day
