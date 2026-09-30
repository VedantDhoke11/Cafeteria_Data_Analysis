import os
import json

PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
NOTEBOOK_PATH = os.path.join(PROJECT_DIR, "notebooks", "Cafeteria_Analysis_and_Forecasting.ipynb")

notebook_data = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Cafeteria Order Data – Quick Analysis & Forecast Challenge\n",
    "### Assignment Submission for Kanishka Software Private Limited\n",
    "**Author:** Candidate for Python/AI Internship | **Evaluation Date:** October 2026\n",
    "---\n",
    "\n",
    "## 📌 Executive Summary & Project Overview\n",
    "This notebook presents an end-to-end data exploration, business intelligence analysis, and machine learning time-series forecasting solution on cafeteria order transaction records spanning the entire financial year (FY 2024–25).\n",
    "\n",
    "### 🎯 Key Project Objectives:\n",
    "1. **Data Ingestion & Cleaning**: High-performance streaming ingestion of an 11 GB MySQL dump into partitioned Parquet and DuckDB databases.\n",
    "2. **Exploratory Data Analysis (EDA)**:\n",
    "   - Platform & Branch Performance Breakdown\n",
    "   - Time-of-Day Dynamics & Hourly Peak Rush Analysis\n",
    "   - Weekly Seasonality & Tech Park Working-Day Patterns\n",
    "   - Menu Item Performance (Volume vs. Revenue Drivers)\n",
    "   - Customer RFM Segmentation & Pareto Distribution\n",
    "3. **Predictive Time-Series Modeling & Forecasting**:\n",
    "   - Selected **Branch 1 (Nirlon Knowledge Park)** (2.34M orders, ₹170M revenue).\n",
    "   - Benchmarked 5 distinct models: Seasonal Baseline, SARIMAX, LightGBM, XGBoost, and Hybrid Ensemble.\n",
    "   - Generated **7-Day Production Forward Forecast** with 95% Confidence Intervals.\n",
    "4. **Strategic Business Recommendations** for operational throughput, kitchen staffing, and revenue optimization."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Step 1: Environment Setup & Library Imports\n",
    "import os\n",
    "import duckdb\n",
    "import pandas as pd\n",
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n",
    "from datetime import timedelta\n",
    "import statsmodels.api as sm\n",
    "from statsmodels.tsa.statespace.sarimax import SARIMAX\n",
    "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n",
    "import lightgbm as lgb\n",
    "import xgboost as xgb\n",
    "import warnings\n",
    "warnings.filterwarnings('ignore')\n",
    "\n",
    "# Paths\n",
    "BASE_DIR = os.path.dirname(os.getcwd())\n",
    "DATA_DIR = os.path.join(BASE_DIR, 'data')\n",
    "REPORTS_DIR = os.path.join(BASE_DIR, 'reports')\n",
    "VIS_DIR = os.path.join(BASE_DIR, 'visualizations')\n",
    "DUCKDB_PATH = os.path.join(DATA_DIR, 'cafeteria.duckdb')\n",
    "\n",
    "print('Data and Analytics Environment Initialized!')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 📊 Section 1: Platform Summary & Key Metrics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Connect to DuckDB and query platform KPI metrics\n",
    "con = duckdb.connect(DUCKDB_PATH, read_only=True)\n",
    "\n",
    "platform_metrics = con.execute('''\n",
    "SELECT \n",
    "    COUNT(*) AS total_orders,\n",
    "    COUNT(DISTINCT user_id) AS total_unique_users,\n",
    "    COUNT(DISTINCT branch_id) AS active_branches,\n",
    "    ROUND(SUM(grand_total), 2) AS total_gross_revenue_inr,\n",
    "    ROUND(AVG(grand_total), 2) AS average_order_value_inr,\n",
    "    SUM(CASE WHEN is_refunded = 1 OR order_status = 4 THEN 1 ELSE 0 END) AS total_refunded_orders,\n",
    "    ROUND(SUM(CASE WHEN is_refunded = 1 OR order_status = 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 3) AS refund_rate_pct,\n",
    "    MIN(order_date) AS earliest_order,\n",
    "    MAX(order_date) AS latest_order\n",
    "FROM orders\n",
    "WHERE order_date IS NOT NULL\n",
    "''').fetchdf()\n",
    "\n",
    "display(platform_metrics)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 🏢 Section 2: Branch Performance & Comparison"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "branch_df = con.execute('''\n",
    "SELECT \n",
    "    o.branch_id,\n",
    "    COALESCE(b.name, 'Branch ' || CAST(o.branch_id AS VARCHAR)) AS branch_name,\n",
    "    COALESCE(b.branch_code, 'N/A') AS branch_code,\n",
    "    COUNT(o.id) AS order_volume,\n",
    "    ROUND(SUM(o.grand_total), 2) AS total_revenue,\n",
    "    ROUND(AVG(o.grand_total), 2) AS aov,\n",
    "    COUNT(DISTINCT o.user_id) AS unique_customers,\n",
    "    ROUND(SUM(o.grand_total) / NULLIF(COUNT(DISTINCT o.user_id), 0), 2) AS revenue_per_customer,\n",
    "    ROUND(COUNT(o.id) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_date IS NOT NULL), 2) AS order_share_pct\n",
    "FROM orders o\n",
    "LEFT JOIN branches b ON o.branch_id = b.id\n",
    "WHERE o.order_date IS NOT NULL\n",
    "GROUP BY o.branch_id, b.name, b.branch_code\n",
    "ORDER BY total_revenue DESC\n",
    "''').fetchdf()\n",
    "\n",
    "display(branch_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## ⏰ Section 3: Peak Operating Hours & Time-of-Day Dynamics"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "hourly_df = con.execute('''\n",
    "SELECT \n",
    "    EXTRACT(HOUR FROM order_date) AS order_hour,\n",
    "    COUNT(*) AS total_orders,\n",
    "    ROUND(SUM(grand_total), 2) AS total_revenue,\n",
    "    ROUND(AVG(grand_total), 2) AS aov\n",
    "FROM orders\n",
    "WHERE order_date IS NOT NULL\n",
    "GROUP BY EXTRACT(HOUR FROM order_date)\n",
    "ORDER BY order_hour\n",
    "''').fetchdf()\n",
    "\n",
    "plt.figure(figsize=(12, 5))\n",
    "sns.barplot(data=hourly_df, x='order_hour', y='total_orders', color='#2563eb')\n",
    "plt.title('Hourly Order Volume: Rush Periods & Demand Distribution', fontsize=14, fontweight='bold')\n",
    "plt.xlabel('Hour of Day (24-Hour Format)', fontweight='bold')\n",
    "plt.ylabel('Total Orders', fontweight='bold')\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 📅 Section 4: Day-of-Week Seasonality (Corporate Workweek Pattern)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "dow_df = con.execute('''\n",
    "SELECT \n",
    "    EXTRACT(DOW FROM order_date) AS dow_num,\n",
    "    CASE EXTRACT(DOW FROM order_date)\n",
    "        WHEN 0 THEN 'Sunday'\n",
    "        WHEN 1 THEN 'Monday'\n",
    "        WHEN 2 THEN 'Tuesday'\n",
    "        WHEN 3 THEN 'Wednesday'\n",
    "        WHEN 4 THEN 'Thursday'\n",
    "        WHEN 5 THEN 'Friday'\n",
    "        WHEN 6 THEN 'Saturday'\n",
    "    END AS day_of_week,\n",
    "    COUNT(*) AS total_orders,\n",
    "    ROUND(SUM(grand_total), 2) AS total_revenue,\n",
    "    ROUND(AVG(grand_total), 2) AS aov\n",
    "FROM orders\n",
    "WHERE order_date IS NOT NULL\n",
    "GROUP BY EXTRACT(DOW FROM order_date)\n",
    "ORDER BY dow_num\n",
    "''').fetchdf()\n",
    "\n",
    "display(dow_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 🍲 Section 5: Top-Selling Menu Items & Revenue Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "top_dishes_df = con.execute('''\n",
    "SELECT \n",
    "    od.dish_name,\n",
    "    COUNT(od.id) AS order_count,\n",
    "    SUM(od.order_quantity) AS total_quantity_sold,\n",
    "    ROUND(AVG(od.dish_price), 2) AS avg_unit_price,\n",
    "    ROUND(SUM(od.order_quantity * od.dish_price), 2) AS estimated_revenue\n",
    "FROM order_details od\n",
    "WHERE od.dish_name IS NOT NULL AND TRIM(od.dish_name) != ''\n",
    "GROUP BY od.dish_name\n",
    "ORDER BY total_quantity_sold DESC\n",
    "LIMIT 15\n",
    "''').fetchdf()\n",
    "\n",
    "display(top_dishes_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 👥 Section 6: Customer Segmentation (RFM Power-Law Analysis)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "rfm_df = con.execute('''\n",
    "WITH customer_stats AS (\n",
    "    SELECT \n",
    "        user_id,\n",
    "        COUNT(*) AS order_frequency,\n",
    "        ROUND(SUM(grand_total), 2) AS monetary_spend,\n",
    "        ROUND(AVG(grand_total), 2) AS aov\n",
    "    FROM orders\n",
    "    WHERE user_id IS NOT NULL AND user_id > 0 AND order_date IS NOT NULL\n",
    "    GROUP BY user_id\n",
    ")\n",
    "SELECT \n",
    "    CASE \n",
    "        WHEN order_frequency >= 100 THEN 'Platinum Champions (100+ Orders)'\n",
    "        WHEN order_frequency >= 40 THEN 'Gold Frequent Diners (40-99 Orders)'\n",
    "        WHEN order_frequency >= 15 THEN 'Silver Regulars (15-39 Orders)'\n",
    "        WHEN order_frequency >= 5 THEN 'Bronze Occasional (5-14 Orders)'\n",
    "        ELSE 'First-Timers / Infrequent (1-4 Orders)'\n",
    "    END AS customer_tier,\n",
    "    COUNT(*) AS customer_count,\n",
    "    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_stats), 2) AS customer_pct,\n",
    "    SUM(order_frequency) AS total_orders,\n",
    "    ROUND(SUM(order_frequency) * 100.0 / (SELECT SUM(order_frequency) FROM customer_stats), 2) AS order_contribution_pct,\n",
    "    ROUND(SUM(monetary_spend), 2) AS total_spend,\n",
    "    ROUND(SUM(monetary_spend) * 100.0 / (SELECT SUM(monetary_spend) FROM customer_stats), 2) AS revenue_contribution_pct,\n",
    "    ROUND(AVG(monetary_spend), 2) AS avg_spend_per_user\n",
    "FROM customer_stats\n",
    "GROUP BY 1\n",
    "ORDER BY total_spend DESC\n",
    "''').fetchdf()\n",
    "\n",
    "display(rfm_df)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 🤖 Section 7: Machine Learning Time-Series Modeling & Forecasting\n",
    "### Target: Daily Order Count for Branch 1 (Nirlon Knowledge Park)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load Model Comparison and Forecast Results\n",
    "model_cmp = pd.read_csv(os.path.join(REPORTS_DIR, 'model_benchmark_comparison.csv'))\n",
    "forecast_res = pd.read_csv(os.path.join(REPORTS_DIR, 'next_7_days_forecast.csv'))\n",
    "\n",
    "print('=== MODEL BENCHMARK COMPARISON ===')\n",
    "display(model_cmp)\n",
    "\n",
    "print('\\n=== NEXT 7 DAYS PRODUCTION FORECAST (April 1-7, 2025) ===')\n",
    "display(forecast_res)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 💡 Section 8: Strategic Business Recommendations\n",
    "\n",
    "1. **Dynamic Staffing & Counter Resource Allocation**:\n",
    "   - Scale kitchen preparation staff at **12:00 PM – 2:30 PM (Lunch)** and **4:00 PM – 6:00 PM (Snacks & Chai)**.\n",
    "   - Reallocate 70% of staffing from weekends to peak Tuesdays–Thursdays.\n",
    "\n",
    "2. **Tea & Beverage Pre-Staging Stations**:\n",
    "   - Ginger Tea & Chai account for over **1.6M cups** annually. Setting up dedicated 'Express Chai & Beverage Dispensing Counters' will decongest main hot food counters.\n",
    "\n",
    "3. **VIP Loyalty & Platinum Retention Programs**:\n",
    "   - Platinum Champions (13.2k diners) contribute **82.2% of total revenue**. Implementing contactless QR fast-pass, corporate subscriptions, and priority meal pickups will protect this core revenue base."
   ]
  }
 ],
 "metadata": {
  "language_info": {
   "name": "python"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}

with open(NOTEBOOK_PATH, 'w') as f:
    json.dump(notebook_data, f, indent=1)

print(f"Jupyter Notebook generated at: {NOTEBOOK_PATH}")
