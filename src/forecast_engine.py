import os
import json
import duckdb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import lightgbm as lgb
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "cafeteria.duckdb")
REPORTS_DIR = os.path.join(PROJECT_DIR, "reports")
MODELS_DIR = os.path.join(PROJECT_DIR, "models")
VIS_DIR = os.path.join(PROJECT_DIR, "visualizations")

def calculate_mape(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    non_zero = y_true != 0
    return np.mean(np.abs((y_true[non_zero] - y_pred[non_zero]) / y_true[non_zero])) * 100

def create_features(df, target_col='order_count'):
    df_feat = df.copy()
    df_feat['dayofweek'] = df_feat['order_date'].dt.dayofweek
    df_feat['is_weekend'] = df_feat['dayofweek'].isin([5, 6]).astype(int)
    df_feat['dayofmonth'] = df_feat['order_date'].dt.day
    df_feat['month'] = df_feat['order_date'].dt.month
    df_feat['quarter'] = df_feat['order_date'].dt.quarter
    df_feat['dayofyear'] = df_feat['order_date'].dt.dayofyear
    
    # Lag features
    for lag in [1, 2, 3, 7, 14, 21, 28]:
        df_feat[f'lag_{lag}'] = df_feat[target_col].shift(lag)
        
    # Rolling statistics
    df_feat['rolling_mean_7'] = df_feat[target_col].shift(1).rolling(window=7).mean()
    df_feat['rolling_std_7'] = df_feat[target_col].shift(1).rolling(window=7).std()
    df_feat['rolling_mean_14'] = df_feat[target_col].shift(1).rolling(window=14).mean()
    df_feat['rolling_mean_28'] = df_feat[target_col].shift(1).rolling(window=28).mean()
    
    return df_feat

def run_forecasting(branch_id=1, branch_name="Nirlon Knowledge Park"):
    print(f"=== Running Forecasting Engine for Branch {branch_id} ({branch_name}) ===")
    con = duckdb.connect(DUCKDB_PATH)
    
    # Query daily aggregated orders and revenue for target branch
    query = f"""
    SELECT 
        CAST(order_date AS DATE) AS order_date,
        COUNT(*) AS order_count,
        ROUND(SUM(grand_total), 2) AS daily_revenue,
        COUNT(DISTINCT user_id) AS active_diners,
        ROUND(AVG(grand_total), 2) AS daily_aov
    FROM orders
    WHERE branch_id = {branch_id} AND order_date IS NOT NULL AND order_date >= '2024-04-01' AND order_date <= '2025-04-01'
    GROUP BY CAST(order_date AS DATE)
    ORDER BY order_date
    """
    df_daily = con.execute(query).fetchdf()
    con.close()
    
    df_daily['order_date'] = pd.to_datetime(df_daily['order_date'])
    # Fill any missing dates in range with 0 or interpolation
    idx = pd.date_range(start=df_daily['order_date'].min(), end=df_daily['order_date'].max())
    df_daily = df_daily.set_index('order_date').reindex(idx, fill_value=0).reset_index()
    df_daily.rename(columns={'index': 'order_date'}, inplace=True)
    
    df_daily.to_csv(os.path.join(REPORTS_DIR, f"branch_{branch_id}_daily_history.csv"), index=False)
    print(f"Daily series points: {len(df_daily)} days (from {df_daily['order_date'].min().date()} to {df_daily['order_date'].max().date()})")
    print(f"Average daily orders: {df_daily['order_count'].mean():.1f} | Max daily orders: {df_daily['order_count'].max():,}")

    # Backtesting Split: Train (first N-28 days), Test (last 28 days - 4 weeks)
    test_days = 28
    train_df = df_daily.iloc[:-test_days].copy()
    test_df = df_daily.iloc[-test_days:].copy()
    
    print(f"Train samples: {len(train_df)} days | Test samples: {len(test_df)} days")
    
    # -------------------------------------------------------------
    # MODEL 1: Naive Weekly Seasonal Baseline (Lag-7)
    # -------------------------------------------------------------
    baseline_preds = df_daily['order_count'].shift(7).iloc[-test_days:].values
    mae_base = mean_absolute_error(test_df['order_count'], baseline_preds)
    rmse_base = np.sqrt(mean_squared_error(test_df['order_count'], baseline_preds))
    mape_base = calculate_mape(test_df['order_count'], baseline_preds)
    r2_base = r2_score(test_df['order_count'], baseline_preds)

    # -------------------------------------------------------------
    # MODEL 2: SARIMA Model (p=1, d=1, q=1) x (P=1, D=1, Q=1, s=7)
    # -------------------------------------------------------------
    print("Training SARIMAX model...")
    sarima_model = SARIMAX(
        train_df['order_count'],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False
    )
    sarima_fit = sarima_model.fit(disp=False)
    sarima_test_forecast = sarima_fit.get_forecast(steps=test_days)
    sarima_preds = np.maximum(0, sarima_test_forecast.predicted_mean.values)
    
    mae_sarima = mean_absolute_error(test_df['order_count'], sarima_preds)
    rmse_sarima = np.sqrt(mean_squared_error(test_df['order_count'], sarima_preds))
    mape_sarima = calculate_mape(test_df['order_count'], sarima_preds)
    r2_sarima = r2_score(test_df['order_count'], sarima_preds)

    # -------------------------------------------------------------
    # MODEL 3: LightGBM Regressor with Lag & Calendar Features
    # -------------------------------------------------------------
    print("Training LightGBM Regressor...")
    df_feat = create_features(df_daily, target_col='order_count')
    feature_cols = [c for c in df_feat.columns if c not in ['order_date', 'order_count', 'daily_revenue', 'active_diners', 'daily_aov']]
    
    # Drop rows with NaN due to lags in training
    df_feat_clean = df_feat.dropna(subset=feature_cols)
    train_feat = df_feat_clean[df_feat_clean['order_date'] < test_df['order_date'].min()]
    test_feat = df_feat_clean[df_feat_clean['order_date'] >= test_df['order_date'].min()]
    
    X_train, y_train = train_feat[feature_cols], train_feat['order_count']
    X_test, y_test = test_feat[feature_cols], test_feat['order_count']
    
    lgb_model = lgb.LGBMRegressor(
        n_estimators=150,
        learning_rate=0.04,
        max_depth=5,
        num_leaves=20,
        random_state=42,
        verbosity=-1
    )
    lgb_model.fit(X_train, y_train)
    lgb_preds = np.maximum(0, lgb_model.predict(X_test))
    
    mae_lgb = mean_absolute_error(y_test, lgb_preds)
    rmse_lgb = np.sqrt(mean_squared_error(y_test, lgb_preds))
    mape_lgb = calculate_mape(y_test, lgb_preds)
    r2_lgb = r2_score(y_test, lgb_preds)

    # -------------------------------------------------------------
    # MODEL 4: XGBoost Regressor
    # -------------------------------------------------------------
    print("Training XGBoost Regressor...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=150,
        learning_rate=0.04,
        max_depth=4,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    xgb_preds = np.maximum(0, xgb_model.predict(X_test))
    
    mae_xgb = mean_absolute_error(y_test, xgb_preds)
    rmse_xgb = np.sqrt(mean_squared_error(y_test, xgb_preds))
    mape_xgb = calculate_mape(y_test, xgb_preds)
    r2_xgb = r2_score(y_test, xgb_preds)

    # -------------------------------------------------------------
    # MODEL 5: Hybrid Ensemble (50% SARIMA + 50% LightGBM)
    # -------------------------------------------------------------
    ensemble_preds = 0.5 * sarima_preds + 0.5 * lgb_preds
    mae_ens = mean_absolute_error(test_df['order_count'], ensemble_preds)
    rmse_ens = np.sqrt(mean_squared_error(test_df['order_count'], ensemble_preds))
    mape_ens = calculate_mape(test_df['order_count'], ensemble_preds)
    r2_ens = r2_score(test_df['order_count'], ensemble_preds)

    # Compile Evaluation Table
    model_comparison = pd.DataFrame([
        {'Model': 'Seasonal Baseline (Lag-7)', 'MAE': round(mae_base, 2), 'RMSE': round(rmse_base, 2), 'MAPE (%)': round(mape_base, 2), 'R² Score': round(r2_base, 4)},
        {'Model': 'SARIMAX (1,1,1)(1,1,1)7', 'MAE': round(mae_sarima, 2), 'RMSE': round(rmse_sarima, 2), 'MAPE (%)': round(mape_sarima, 2), 'R² Score': round(r2_sarima, 4)},
        {'Model': 'LightGBM Regressor', 'MAE': round(mae_lgb, 2), 'RMSE': round(rmse_lgb, 2), 'MAPE (%)': round(mape_lgb, 2), 'R² Score': round(r2_lgb, 4)},
        {'Model': 'XGBoost Regressor', 'MAE': round(mae_xgb, 2), 'RMSE': round(rmse_xgb, 2), 'MAPE (%)': round(mape_xgb, 2), 'R² Score': round(r2_xgb, 4)},
        {'Model': 'Ensemble (SARIMAX + LightGBM)', 'MAE': round(mae_ens, 2), 'RMSE': round(rmse_ens, 2), 'MAPE (%)': round(mape_ens, 2), 'R² Score': round(r2_ens, 4)},
    ]).sort_values(by='MAE')

    print("\n=== MODEL BENCHMARK COMPARISON ===")
    print(model_comparison.to_string(index=False))
    model_comparison.to_csv(os.path.join(REPORTS_DIR, "model_benchmark_comparison.csv"), index=False)

    # -------------------------------------------------------------
    # FUTURE 7-DAY FORECAST (April 2, 2025 to April 8, 2025)
    # -------------------------------------------------------------
    print("\n=== Generating Production 7-Day Future Forecast ===")
    # Retrain SARIMAX on full dataset for maximum accuracy
    full_sarima_model = SARIMAX(
        df_daily['order_count'],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 7),
        enforce_stationarity=False,
        enforce_invertibility=False
    ).fit(disp=False)
    
    future_forecast = full_sarima_model.get_forecast(steps=7)
    future_mean = np.maximum(0, np.round(future_forecast.predicted_mean.values))
    future_ci = future_forecast.conf_int(alpha=0.05)
    future_lower = np.maximum(0, np.round(future_ci.iloc[:, 0].values))
    future_upper = np.maximum(0, np.round(future_ci.iloc[:, 1].values))
    
    last_date = df_daily['order_date'].max()
    future_dates = [last_date + timedelta(days=i) for i in range(1, 8)]
    
    avg_aov = df_daily['daily_revenue'].sum() / df_daily['order_count'].sum()
    
    forecast_df = pd.DataFrame({
        'Date': [d.strftime('%Y-%m-%d') for d in future_dates],
        'Day_of_Week': [d.strftime('%A') for d in future_dates],
        'Forecasted_Orders': future_mean.astype(int),
        'Lower_CI_95%': future_lower.astype(int),
        'Upper_CI_95%': future_upper.astype(int),
        'Estimated_Revenue_INR': np.round(future_mean * avg_aov, 2)
    })
    
    print(forecast_df.to_string(index=False))
    forecast_df.to_csv(os.path.join(REPORTS_DIR, "next_7_days_forecast.csv"), index=False)
    
    # Save test backtest predictions for plotting
    backtest_plot_df = pd.DataFrame({
        'order_date': test_df['order_date'].dt.strftime('%Y-%m-%d').values,
        'Actual_Orders': test_df['order_count'].values,
        'SARIMAX': np.round(sarima_preds).astype(int),
        'LightGBM': np.round(lgb_preds).astype(int),
        'Ensemble': np.round(ensemble_preds).astype(int)
    })
    backtest_plot_df.to_csv(os.path.join(REPORTS_DIR, "backtest_predictions.csv"), index=False)
    
    # Save Feature Importance
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'LightGBM_Importance': lgb_model.feature_importances_,
        'XGBoost_Importance': xgb_model.feature_importances_
    }).sort_values(by='LightGBM_Importance', ascending=False)
    importance_df.to_csv(os.path.join(REPORTS_DIR, "feature_importance.csv"), index=False)

    print("\nForecasting completed successfully! Results and metrics saved to reports.")

if __name__ == '__main__':
    run_forecasting(branch_id=1, branch_name="Nirlon Knowledge Park")
