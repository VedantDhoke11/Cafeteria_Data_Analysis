import os
import json
import duckdb
import pandas as pd
import numpy as np

PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "cafeteria.duckdb")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")

def run_eda():
    print("Connecting to DuckDB...")
    con = duckdb.connect(DUCKDB_PATH)
    
    insights = {}
    
    # 1. Overall Platform Summary Metrics
    print("Computing Platform Summary Metrics...")
    summary_query = """
    SELECT 
        COUNT(*) AS total_orders,
        COUNT(DISTINCT user_id) AS total_unique_users,
        COUNT(DISTINCT branch_id) AS active_branches,
        SUM(grand_total) AS total_gross_revenue,
        AVG(grand_total) AS average_order_value,
        SUM(CASE WHEN is_refunded = 1 OR order_status = 4 THEN 1 ELSE 0 END) AS total_refunded_orders,
        ROUND(SUM(CASE WHEN is_refunded = 1 OR order_status = 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS refund_rate_pct,
        MIN(order_date) AS earliest_order,
        MAX(order_date) AS latest_order
    FROM orders
    WHERE order_date IS NOT NULL AND grand_total >= 0
    """
    summary_df = con.execute(summary_query).fetchdf()
    insights['platform_summary'] = summary_df.to_dict(orient='records')[0]
    # Format datetime for JSON serialization
    insights['platform_summary']['earliest_order'] = str(insights['platform_summary']['earliest_order'])
    insights['platform_summary']['latest_order'] = str(insights['platform_summary']['latest_order'])
    print("Platform Summary:", insights['platform_summary'])

    # 2. Branch Performance & Ranking
    print("\nAnalyzing Branch Performance...")
    branch_query = """
    SELECT 
        o.branch_id,
        COALESCE(b.name, 'Branch ' || CAST(o.branch_id AS VARCHAR)) AS branch_name,
        COALESCE(b.branch_code, 'N/A') AS branch_code,
        COUNT(o.id) AS order_volume,
        ROUND(SUM(o.grand_total), 2) AS total_revenue,
        ROUND(AVG(o.grand_total), 2) AS aov,
        COUNT(DISTINCT o.user_id) AS unique_customers,
        ROUND(SUM(o.grand_total) / NULLIF(COUNT(DISTINCT o.user_id), 0), 2) AS revenue_per_customer,
        ROUND(COUNT(o.id) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_date IS NOT NULL), 2) AS order_share_pct
    FROM orders o
    LEFT JOIN branches b ON o.branch_id = b.id
    WHERE o.order_date IS NOT NULL
    GROUP BY o.branch_id, b.name, b.branch_code
    ORDER BY total_revenue DESC
    """
    branch_df = con.execute(branch_query).fetchdf()
    branch_df.to_csv(os.path.join(REPORTS_DIR, "branch_performance.csv"), index=False)
    insights['branch_performance'] = branch_df.to_dict(orient='records')

    # 3. Peak Operating Hours & Time-of-Day Dynamics
    print("\nAnalyzing Hourly Dynamics...")
    hourly_query = """
    SELECT 
        EXTRACT(HOUR FROM order_date) AS order_hour,
        COUNT(*) AS total_orders,
        ROUND(SUM(grand_total), 2) AS total_revenue,
        ROUND(AVG(grand_total), 2) AS aov
    FROM orders
    WHERE order_date IS NOT NULL
    GROUP BY EXTRACT(HOUR FROM order_date)
    ORDER BY order_hour
    """
    hourly_df = con.execute(hourly_query).fetchdf()
    hourly_df.to_csv(os.path.join(REPORTS_DIR, "hourly_trends.csv"), index=False)
    insights['hourly_trends'] = hourly_df.to_dict(orient='records')

    # 4. Day of Week Analysis
    print("\nAnalyzing Day-of-Week Patterns...")
    dow_query = """
    SELECT 
        EXTRACT(DOW FROM order_date) AS dow_num,
        CASE EXTRACT(DOW FROM order_date)
            WHEN 0 THEN 'Sunday'
            WHEN 1 THEN 'Monday'
            WHEN 2 THEN 'Tuesday'
            WHEN 3 THEN 'Wednesday'
            WHEN 4 THEN 'Thursday'
            WHEN 5 THEN 'Friday'
            WHEN 6 THEN 'Saturday'
        END AS day_of_week,
        COUNT(*) AS total_orders,
        ROUND(SUM(grand_total), 2) AS total_revenue,
        ROUND(AVG(grand_total), 2) AS aov
    FROM orders
    WHERE order_date IS NOT NULL
    GROUP BY EXTRACT(DOW FROM order_date)
    ORDER BY dow_num
    """
    dow_df = con.execute(dow_query).fetchdf()
    dow_df.to_csv(os.path.join(REPORTS_DIR, "day_of_week_trends.csv"), index=False)
    insights['day_of_week_trends'] = dow_df.to_dict(orient='records')

    # 5. Monthly & Daily Time Series Trends
    print("\nAnalyzing Monthly Growth Trends...")
    monthly_query = """
    SELECT 
        STRFTIME('%Y-%m', order_date) AS order_month,
        COUNT(*) AS total_orders,
        ROUND(SUM(grand_total), 2) AS total_revenue,
        COUNT(DISTINCT user_id) AS active_users,
        ROUND(AVG(grand_total), 2) AS aov
    FROM orders
    WHERE order_date IS NOT NULL
    GROUP BY STRFTIME('%Y-%m', order_date)
    ORDER BY order_month
    """
    monthly_df = con.execute(monthly_query).fetchdf()
    monthly_df.to_csv(os.path.join(REPORTS_DIR, "monthly_trends.csv"), index=False)
    insights['monthly_trends'] = monthly_df.to_dict(orient='records')

    # 6. Payment Modes & Channel Analysis
    print("\nAnalyzing Payment Modes & Channels...")
    payment_query = """
    SELECT 
        COALESCE(mode_of_transaction, 'Unknown') AS payment_mode,
        COUNT(*) AS total_orders,
        ROUND(SUM(grand_total), 2) AS total_revenue,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_date IS NOT NULL), 2) AS order_pct,
        ROUND(AVG(grand_total), 2) AS aov
    FROM orders
    WHERE order_date IS NOT NULL
    GROUP BY mode_of_transaction
    ORDER BY total_orders DESC
    """
    payment_df = con.execute(payment_query).fetchdf()
    payment_df.to_csv(os.path.join(REPORTS_DIR, "payment_modes.csv"), index=False)
    insights['payment_modes'] = payment_df.to_dict(orient='records')

    # Channel (order_through)
    channel_query = """
    SELECT 
        COALESCE(order_through, 'Direct POS') AS order_channel,
        COUNT(*) AS total_orders,
        ROUND(SUM(grand_total), 2) AS total_revenue,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE order_date IS NOT NULL), 2) AS order_pct,
        ROUND(AVG(grand_total), 2) AS aov
    FROM orders
    WHERE order_date IS NOT NULL
    GROUP BY order_through
    ORDER BY total_orders DESC
    """
    channel_df = con.execute(channel_query).fetchdf()
    channel_df.to_csv(os.path.join(REPORTS_DIR, "order_channels.csv"), index=False)
    insights['order_channels'] = channel_df.to_dict(orient='records')

    # 7. Top-Selling Menu Items & Category Performance
    print("\nAnalyzing Menu Items & Categories...")
    top_dishes_query = """
    SELECT 
        od.dish_name,
        COUNT(od.id) AS order_count,
        SUM(od.order_quantity) AS total_quantity_sold,
        ROUND(AVG(od.dish_price), 2) AS avg_unit_price,
        ROUND(SUM(od.order_quantity * od.dish_price), 2) AS estimated_revenue
    FROM order_details od
    WHERE od.dish_name IS NOT NULL AND TRIM(od.dish_name) != ''
    GROUP BY od.dish_name
    ORDER BY total_quantity_sold DESC
    LIMIT 30
    """
    top_dishes_df = con.execute(top_dishes_query).fetchdf()
    top_dishes_df.to_csv(os.path.join(REPORTS_DIR, "top_selling_dishes.csv"), index=False)
    insights['top_selling_dishes'] = top_dishes_df.head(15).to_dict(orient='records')

    # Top Counters
    counter_query = """
    SELECT 
        c.id AS counter_id,
        COALESCE(c.counter_name, 'Counter ' || CAST(od.counter_id AS VARCHAR)) AS counter_name,
        COALESCE(b.name, 'Branch ' || CAST(c.branch_id AS VARCHAR)) AS branch_name,
        COUNT(od.id) AS items_sold,
        ROUND(SUM(od.order_quantity * od.dish_price), 2) AS counter_revenue
    FROM order_details od
    LEFT JOIN counters c ON od.counter_id = c.id
    LEFT JOIN branches b ON c.branch_id = b.id
    WHERE od.counter_id IS NOT NULL
    GROUP BY c.id, c.counter_name, b.name, c.branch_id, od.counter_id
    ORDER BY counter_revenue DESC
    LIMIT 25
    """
    counter_df = con.execute(counter_query).fetchdf()
    counter_df.to_csv(os.path.join(REPORTS_DIR, "top_counters.csv"), index=False)
    insights['top_counters'] = counter_df.head(15).to_dict(orient='records')

    # 8. Customer Behavior & RFM Segmentation
    print("\nAnalyzing Customer Behavior & RFM Segments...")
    rfm_query = """
    WITH customer_stats AS (
        SELECT 
            user_id,
            COUNT(*) AS order_frequency,
            ROUND(SUM(grand_total), 2) AS monetary_spend,
            ROUND(AVG(grand_total), 2) AS aov,
            MIN(order_date) AS first_order,
            MAX(order_date) AS last_order,
            DATE_DIFF('day', MAX(order_date), '2025-04-01'::TIMESTAMP) AS recency_days
        FROM orders
        WHERE user_id IS NOT NULL AND user_id > 0 AND order_date IS NOT NULL
        GROUP BY user_id
    )
    SELECT 
        CASE 
            WHEN order_frequency >= 100 THEN 'Platinum Champions (100+ Orders)'
            WHEN order_frequency >= 40 THEN 'Gold Frequent Diners (40-99 Orders)'
            WHEN order_frequency >= 15 THEN 'Silver Regulars (15-39 Orders)'
            WHEN order_frequency >= 5 THEN 'Bronze Occasional (5-14 Orders)'
            ELSE 'First-Timers / Infrequent (1-4 Orders)'
        END AS customer_tier,
        COUNT(*) AS customer_count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_stats), 2) AS customer_pct,
        SUM(order_frequency) AS total_orders,
        ROUND(SUM(order_frequency) * 100.0 / (SELECT SUM(order_frequency) FROM customer_stats), 2) AS order_contribution_pct,
        ROUND(SUM(monetary_spend), 2) AS total_spend,
        ROUND(SUM(monetary_spend) * 100.0 / (SELECT SUM(monetary_spend) FROM customer_stats), 2) AS revenue_contribution_pct,
        ROUND(AVG(monetary_spend), 2) AS avg_spend_per_user,
        ROUND(AVG(aov), 2) AS avg_aov
    FROM customer_stats
    GROUP BY 1
    ORDER BY total_spend DESC
    """
    rfm_df = con.execute(rfm_query).fetchdf()
    rfm_df.to_csv(os.path.join(REPORTS_DIR, "customer_rfm_segments.csv"), index=False)
    insights['rfm_segments'] = rfm_df.to_dict(orient='records')

    # Save comprehensive summary JSON
    with open(os.path.join(REPORTS_DIR, "eda_insights_summary.json"), 'w') as f:
        json.dump(insights, f, indent=2)

    print("\nEDA processing complete! Summary exported to JSON and CSV.")
    con.close()

if __name__ == '__main__':
    run_eda()
