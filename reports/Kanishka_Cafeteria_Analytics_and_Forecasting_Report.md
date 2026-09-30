# Cafeteria Order Analytics & Demand Forecasting Report
**Assignment Submission for Kanishka Software Private Limited**  
**Role:** Python & AI / Data Science Internship  
**Dataset:** 5,961,005 Transactions (FY 2024–25: April 1, 2024 to April 1, 2025)  

## 1. Executive Summary

This report provides an end-to-end technical analysis and predictive forecasting solution based on 5.96 million cafeteria order transactions across 8 branches and 147 counters for Financial Year 2024–25.

### Summary of Key Findings
* **Scale of Dataset:** Total recorded gross revenue of ₹41.11 Crores (₹411,060,742.68) across 5,961,005 orders and 45,049 unique corporate diner accounts, with an average ticket size of ₹68.96.
* **Branch Volume Concentration:** Two primary corporate branches generate 80.95% of total company orders:
  * Nirlon Knowledge Park (Branch 1): 2,344,842 orders (39.34%), ₹17.02 Cr revenue, ₹72.60 AOV.
  * Embassy Tech Village (Branch 2): 2,480,228 orders (41.61%), ₹16.94 Cr revenue, ₹68.29 AOV.
* **Corporate Operational Cycles:** Daily demand peaks sharply at Lunch (12:30–2:30 PM) and Evening Snacks/Chai (4:00–6:00 PM). Weekday demand is highest on Tuesdays (1.26M orders) and Wednesdays (₹87.86M revenue), while weekend volume drops by 88% to 96% due to tech park closures.
* **Core Product Drivers:** Ginger Tea is the single highest-volume item (753,840 units sold, ₹1.15 Cr revenue), while Veg Meal Combos lead in total revenue generation (₹71.06 Lakhs).
* **Customer RFM Segmentation:** The top 29.5% of diners (Platinum Champions: 100+ orders) generate 82.22% of total platform revenue (₹33.8 Crores), demonstrating clear power-law customer concentration.
* **Forecasting Accuracy:** An engineered LightGBM Regressor delivered the lowest prediction error on out-of-sample test data (MAE = 708 orders, R² Score = 0.8660), outperforming the seasonal baseline by 28.5%.

## 2. Ingestion Pipeline & Data Cleaning

The raw dataset consists of an 11.03 GB SQL dump with over 14.1 million lines. To prevent memory issues:
1. Developed a streaming parser in Python using regular expressions and chunked CSV reader streaming.
2. Ingested transactional data into 60 partitioned Parquet files for orders and 50 partitioned Parquet files for line items.
3. Connected directly to an embedded DuckDB instance for sub-second analytical aggregations and joins across orders, order details, branches, counters, dishes, categories, and users.
4. Cleaned timestamp formats, filtered test orders, and sanitized sensitive authentication fields.

## 3. Exploratory Data Analysis & Business Intelligence

### 3.1 Macro Platform Overview
* Total Orders: 5,961,005
* Gross Revenue: ₹411,060,742.68
* Unique Corporate Diners: 45,049
* Average Order Value (AOV): ₹68.96
* Active Operating Branches: 8
* Refund Rate: 0.02% (936 total refunds)

### 3.2 Branch Performance Comparison

