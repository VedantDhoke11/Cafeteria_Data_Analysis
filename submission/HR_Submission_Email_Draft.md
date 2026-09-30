# Official HR Submission Email

**To:** hr@ksoftpl.com  
**Subject:** Submission: Cafeteria Order Data Analysis & Demand Forecast Challenge – Vedant Dhoke

---

Dear HR Team,

I hope this email finds you well.

I have completed the technical evaluation challenge for the **Cafeteria Order Data – Quick Analysis & Forecast Challenge** as part of the application process for the Python & AI / Data Science Internship role at Kanishka Software.

I analyzed the complete FY 2024–25 transaction dataset (5.96 million orders across 8 branches), performed exploratory data analysis with customer RFM segmentation, and built a machine learning time-series demand forecasting system.

### Key Highlights & Deliverables:
1. **Data Pipeline & Performance:** Built a streaming regex ETL pipeline to ingest the 11 GB raw SQL dump into partitioned Parquet files and DuckDB, enabling sub-second analytical queries without memory overhead.
2. **Business Intelligence & EDA:**
   * Analyzed ₹41.11 Crores gross revenue across 5.96M orders and 45,049 unique corporate diners.
   * Highlighted volume concentration across flagship tech park branches (Nirlon Knowledge Park and Embassy Tech Village generate 80.95% of total volume).
   * Identified peak operating windows (Lunch: 12:30–2:30 PM, Snacks/Tea: 4:00–6:00 PM) and quantified the 88–96% volume drop on weekends.
   * Uncovered key customer distribution: the top 29.5% of diners (Platinum tier) drive 82.22% of total platform revenue.
3. **Time-Series Demand Forecasting:**
   * Formulated and evaluated 5 time-series models for Branch 1 on a 28-day out-of-sample backtest.
   * The engineered **LightGBM Regressor** achieved an **R² score of 0.8660** (MAE: 708 orders/day), reducing forecast error by 28.5% over the baseline.
   * Generated a 7-day forward operational forecast (41,742 orders / ~₹30.3 Lakhs revenue) with 95% confidence intervals and kitchen staffing recommendations.

### Repository & Deliverables:
* **GitHub Repository:** https://github.com/VedantDhoke11/Cafeteria_Data_Analysis
* **Presentation Dashboard:** Included in repository (`reports/Executive_Presentation_Report.html`)
* **Attached:** Updated Resume (`Vedant_Dhoke_Resume.pdf`)

The repository includes the complete source code, documented ETL and ML scripts, an interactive Jupyter Notebook, visual charts, and the standalone HTML report.

Thank you for the opportunity, and I look forward to discussing my technical approach and results with the team.

Warm regards,

**Vedant Dhoke**  
Email: vedantdhoke11@gmail.com  
GitHub: https://github.com/VedantDhoke11  
LinkedIn: https://www.linkedin.com/in/vedant-dhoke  
