# Corporate Cafeteria Order Analytics & Demand Forecasting

End-to-end data engineering, business intelligence, and time-series demand forecasting pipeline built on **5.96 million order transactions** across 8 corporate cafeteria branches (FY 2024–25).

---

## Executive Summary

This repository contains the complete analytical workflow and machine learning demand forecasting system developed for the Kanishka Software evaluation challenge. The objective was to ingest and analyze a full financial year of high-volume transaction data, identify operational patterns across branches and customer segments, and build an accurate time-series model to forecast daily order demand for kitchen planning and inventory optimization.

### Key Metrics & Highlights
* **Dataset Scope:** 5,961,005 order transactions | ₹41.11 Crores ($411.06M INR) gross revenue | 45,049 unique diners.
* **Volume Concentration:** Two flagship tech park locations (**Nirlon Knowledge Park** and **Embassy Tech Village**) drive **80.95%** of all orders (₹33.96 Cr revenue).
* **Corporate Temporal Patterns:** Strong workweek cycle peaking on Tuesdays (1.26M orders) and Wednesdays (₹8.78 Cr revenue), with an 88%–96% volume drop on weekends.
* **Menu Mix:** High-velocity beverages dominate transactions (**Ginger Tea** alone accounts for 753,840 units sold / ₹1.15 Cr revenue), while Veg Meal Combos lead hot-food gross revenue.
* **Customer Distribution:** The top **29.5% of diners (Platinum tier)** generate **82.22% of total revenue** (₹33.8 Cr).
* **Forecasting Model:** A **LightGBM Regressor** with lagged demand, rolling window statistics, and calendar features achieved an **$R^2 = 0.8660$** and **MAE of 708 orders/day** on a 28-day out-of-sample backtest, reducing error by 28.5% compared to the seasonal baseline.
* **Forward Forecast:** Projected **41,742 orders** (~₹30.3 Lakhs revenue) for Branch 1 across the next 7-day operational cycle (April 1–7, 2025).

---

## Data Architecture & ETL Pipeline

The raw dataset was provided as an 11.03 GB SQL dump containing over 14.1 million rows across orders, order details, counters, dishes, and user profiles.

To handle this volume efficiently on a local workstation without out-of-memory (OOM) failures:
1. **Streaming SQL Parser (`src/extract_full_pipeline.py`):** Built a line-by-line regex ingestion engine that extracts insert tuples, casts data types, and streams rows directly into batch chunks.
2. **Columnar Parquet Storage:** Converted large transactional tables into partitioned Parquet files (`data/*.parquet`), reducing disk footprint by >85% while enabling fast vectorized reads.
3. **Embedded OLAP with DuckDB:** Used DuckDB (`data/cafeteria.duckdb`) for sub-second analytical queries, multi-table aggregations, and RFM metric computation without requiring a standalone database server.

---

## Core Analytics & Business Insights

### 1. Branch Performance Breakdown

| Branch ID | Location | Orders | Revenue (INR) | AOV (INR) | Unique Diners | Order Share |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | Nirlon Knowledge Park | 2,344,842 | ₹17,02,24,652.67 | ₹72.60 | 14,442 | 39.34% |
| 2 | Embassy Tech Village | 2,480,228 | ₹16,93,86,369.74 | ₹68.29 | 22,223 | 41.61% |
| 9 | Magma | 653,115 | ₹4,35,36,038.90 | ₹66.66 | 9,462 | 10.96% |
| 4 | Magnus Tower | 443,902 | ₹2,56,73,606.00 | ₹57.84 | 4 | 7.45% |
| 10 | JPMT-Kalina | 38,477 | ₹22,04,596.37 | ₹57.30 | 667 | 0.65% |
| 3 | KANISHKA CAFE | 432 | ₹35,272.00 | ₹81.65 | 6 | 0.01% |
| 11 | JPMC ETV- 5 | 8 | ₹152.00 | ₹19.00 | 1 | <0.01% |

