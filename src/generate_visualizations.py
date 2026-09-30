import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
VIS_DIR = os.path.join(PROJECT_DIR, "visualizations")
os.makedirs(VIS_DIR, exist_ok=True)

# Set high aesthetic styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Segoe UI, Helvetica, Arial, sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#f1f5f9'
plt.rcParams['grid.linestyle'] = '--'

PALETTE = ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

def plot_branch_performance():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "branch_performance.csv"))
    df = df[df['branch_id'] > 0].sort_values(by='total_revenue', ascending=True)
    
    fig, ax1 = plt.subplots(figsize=(12, 6), dpi=300)
    
    y_pos = np.arange(len(df))
    bars = ax1.barh(y_pos, df['total_revenue'] / 1e7, color='#2563eb', alpha=0.85, label='Gross Revenue (Cr ₹)', height=0.55)
    
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(df['branch_name'], fontsize=11, fontweight='bold', color='#1e293b')
    ax1.set_xlabel('Total Revenue (in ₹ Crores)', fontsize=12, fontweight='bold', color='#1e293b')
    ax1.set_title('Branch Performance: Revenue & Order Volume Distribution (FY 2024-25)', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    
    # Add data labels
    for bar, (_, row) in zip(bars, df.iterrows()):
        rev_cr = row['total_revenue'] / 1e7
        orders_k = row['order_volume'] / 1e3
        ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, 
                 f"₹{rev_cr:.2f} Cr ({orders_k:.0f}k orders | AOV ₹{row['aov']:.0f})", 
                 va='center', fontsize=9.5, fontweight='600', color='#334155')
                 
    ax1.set_xlim(0, max(df['total_revenue']/1e7) * 1.35)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "branch_revenue_and_volume.png"), dpi=300)
    plt.close()
    print("Saved branch_revenue_and_volume.png")

def plot_hourly_dynamics():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "hourly_trends.csv"))
    
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    bars = ax.bar(df['order_hour'], df['total_orders'] / 1000, color='#3b82f6', width=0.7, edgecolor='#1d4ed8', alpha=0.85)
    
    # Highlight peaks
    for bar, hour in zip(bars, df['order_hour']):
        if hour in [9, 10, 13, 14, 16, 17]:
            bar.set_color('#1d4ed8')
            
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, fontsize=10)
    ax.set_xlabel('Hour of Day (24-Hour Clock)', fontsize=12, fontweight='bold', color='#1e293b')
    ax.set_ylabel('Total Orders (in Thousands)', fontsize=12, fontweight='bold', color='#1e293b')
    ax.set_title('Peak Operating Hours & Rush Periods Across Cafeterias', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    
    # Peak annotations
    max_row = df.loc[df['total_orders'].idxmax()]
    ax.annotate(f'Peak Lunch Rush\n({max_row["total_orders"]/1e3:.0f}k orders)', 
                xy=(max_row['order_hour'], max_row['total_orders']/1000), 
                xytext=(max_row['order_hour']+1.5, max_row['total_orders']/1000 + 40),
                arrowprops=dict(facecolor='#ef4444', shrink=0.08, width=1.5, headwidth=6),
                fontsize=10, fontweight='bold', color='#b91c1c')

    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "hourly_operating_dynamics.png"), dpi=300)
    plt.close()
    print("Saved hourly_operating_dynamics.png")

def plot_day_of_week():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "day_of_week_trends.csv"))
    # Order: Monday to Sunday
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    df = df.sort_values('day_of_week')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    
    colors = ['#2563eb', '#2563eb', '#2563eb', '#2563eb', '#2563eb', '#94a3b8', '#94a3b8']
    
    # Orders
    ax1.bar(df['day_of_week'], df['total_orders'] / 1e3, color=colors, alpha=0.85, edgecolor='#1e293b', width=0.6)
    ax1.set_title('Total Order Volume by Day of Week', fontsize=12, fontweight='bold', color='#0f172a')
    ax1.set_ylabel('Orders (Thousands)', fontsize=11, fontweight='bold')
    ax1.tick_params(axis='x', rotation=30)
    for i, v in enumerate(df['total_orders'] / 1e3):
        ax1.text(i, v + 20, f"{v:.0f}k", ha='center', fontsize=9.5, fontweight='bold')
        
    # Revenue
    ax2.bar(df['day_of_week'], df['total_revenue'] / 1e7, color='#10b981', alpha=0.85, edgecolor='#047857', width=0.6)
    ax2.set_title('Total Revenue by Day of Week (₹ Crores)', fontsize=12, fontweight='bold', color='#0f172a')
    ax2.set_ylabel('Revenue (₹ Cr)', fontsize=11, fontweight='bold')
    ax2.tick_params(axis='x', rotation=30)
    for i, v in enumerate(df['total_revenue'] / 1e7):
        ax2.text(i, v + 1.5, f"₹{v:.1f} Cr", ha='center', fontsize=9.5, fontweight='bold')
        
    plt.suptitle('Weekly Seasonality: Corporate Tech Park Dynamic (Weekday Peak vs Weekend Dip)', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "day_of_week_seasonality.png"), dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved day_of_week_seasonality.png")

