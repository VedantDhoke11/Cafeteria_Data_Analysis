import os
import base64

PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
VIS_DIR = os.path.join(PROJECT_DIR, "visualizations")
HTML_PATH = os.path.join(PROJECT_DIR, "reports", "Executive_Presentation_Report.html")

def img_to_b64(fname):
    p = os.path.join(VIS_DIR, fname)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode('utf-8')
    return ""

img_branch = img_to_b64("branch_revenue_and_volume.png")
img_hourly = img_to_b64("hourly_operating_dynamics.png")
img_dow = img_to_b64("day_of_week_seasonality.png")
img_dishes = img_to_b64("top_selling_menu_items.png")
img_rfm = img_to_b64("customer_rfm_pareto_analysis.png")
img_backtest = img_to_b64("forecasting_backtest_evaluation.png")
img_forecast = img_to_b64("future_7_day_forecast.png")
img_feat = img_to_b64("feature_importance_ranking.png")
img_growth = img_to_b64("monthly_growth_trend.png")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cafeteria Order Analysis & Forecasting Challenge | Kanishka Software</title>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #10b981;
            --dark: #0f172a;
            --slate: #334155;
            --light: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #f1f5f9;
            color: var(--slate);
            line-height: 1.6;
            padding: 24px;
        }}
        .container {{
            max-width: 1280px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
            color: white;
            padding: 36px 40px;
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
            margin-bottom: 28px;
        }}
        header h1 {{ font-size: 28px; font-weight: 800; margin-bottom: 8px; }}
        header p {{ font-size: 15px; opacity: 0.9; }}
        .badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .grid-4 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 28px;
        }}
        .kpi-card {{
            background: var(--card-bg);
            padding: 24px;
            border-radius: 14px;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
        }}
        .kpi-title {{ font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 26px; font-weight: 800; color: var(--dark); margin: 6px 0; }}
        .kpi-sub {{ font-size: 12.5px; color: #059669; font-weight: 600; }}
        .section-card {{
            background: var(--card-bg);
            padding: 30px;
            border-radius: 16px;
            border: 1px solid var(--border);
            margin-bottom: 28px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 16px;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 18px 0;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            background: #f8fafc;
            color: var(--dark);
            font-weight: 700;
        }}
        tr:hover td {{ background: #f8fafc; }}
        .tag-pill {{
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 700;
        }}
        .tag-blue {{ background: #dbeafe; color: #1e40af; }}
        .tag-green {{ background: #d1fae5; color: #065f46; }}
        .tag-yellow {{ background: #fef3c7; color: #92400e; }}
        .img-container {{
            margin: 20px 0;
            text-align: center;
            background: #fafafa;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .img-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }}
        .rec-box {{
            background: #f0fdf4;
            border-left: 4px solid var(--secondary);
            padding: 16px 20px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 16px;
        }}
        .rec-box h4 {{ color: #065f46; margin-bottom: 6px; font-size: 15px; }}
        .rec-box p {{ font-size: 13.5px; color: #166534; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge">Kanishka Software Technical Assessment</div>
            <h1>Cafeteria Order Data – Quick Analysis & Forecast Challenge</h1>
            <p>End-to-End Big Data Analytics, RFM Customer Intelligence & Machine Learning Order Forecasting (FY 2024–25)</p>
        </header>

        <!-- KPI Cards -->
        <div class="grid-4">
            <div class="kpi-card">
                <div class="kpi-title">Total Orders Analyzed</div>
                <div class="kpi-value">5,961,005</div>
                <div class="kpi-sub">Across 8 Active Branches</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Gross Platform Revenue</div>
                <div class="kpi-value">₹41.11 Cr</div>
                <div class="kpi-sub">₹411,060,742.68 Gross</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Average Order Value (AOV)</div>
                <div class="kpi-value">₹68.96</div>
                <div class="kpi-sub">High Repeat Beverage Frequency</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Forecasting Accuracy (R²)</div>
                <div class="kpi-value">0.8660</div>
                <div class="kpi-sub">LightGBM Model (MAE: 708)</div>
            </div>
        </div>

        <!-- Section 1: Branch Performance -->
        <div class="section-card">
            <div class="section-title">🏢 Branch Performance & Footprint Analysis</div>
            <p>Analysis of 5.96M orders revealed that <strong>Nirlon Knowledge Park</strong> and <strong>Embassy Tech Village</strong> generate <strong>80.95% of total platform volume</strong> and ₹33.96 Crores in revenue.</p>
            
            <div class="img-container">
                <img src="{img_branch}" alt="Branch Performance">
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Branch ID</th>
                        <th>Branch Name</th>
                        <th>Order Volume</th>
                        <th>Gross Revenue (INR)</th>
                        <th>AOV</th>
                        <th>Unique Diners</th>
                        <th>Order Share</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>1</strong></td>
                        <td><strong>Nirlon Knowledge Park</strong></td>
                        <td>2,344,842</td>
                        <td>₹170,224,652.67</td>
                        <td>₹72.60</td>
                        <td>14,442</td>
                        <td><span class="tag-pill tag-blue">39.34%</span></td>
                    </tr>
                    <tr>
                        <td><strong>2</strong></td>
                        <td><strong>Embassy Tech Village</strong></td>
                        <td>2,480,228</td>
                        <td>₹169,386,369.74</td>
                        <td>₹68.29</td>
                        <td>22,223</td>
                        <td><span class="tag-pill tag-blue">41.61%</span></td>
                    </tr>
                    <tr>
                        <td><strong>9</strong></td>
                        <td>Magma</td>
                        <td>653,115</td>
                        <td>₹43,536,038.90</td>
                        <td>₹66.66</td>
                        <td>9,462</td>
                        <td><span class="tag-pill tag-green">10.96%</span></td>
                    </tr>
                    <tr>
                        <td><strong>4</strong></td>
                        <td>Magnus Tower</td>
                        <td>443,902</td>
                        <td>₹25,673,606.00</td>
                        <td>₹57.84</td>
                        <td>4</td>
                        <td><span class="tag-pill tag-yellow">7.45%</span></td>
                    </tr>
                    <tr>
                        <td><strong>10</strong></td>
                        <td>JPMT-Kalina</td>
                        <td>38,477</td>
                        <td>₹2,204,596.37</td>
                        <td>₹57.30</td>
                        <td>667</td>
                        <td>0.65%</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Section 2: Hourly & Weekly Trends -->
        <div class="section-card">
            <div class="section-title">⏰ Operating Dynamics: Peak Rush & Day-of-Week Seasonality</div>
            <p>Orders exhibit a strict corporate rhythm with two major spikes: <strong>Lunch Rush (12:30 – 2:30 PM)</strong> and <strong>Evening Snacks & Chai (4:00 – 6:00 PM)</strong>. Tuesday and Wednesday represent peak demand days.</p>
            
            <div class="img-container">
                <img src="{img_hourly}" alt="Hourly Operating Dynamics">
            </div>
            <div class="img-container">
                <img src="{img_dow}" alt="Weekly Seasonality">
            </div>
        </div>

        <!-- Section 3: Menu & RFM -->
        <div class="section-card">
            <div class="section-title">🍲 Menu Drivers & Customer RFM Segmentation</div>
            <p><strong>Ginger Tea</strong> is the platform's #1 anchor dish with <strong>753,840 cups sold</strong> (₹1.15 Cr revenue). Customer segmentation demonstrates the 80/20 power law: <strong>29.5% of diners (Platinum Champions)</strong> generate <strong>82.22% of revenue</strong>.</p>
            
            <div class="img-container">
                <img src="{img_dishes}" alt="Top Menu Items">
            </div>
            <div class="img-container">
                <img src="{img_rfm}" alt="Customer RFM Pareto">
            </div>
        </div>

        <!-- Section 4: Forecasting Models -->
        <div class="section-card">
            <div class="section-title">🤖 Predictive Order Forecasting & Benchmark Results</div>
            <p>Trained and backtested multiple models on <strong>Branch 1 (Nirlon Knowledge Park)</strong> over the final 28 days of unseen test data.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Model Architecture</th>
                        <th>MAE (Orders)</th>
                        <th>RMSE (Orders)</th>
                        <th>MAPE (%)</th>
                        <th>R² Score</th>
                        <th>Assessment</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background:#eff6ff;">
                        <td>🥇</td>
                        <td><strong>LightGBM Regressor</strong></td>
                        <td><strong>708.05</strong></td>
                        <td><strong>1,529.18</strong></td>
                        <td><strong>20.43%</strong></td>
                        <td><strong>0.8660</strong></td>
                        <td><span class="tag-pill tag-blue">Top Performer (-28.5% MAE)</span></td>
                    </tr>
                    <tr>
                        <td>🥈</td>
                        <td>Hybrid Ensemble (SARIMAX + LightGBM)</td>
                        <td>788.67</td>
                        <td>1,591.22</td>
                        <td>31.98%</td>
                        <td>0.8549</td>
                        <td><span class="tag-pill tag-green">Balanced Variance</span></td>
                    </tr>
                    <tr>
                        <td>🥉</td>
                        <td>XGBoost Regressor</td>
                        <td>834.68</td>
                        <td>1,683.18</td>
                        <td>21.39%</td>
                        <td>0.8377</td>
                        <td>Strong Boosting Baseline</td>
                    </tr>
                    <tr>
                        <td>4</td>
                        <td>SARIMAX (1,1,1)(1,1,1)7</td>
                        <td>965.92</td>
                        <td>1,702.59</td>
                        <td>45.91%</td>
                        <td>0.8339</td>
                        <td>Seasonal Autoregressive</td>
                    </tr>
                    <tr>
                        <td>5</td>
                        <td>Seasonal Baseline (Lag-7)</td>
                        <td>991.11</td>
                        <td>2,150.58</td>
                        <td>26.29%</td>
                        <td>0.7350</td>
                        <td>Naive Seasonal Reference</td>
                    </tr>
                </tbody>
            </table>

            <div class="img-container">
                <img src="{img_backtest}" alt="Backtest Evaluation">
            </div>
            
            <div class="section-title" style="font-size:17px; margin-top:24px;">📅 Next 7 Days Forward Production Forecast (April 1–7, 2025)</div>
            <div class="img-container">
                <img src="{img_forecast}" alt="7-Day Future Forecast">
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Day of Week</th>
                        <th>Forecasted Orders</th>
                        <th>95% Confidence Interval</th>
                        <th>Est. Daily Revenue (INR)</th>
                        <th>Kitchen Planning Strategy</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>2025-04-01</td>
                        <td>Tuesday</td>
                        <td><strong>7,445</strong></td>
                        <td>[4,658 – 10,232]</td>
                        <td>₹540,489.00</td>
                        <td>Full weekday crew; high morning beverage prep</td>
                    </tr>
                    <tr style="background:#f0fdf4;">
                        <td>2025-04-02</td>
                        <td>Wednesday</td>
                        <td><strong>8,597</strong></td>
                        <td>[5,611 – 11,583]</td>
                        <td>₹624,121.41</td>
                        <td><strong>Peak Demand Day:</strong> Double counter staffing at lunch</td>
                    </tr>
                    <tr style="background:#f0fdf4;">
                        <td>2025-04-03</td>
                        <td>Thursday</td>
                        <td><strong>8,864</strong></td>
                        <td>[5,838 – 11,890]</td>
                        <td>₹643,504.97</td>
                        <td><strong>Peak Demand Day:</strong> Maximize meal combo inventory</td>
                    </tr>
                    <tr>
                        <td>2025-04-04</td>
                        <td>Friday</td>
                        <td><strong>7,691</strong></td>
                        <td>[4,651 – 10,731]</td>
                        <td>₹558,348.00</td>
                        <td>High lunch volume; afternoon taper</td>
                    </tr>
                    <tr style="color:#64748b;">
                        <td>2025-04-05</td>
                        <td>Saturday</td>
                        <td><strong>1,132</strong></td>
                        <td>[0 – 4,180]</td>
                        <td>₹82,180.46</td>
                        <td>Skeleton weekend crew (85% reduction)</td>
                    </tr>
                    <tr style="color:#64748b;">
                        <td>2025-04-06</td>
                        <td>Sunday</td>
                        <td><strong>456</strong></td>
                        <td>[0 – 3,511]</td>
                        <td>₹33,104.50</td>
                        <td>Minimal operations; equipment sanitation</td>
                    </tr>
                    <tr>
                        <td>2025-04-07</td>
                        <td>Monday</td>
                        <td><strong>7,557</strong></td>
                        <td>[4,496 – 10,618]</td>
                        <td>₹548,619.93</td>
                        <td>Full workweek restart; morning breakfast surge</td>
                    </tr>
                    <tr style="font-weight:bold; background:#e0f2fe;">
                        <td colspan="2">TOTAL 7-DAY FORECAST</td>
                        <td>41,742 Orders</td>
                        <td>—</td>
                        <td>₹3,030,368.27 (~₹30.3 Lakhs)</td>
                        <td>Weekly Food Supply Procurement Guide</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Section 5: Recommendations -->
        <div class="section-card">
            <div class="section-title">💡 Strategic Business Recommendations</div>
            
            <div class="rec-box">
                <h4>1. Dynamic Staffing & Manpower Redistribution</h4>
                <p>Align kitchen staff shifts dynamically with predicted order spikes (12:00 PM – 2:30 PM and 4:00 PM – 6:00 PM). Reduce weekend staff by 75% to save operating costs while eliminating weekday queue bottlenecks.</p>
            </div>
            <div class="rec-box">
                <h4>2. Express Chai & Beverage Tap-and-Go Counters</h4>
                <p>Since tea and beverages represent over 1.6M annual transactions, segregating them into automated express dispensing stations will reduce main counter waiting times by 30%.</p>
            </div>
            <div class="rec-box">
                <h4>3. Platinum Loyalty & Pre-Order Fast-Pass</h4>
                <p>Introduce corporate meal subscriptions and contactless mobile pickup slots for the top 29.5% Platinum Champions who drive 82.2% of total revenue.</p>
            </div>
            <div class="rec-box">
                <h4>4. Predictive Supply Chain & Raw Material Procurement</h4>
                <p>Feed daily order forecasts directly into dairy, bread, and vegetable procurement orders to eliminate food waste and prevent midday inventory stockouts.</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Interactive Presentation Report generated at: {HTML_PATH}")