### 2. Operational Dynamics & Rush Hours
* **Breakfast / Morning Tea (09:00 - 11:00 AM):** 1.15 million orders (beverage-heavy).
* **Lunch Rush (12:30 - 02:30 PM):** 2.24 million orders, reaching peak AOV (₹78.50) at 1:00 PM.
* **Evening Snacks & Chai (04:00 - 06:00 PM):** 1.48 million orders.
* **Off-Peak (10:00 PM - 07:00 AM):** Minimal activity, matching corporate office hours.

### 3. Customer RFM Segmentation

| Tier | Order Frequency | User Count | Diner % | Total Orders | Order % | Spend (INR) | Spend % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Platinum Champions** | 100+ orders | 13,291 | 29.50% | 4,864,642 | 81.61% | ₹33.80 Cr | 82.22% |
| **Gold Frequent** | 40–99 orders | 12,201 | 27.08% | 808,629 | 13.57% | ₹5.34 Cr | 13.00% |
| **Silver Regulars** | 15–39 orders | 8,726 | 19.37% | 226,809 | 3.80% | ₹1.53 Cr | 3.73% |
| **Bronze Occasional** | 5–14 orders | 5,506 | 12.22% | 49,605 | 0.83% | ₹34.91 L | 0.85% |
| **First-Timers** | 1–4 orders | 5,324 | 11.82% | 11,319 | 0.19% | ₹8.52 L | 0.21% |

---

## Time Series Forecasting Engine

### Problem Formulation
* **Target:** Daily aggregated order count for Branch 1 (Nirlon Knowledge Park).
* **Training Horizon:** April 1, 2024 to March 3, 2025 (337 days).
* **Out-of-Sample Test Window:** March 4, 2025 to March 31, 2025 (28 days).
* **Feature Engineering:**
  * Lag features: $t-1, t-2, t-3, t-7, t-14, t-21, t-28$.
  * Rolling statistics: 7-day and 14-day rolling mean and standard deviation.
  * Calendar signals: Day of week, day of month, month, and weekend indicator.

### Model Benchmark Comparison

| Model | MAE (Orders) | RMSE (Orders) | MAPE (%) | $R^2$ Score | Notes |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **LightGBM Regressor** | **708.05** | **1,529.18** | **20.43%** | **0.8660** | **Best performance across all metrics** |
| Hybrid (SARIMAX + LightGBM) | 788.67 | 1,591.22 | 31.98% | 0.8549 | Combines linear trend with GBDT residuals |
| XGBoost Regressor | 834.68 | 1,683.18 | 21.39% | 0.8377 | Strong non-linear baseline |
| SARIMAX $(1,1,1)(1,1,1)_7$ | 965.92 | 1,702.59 | 45.91% | 0.8339 | Captures 7-day seasonality |
| Seasonal Naive (Lag-7) | 991.11 | 2,150.58 | 26.29% | 0.7350 | Baseline reference |

### Next 7-Day Forward Forecast (Branch 1)

| Date | Day | Predicted Orders | 95% Confidence Interval | Est. Revenue (INR) | Operational Note |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 2025-04-01 | Tuesday | 7,445 | [4,658 – 10,232] | ₹5,40,489 | Full kitchen staffing; morning tea prep |
| 2025-04-02 | Wednesday | 8,597 | [5,611 – 11,583] | ₹6,24,121 | Peak volume day: Double lunch line staffing |
| 2025-04-03 | Thursday | 8,864 | [5,838 – 11,890] | ₹6,43,505 | Peak revenue day: Max meal combo stock |
| 2025-04-04 | Friday | 7,691 | [4,651 – 10,731] | ₹5,58,348 | High lunch rush; afternoon taper |
| 2025-04-05 | Saturday | 1,132 | [0 – 4,180] | ₹82,180 | Skeleton weekend crew (85% reduction) |
| 2025-04-06 | Sunday | 456 | [0 – 3,511] | ₹33,105 | Minimal operations; maintenance |
| 2025-04-07 | Monday | 7,557 | [4,496 – 10,618] | ₹5,48,620 | Workweek restart; full inventory restock |
| **Total** | **7 Days** | **41,742** | — | **₹30,30,368** | **Raw material procurement baseline** |