def plot_top_dishes():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "top_selling_dishes.csv")).head(12)
    df = df.sort_values(by='total_quantity_sold', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
    bars = ax.barh(df['dish_name'], df['total_quantity_sold'] / 1e3, color='#0ea5e9', alpha=0.88, height=0.6)
    
    ax.set_xlabel('Total Quantity Sold (in Thousands of Units)', fontsize=12, fontweight='bold', color='#1e293b')
    ax.set_title('Top 12 Best-Selling Menu Items by Volume & Revenue (FY 2024-25)', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    
    for bar, (_, row) in zip(bars, df.iterrows()):
        qty_k = row['total_quantity_sold'] / 1e3
        rev_lakh = (row['total_quantity_sold'] * row['avg_unit_price']) / 1e5
        ax.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2, 
                f"{qty_k:.0f}k units | ₹{rev_lakh:.1f} Lakhs (Avg ₹{row['avg_unit_price']:.0f})", 
                va='center', fontsize=9.5, fontweight='600', color='#334155')
                
    ax.set_xlim(0, max(df['total_quantity_sold']/1e3) * 1.35)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "top_selling_menu_items.png"), dpi=300)
    plt.close()
    print("Saved top_selling_menu_items.png")

def plot_rfm_pareto():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "customer_rfm_segments.csv"))
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    
    # Donut of customer count
    ax1.pie(df['customer_count'], labels=df['customer_tier'], autopct='%1.1f%%', startangle=140, 
            colors=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1'],
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2))
    ax1.set_title('Customer Base Breakdown by Tier\n(Total: 45,049 Diners)', fontsize=12, fontweight='bold')
    
    # Donut of Revenue Contribution
    ax2.pie(df['total_spend'], labels=df['customer_tier'], autopct='%1.1f%%', startangle=140, 
            colors=['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#cbd5e1'],
            wedgeprops=dict(width=0.4, edgecolor='w', linewidth=2))
    ax2.set_title('Revenue Contribution by Tier\n(Total: ₹41.1 Crores)', fontsize=12, fontweight='bold')
    
    plt.suptitle('Customer RFM Segmentation: The 80/20 Power Law (Platinum Champions Drive 82.2% Revenue)', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "customer_rfm_pareto_analysis.png"), dpi=300)
    plt.close()
    print("Saved customer_rfm_pareto_analysis.png")

def plot_forecast_backtest():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "backtest_predictions.csv"))
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)
    
    ax.plot(df['order_date'], df['Actual_Orders'], label='Actual Daily Orders', color='#0f172a', linewidth=2.5, marker='o', markersize=4)
    ax.plot(df['order_date'], df['LightGBM'], label='LightGBM Regressor (R² = 0.866)', color='#2563eb', linewidth=2, linestyle='--', marker='s', markersize=3.5)
    ax.plot(df['order_date'], df['SARIMAX'], label='SARIMAX (1,1,1)(1,1,1)7 (R² = 0.834)', color='#10b981', linewidth=1.8, linestyle=':', marker='^', markersize=3.5)
    ax.plot(df['order_date'], df['Ensemble'], label='Ensemble Model (R² = 0.855)', color='#f59e0b', linewidth=1.8, linestyle='-.')
    
    ax.set_title('Out-of-Sample Model Backtest Evaluation: Actual vs. Forecasted Daily Orders (Last 28 Days)', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    ax.set_ylabel('Daily Order Volume', fontsize=12, fontweight='bold')
    ax.set_xlabel('Date (March 2025 Test Window)', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', frameon=True, fontsize=10.5)
    
    # Format x axis dates
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "forecasting_backtest_evaluation.png"), dpi=300)
    plt.close()
    print("Saved forecasting_backtest_evaluation.png")