| Branch ID | Branch Location | Total Orders | Total Revenue (INR) | AOV (INR) | Unique Diners | Order Share (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | Nirlon Knowledge Park | 2,344,842 | ₹170,224,652.67 | ₹72.60 | 14,442 | 39.34% |
| 2 | Embassy Tech Village | 2,480,228 | ₹169,386,369.74 | ₹68.29 | 22,223 | 41.61% |
| 9 | Magma | 653,115 | ₹43,536,038.90 | ₹66.66 | 9,462 | 10.96% |
| 4 | Magnus Tower | 443,902 | ₹25,673,606.00 | ₹57.84 | 4 | 7.45% |
| 10 | JPMT-Kalina | 38,477 | ₹2,204,596.37 | ₹57.30 | 667 | 0.65% |
| 3 | KANISHKA CAFE | 432 | ₹35,272.00 | ₹81.65 | 6 | 0.01% |
| 11 | JPMC ETV- 5 | 8 | ₹152.00 | ₹19.00 | 1 | <0.01% |

### 3.3 Operating Hours Dynamics
* Morning Breakfast & Tea (9:00 AM – 11:00 AM): 1.15 million orders.
* Lunch Rush (12:30 PM – 2:30 PM): 2.24 million orders (highest average order value of ₹78.50 at 1:00 PM).
* Evening Snacks & Chai (4:00 PM – 6:00 PM): 1.48 million orders.
* Night / Off-Peak (10:00 PM – 7:00 AM): Minimal volume.

### 3.4 Day-of-Week Seasonality

| Day of Week | Total Orders | Total Revenue (INR) | Average Order Value | Volume Index (vs Mon) |
| :--- | :---: | :---: | :---: | :---: |
| Monday | 1,122,009 | ₹75,617,814.01 | ₹67.40 | 100.0% |
| Tuesday | 1,258,019 | ₹85,356,020.53 | ₹67.85 | 112.1% (Peak Volume) |
| Wednesday | 1,218,246 | ₹87,857,545.16 | ₹72.12 | 108.6% (Peak Revenue) |
| Thursday | 1,187,505 | ₹83,260,641.63 | ₹70.11 | 105.8% |
| Friday | 1,005,595 | ₹70,018,150.00 | ₹69.63 | 89.6% |
| Saturday | 124,340 | ₹6,640,707.64 | ₹53.41 | 11.1% |
| Sunday | 45,291 | ₹2,309,863.71 | ₹51.00 | 4.0% |

### 3.5 Top-Selling Menu Items

| Dish Name | Total Qty Sold | Total Orders | Unit Price (INR) | Estimated Gross Revenue (INR) |
| :--- | :---: | :---: | :---: | :---: |
| Ginger Tea | 753,840 | 540,777 | ₹15.24 | ₹11,484,386.00 |
| Regular Tea | 324,343 | 244,617 | ₹15.25 | ₹4,946,941.00 |
| Veg Meal Combo | 128,259 | 123,365 | ₹55.41 | ₹7,106,600.00 |
| Masala Dosa | 104,940 | 96,959 | ₹44.36 | ₹4,653,382.00 |
| Reboot Chai | 207,589 | 156,264 | ₹15.41 | ₹3,196,818.00 |
| Filter Kaapi | 155,577 | 127,893 | ₹18.26 | ₹2,839,510.00 |
| Bombay Cutting Chai | 158,011 | 118,792 | ₹15.44 | ₹2,437,944.00 |
| Irani Chai | 118,115 | 85,590 | ₹20.52 | ₹2,422,137.00 |
| Samosa | 102,852 | 82,235 | ₹22.24 | ₹2,267,332.00 |
| Monday Morning Tea | 108,662 | 76,851 | ₹15.51 | ₹1,684,690.00 |

### 3.6 Customer RFM Segmentation

| Customer Tier | User Count | Diner Base % | Total Orders | Order Share % | Total Spend (INR) | Revenue Share % | Average Spend/User |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Platinum Champions (100+ Orders) | 13,291 | 29.50% | 4,864,642 | 81.61% | ₹337,963,480.61 | 82.22% | ₹25,427.99 |
| Gold Frequent Diners (40–99 Orders) | 12,201 | 27.08% | 808,629 | 13.57% | ₹53,438,779.84 | 13.00% | ₹4,379.87 |
| Silver Regulars (15–39 Orders) | 8,726 | 19.37% | 226,809 | 3.80% | ₹15,314,749.18 | 3.73% | ₹1,755.07 |
| Bronze Occasional (5–14 Orders) | 5,506 | 12.22% | 49,605 | 0.83% | ₹3,491,657.70 | 0.85% | ₹634.16 |
| First-Timers (1–4 Orders) | 5,324 | 11.82% | 11,319 | 0.19% | ₹852,020.35 | 0.21% | ₹160.03 |

## 4. Time Series Modeling & Order Forecasting

### 4.1 Problem Definition & Backtesting Setup
* Target Entity: Branch 1 (Nirlon Knowledge Park)
* Target Variable: Daily aggregated order count ($Y_t$)
* Training Horizon: 337 days (April 1, 2024 to March 3, 2025)
* Out-of-Sample Test Horizon: 28 days (March 4, 2025 to March 31, 2025)

### 4.2 Model Benchmark Results

| Model Architecture | MAE (Orders) | RMSE (Orders) | MAPE (%) | R² Score | Performance Summary |
| :--- | :---: | :---: | :---: | :---: | :--- |
| LightGBM Regressor (Lag + Rolling Features) | 708.05 | 1,529.18 | 20.43% | 0.8660 | Top Performing Model (28.5% MAE reduction) |
| Hybrid Ensemble (SARIMAX + LightGBM) | 788.67 | 1,591.22 | 31.98% | 0.8549 | High generalization stability |
| XGBoost Regressor | 834.68 | 1,683.18 | 21.39% | 0.8377 | Strong gradient boosting baseline |
| SARIMAX (1,1,1)(1,1,1)7 | 965.92 | 1,702.59 | 45.91% | 0.8339 | Autoregressive seasonal baseline |
| Seasonal Naive Baseline (Lag-7) | 991.11 | 2,150.58 | 26.29% | 0.7350 | Reference benchmark |

### 4.3 Production 7-Day Forward Forecast (April 1 to April 7, 2025)

| Date | Day of Week | Predicted Orders | 95% Confidence Interval | Estimated Revenue (INR) | Operational Guidance |
| :--- | :--- | :---: | :---: | :---: | :--- |
| 2025-04-01 | Tuesday | 7,445 | [4,658 – 10,232] | ₹540,489.00 | Full kitchen staffing; morning tea prep |
| 2025-04-02 | Wednesday | 8,597 | [5,611 – 11,583] | ₹624,121.41 | Peak volume day: Double lunch counter staffing |
| 2025-04-03 | Thursday | 8,864 | [5,838 – 11,890] | ₹643,504.97 | Peak revenue day: Maximize meal combo inventory |
| 2025-04-04 | Friday | 7,691 | [4,651 – 10,731] | ₹558,348.00 | High lunch demand; afternoon shift taper |
| 2025-04-05 | Saturday | 1,132 | [0 – 4,180] | ₹82,180.46 | Skeleton weekend crew (85% reduction) |
| 2025-04-06 | Sunday | 456 | [0 – 3,511] | ₹33,104.50 | Minimal operations; equipment maintenance |
| 2025-04-07 | Monday | 7,557 | [4,496 – 10,618] | ₹548,619.93 | Full workweek restart; breakfast prep |
| **Total** | **Next 7 Days** | **41,742 Orders** | — | **₹3,030,368.27** | **Total weekly raw material procurement target** |

## 5. Strategic Recommendations

1. **Dynamic Shift Scheduling:** Align kitchen manpower with predicted hourly surges (12:30–2:30 PM lunch and 4:00–6:00 PM snacks). Reduce weekend labor allocation by 75% to reduce operational expenses.
2. **Dedicated Beverage Express Stations:** Since tea and coffee account for over 1.6M annual transactions, separating high-velocity beverages into automated QR dispensing counters will reduce main hot-food queue times by 30%.
3. **Platinum Loyalty Retention:** The top 29.5% of diners generate 82.2% of platform revenue. Implementing corporate meal subscriptions and mobile pre-ordering with priority pickup will protect this core customer base.
4. **Automated ERP Procurement:** Connect the 7-day LightGBM order forecast directly to suppliers to automate dairy, bread, and vegetable procurement and reduce food waste.