---

## Operational Recommendations

1. **Dynamic Staff Scheduling:** Allocate peak kitchen staffing during 12:30–2:30 PM (lunch) and 4:00–6:00 PM (tea). Reduce weekend staffing by 75–85% to cut operating expenses.
2. **Dedicated Beverage Express Counters:** High-volume hot beverages (Ginger Tea, Regular Tea, Filter Kaapi) account for over 1.6M transactions. Separating these into automated QR/kiosk pickup lines will reduce main meal queue bottlenecks.
3. **Loyalty Protection for Platinum Segment:** 29.5% of diners drive 82.2% of revenue. Implement pre-ordering, dedicated express pickup lines, and subscription passes for this segment.
4. **Predictive Procurement Integration:** Feed the 7-day LightGBM order forecast directly to suppliers to automate perishables ordering (milk, bread, vegetables) and minimize food waste.

---

## Repository Structure

```
.
├── notebooks/
│   └── Cafeteria_Analysis_and_Forecasting.ipynb   # Interactive analysis & visualization notebook
├── src/
│   ├── extract_full_pipeline.py                   # Streaming SQL parser and Parquet/DuckDB ETL
│   ├── extract_lookup_tables.py                   # Dimension table extractor (branches, dishes, users)
│   ├── eda_analysis.py                            # Aggregations, metrics, and RFM segmentation
│   ├── forecast_engine.py                         # Time-series feature engineering, benchmarking & forecasting
│   ├── generate_visualizations.py                 # High-resolution chart generation
│   └── generate_html_report.py                    # Standalone HTML presentation dashboard builder
├── reports/
│   ├── Executive_Presentation_Report.html         # Interactive dashboard presentation (open in browser)
│   ├── Kanishka_Cafeteria_Analytics_and_Forecasting_Report.md  # Detailed technical report
│   ├── model_benchmark_comparison.csv             # Evaluation metrics across all 5 models
│   ├── next_7_days_forecast.csv                   # Daily predictions with confidence intervals
│   ├── branch_performance.csv                     # Branch-level summaries
│   └── customer_rfm_segments.csv                  # RFM segment aggregates
├── visualizations/                                # Exported charts (PNG, 300 DPI)
│   ├── branch_revenue_and_volume.png
│   ├── hourly_operating_dynamics.png
│   ├── day_of_week_seasonality.png
│   ├── top_selling_menu_items.png
│   ├── customer_rfm_pareto_analysis.png
│   ├── forecasting_backtest_evaluation.png
│   └── future_7_day_forecast.png
├── submission/
│   ├── HR_Submission_Email_Draft.md               # Ready-to-send submission email
│   └── Vedant_Dhoke_Resume.pdf                    # Candidate resume
└── requirements.txt                               # Project dependencies
```

---

## Setup & How to Run

### Prerequisites
* Python 3.10 or higher
* Recommended: Virtual environment

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/VedantDhoke11/Cafeteria_Data_Analysis.git
cd Cafeteria_Data_Analysis

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Run Analysis & Forecasting Pipeline
```bash
# Step 1: Run Business Intelligence and RFM Analysis
python src/eda_analysis.py

# Step 2: Run Machine Learning Time-Series Models & Forecast
python src/forecast_engine.py

# Step 3: Generate Visualizations & Presentation Report
python src/generate_visualizations.py
python src/generate_html_report.py
```

### 3. Review Interactive Notebook & Dashboard
* **Jupyter Notebook:**
  ```bash
  jupyter notebook notebooks/Cafeteria_Analysis_and_Forecasting.ipynb
  ```
* **Interactive Presentation Dashboard:**
  Open `reports/Executive_Presentation_Report.html` in any web browser.

---

## Author

**Vedant Dhoke**  
* Email: [vedantdhoke311@gmail.com](mailto:vedantdhoke311@gmail.com)  
* GitHub: [github.com/VedantDhoke11](https://github.com/VedantDhoke11)  