def plot_future_forecast():
    df_hist = pd.read_csv(os.path.join(REPORTS_DIR, "branch_1_daily_history.csv")).tail(21)
    df_fc = pd.read_csv(os.path.join(REPORTS_DIR, "next_7_days_forecast.csv"))
    
    df_hist['order_date'] = pd.to_datetime(df_hist['order_date'])
    df_fc['Date'] = pd.to_datetime(df_fc['Date'])
    
    fig, ax = plt.subplots(figsize=(14, 6), dpi=300)
    
    # Plot recent history
    ax.plot(df_hist['order_date'], df_hist['order_count'], label='Historical Orders (Past 3 Weeks)', color='#475569', linewidth=2.2, marker='o', markersize=4)
    
    # Plot future forecast
    ax.plot(df_fc['Date'], df_fc['Forecasted_Orders'], label='7-Day Future Forecast (LightGBM/SARIMAX)', color='#2563eb', linewidth=3, marker='D', markersize=6)
    ax.fill_between(df_fc['Date'], df_fc['Lower_CI_95%'], df_fc['Upper_CI_95%'], color='#93c5fd', alpha=0.35, label='95% Prediction Interval')
    
    # Annotate forecast values
    for _, row in df_fc.iterrows():
        ax.annotate(f"{row['Forecasted_Orders']:,}\n({row['Day_of_Week'][:3]})",
                    xy=(row['Date'], row['Forecasted_Orders']),
                    xytext=(0, 12), textcoords='offset points',
                    ha='center', fontsize=9, fontweight='bold', color='#1d4ed8')

    ax.set_title('7-Day Forward Order Forecast for Branch 1 (Nirlon Knowledge Park) [April 1–7, 2025]', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
    ax.set_ylabel('Predicted Daily Order Count', fontsize=12, fontweight='bold')
    ax.set_xlabel('Timeline', fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', frameon=True, fontsize=10.5)
    
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "future_7_day_forecast.png"), dpi=300)
    plt.close()
    print("Saved future_7_day_forecast.png")

def plot_feature_importance():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "feature_importance.csv")).head(10)
    df = df.sort_values(by='LightGBM_Importance', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)
    bars = ax.barh(df['Feature'], df['LightGBM_Importance'], color='#3b82f6', height=0.6, alpha=0.85)
    
    ax.set_xlabel('Feature Importance Score (Split Gain)', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Most Predictive Features for Daily Cafeteria Order Forecasting', fontsize=13, fontweight='bold', pad=12)
    
    for bar in bars:
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{int(bar.get_width())}", va='center', fontsize=9.5, fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "feature_importance_ranking.png"), dpi=300)
    plt.close()
    print("Saved feature_importance_ranking.png")

def plot_monthly_growth():
    df = pd.read_csv(os.path.join(REPORTS_DIR, "monthly_trends.csv"))
    
    fig, ax1 = plt.subplots(figsize=(12, 5.5), dpi=300)
    ax2 = ax1.twinx()
    
    x = range(len(df))
    bars = ax1.bar(x, df['total_orders'] / 1e3, color='#3b82f6', alpha=0.75, width=0.55, label='Monthly Orders (Thousands)')
    line = ax2.plot(x, df['total_revenue'] / 1e7, color='#10b981', linewidth=2.8, marker='o', markersize=6, label='Gross Revenue (₹ Cr)')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['order_month'], rotation=35, fontsize=10)
    ax1.set_ylabel('Orders (Thousands)', fontsize=11, fontweight='bold', color='#1e293b')
    ax2.set_ylabel('Revenue (₹ Crores)', fontsize=11, fontweight='bold', color='#047857')
    ax1.set_title('Monthly Order Volume and Revenue Growth (FY 2024-25)', fontsize=14, fontweight='bold', pad=15)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', frameon=True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(VIS_DIR, "monthly_growth_trend.png"), dpi=300)
    plt.close()
    print("Saved monthly_growth_trend.png")

if __name__ == '__main__':
    plot_branch_performance()
    plot_hourly_dynamics()
    plot_day_of_week()
    plot_top_dishes()
    plot_rfm_pareto()
    plot_forecast_backtest()
    plot_future_forecast()
    plot_feature_importance()
    plot_monthly_growth()
    print("All visualizations generated successfully!")
