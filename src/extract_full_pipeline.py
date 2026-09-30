import os
import re
import csv
import sqlite3
import pandas as pd
import duckdb
import time

ASSIGNMENT_DIR = r"E:\Personal Projects\Kanishka Software Assignment"
SQL_FILE = os.path.join(ASSIGNMENT_DIR, "Cafeteria Order Data.sql")
USERS_SQL = os.path.join(ASSIGNMENT_DIR, "users.sql")
PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "cafeteria.duckdb")

def parse_csv_line(line):
    line = line.strip()
    if line.startswith('(') and (line.endswith('),') or line.endswith(');')):
        inner = line[1:-2] if line.endswith('),') else line[1:-2]
        reader = csv.reader([inner], quotechar="'", escapechar='\\', skipinitialspace=True)
        for r in reader:
            return [None if (v == 'NULL' or v == '' or v == '0000-00-00 00:00:00') else v for v in r]
    return None

def run_extraction():
    start_total = time.time()
    os.makedirs(DATA_DIR, exist_ok=True)
    con = duckdb.connect(DUCKDB_PATH)
    
    print("=== Phase 1: Extract Users ===")
    user_rows = []
    user_cols = []
    with open(USERS_SQL, 'r', encoding='utf-8', errors='ignore') as f:
        in_users = False
        for line in f:
            if line.startswith('INSERT INTO `users`'):
                in_users = True
                m = re.search(r"INSERT INTO `users` \((.*?)\) VALUES", line)
                if m and not user_cols:
                    user_cols = [c.strip(' `') for c in m.group(1).split(',')]
            elif in_users:
                if line.startswith('--') or line.startswith('/*') or line.startswith('ALTER TABLE') or line.startswith('COMMIT'):
                    in_users = False
                    continue
                row = parse_csv_line(line)
                if row:
                    user_rows.append(row)
                if line.rstrip().endswith(';'):
                    in_users = False
    
    print(f"Loaded {len(user_rows)} users.")
    if user_rows and user_cols:
        df_users = pd.DataFrame(user_rows, columns=user_cols)
        # Drop or hash sensitive columns
        for col in ['password', 'remember_token', 'fcm_code', 'otp']:
            if col in df_users.columns:
                df_users.drop(columns=[col], inplace=True)
        df_users.to_parquet(os.path.join(DATA_DIR, "users.parquet"), index=False)
        con.execute("CREATE OR REPLACE TABLE users AS SELECT * FROM df_users")
        print("Users saved successfully.")

    print("\n=== Phase 2: Extract Lookup Tables from Cafeteria Order Data.sql ===")
    
    # Table names and target line regions
    lookup_tables = {
        'branches': (14454, 15000),
        'categories': (53320, 54000),
        'counters': (134271, 134500),
        'dishes': (134943, 146654),
        'locations': (273187, 273240),
        'mode_has_payments': (288979, 289010)
    }
    
    lookup_data = {t: [] for t in lookup_tables}
    lookup_cols = {t: [] for t in lookup_tables}
    
    # Define exact schema for dishes, branches, categories, counters, locations
    branches_cols = ['id', 'name', 'branch_code', 'branch_merchant_code', 'branch_manager', 'invoice_prefix', 'contact_number', 'is_active', 'company_has_region_id', 'company_id', 'location_id', 'created_at', 'updated_at']
    categories_cols = ['id', 'category_name', 'images', 'branch_id', 'counter_id', 'discount_ids', 'category_type', 'is_active', 'created_at', 'updated_at']
    counters_cols = ['id', 'counter_name', 'counter_number', 'counter_address', 'image', 'license_no', 'tax_no', 'license_expiry_date', 'branch_id', 'area_id', 'discount_ids', 'template_ids', 'vendor_id', 'app_vendor_id', 'priority', 'todays_paragraph', 'todays_favorites', 'isDigitalDashboard', 'created_at', 'updated_at']
    dishes_cols = ['id', 'dish_name', 'price', 'dish_code', 'image', 'is_customizable', 'is_active', 'is_recommended', 'extra_ids', 'counter_id', 'category_id', 'branch_id', 'preparation_time', 'calories', 'food_type', 'is_popular', 'rank', 'user_type', 'created_by', 'edited_by', 'is_extra', 'is_addon', 'is_spice', 'is_sweet', 'created_at', 'updated_at']
    locations_cols = ['id', 'name', 'address', 'state_id', 'city_id', 'pincode', 'edited_at', 'edited_by', 'vip_percent', 'vvip_percent', 'license_name', 'license_format', 'branch_id', 'country_id', 'discount_ids', 'lat', 'long', 'contact_person', 'contact_person_no', 'is_active', 'created_at', 'updated_at']
    modes_cols = ['id', 'mode_name', 'pc_id', 'created_at', 'updated_at']

    lookup_schemas = {
        'branches': branches_cols,
        'categories': categories_cols,
        'counters': counters_cols,
        'dishes': dishes_cols,
        'locations': locations_cols,
        'mode_has_payments': modes_cols
    }

    current_table = None
    with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f):
            if line_num > 300000:
                break
            if line.startswith('-- Dumping data for table `'):
                m = re.search(r"-- Dumping data for table `([^`]+)`", line)
                if m and m.group(1) in lookup_tables:
                    current_table = m.group(1)
                else:
                    current_table = None
            elif current_table:
                if line.startswith('INSERT INTO'):
                    continue
                if line.startswith('--') or line.startswith('/*') or line.startswith('UNLOCK TABLES;'):
                    current_table = None
                    continue
                row = parse_csv_line(line)
                if row:
                    cols = lookup_schemas[current_table]
                    if len(row) >= len(cols):
                        lookup_data[current_table].append(row[:len(cols)])
                    else:
                        lookup_data[current_table].append(row + [None]*(len(cols)-len(row)))
                if line.rstrip().endswith(';'):
                    current_table = None

    for tname, rows in lookup_data.items():
        cols = lookup_schemas[tname]
        df = pd.DataFrame(rows, columns=cols)
        # Convert IDs to numeric where appropriate
        for c in ['id', 'branch_id', 'counter_id', 'category_id', 'company_id']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df.to_parquet(os.path.join(DATA_DIR, f"{tname}.parquet"), index=False)
        con.execute(f"CREATE OR REPLACE TABLE {tname} AS SELECT * FROM df")
        print(f"Saved lookup table `{tname}`: {len(df)} rows.")

    print("\n=== Phase 3: Extract Orders Stream (Lines 552,795 to 6,701,165) ===")
    
    # orders table columns
    orders_cols_all = [
        'id', 'order_number', 'user_id', 'order_status', 'status_update_time', 'cd_status', 
        'order_date', 'device_no', 'branch_id', 'branch_merchant_code', 'counter_id', 
        'category_id', 'order_through', 'sub_total', 'tax_amount', 'tax_percent', 
        'discount_name', 'discount_type', 'discount_amount', 'mode_of_transaction', 
        'payment_timestamp', 'order_prepared_by', 'order_closed_by', 'order_closed_type', 
        'order_closed_time', 'order_cancel_reason', 'order_cancel_by', 'order_cancel_at', 
        'grand_total', 'invoice_number', 'paid_or_cancel', 'refund_through', 'instruction', 
        'transaction_id', 'received_transaction_id', 'transaction_data', 'day_closure_report_no', 
        'day_closure_created_by', 'day_closure_created_time', 'received_amount', 'returned_amount', 
        'refunded_amount', 'table_id', 'table_info', 'reward_points', 'reward_amount', 
        'is_refunded', 'is_preorder', 'preorder_time', 'json_data', 'IST_timezone', 
        'order_create_time', 'created_at', 'updated_at'
    ]
    
    # Select most vital analytical columns to optimize memory & query speed
    keep_indices = [0, 1, 2, 3, 6, 7, 8, 10, 12, 13, 14, 18, 19, 28, 46, 47]
    keep_cols = [
        'id', 'order_number', 'user_id', 'order_status', 'order_date', 'device_no', 
        'branch_id', 'counter_id', 'order_through', 'sub_total', 'tax_amount', 
        'discount_amount', 'mode_of_transaction', 'grand_total', 'is_refunded', 'is_preorder'
    ]
    
    orders_batch = []
    chunk_idx = 0
    total_orders_extracted = 0
    t0 = time.time()
    
    with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f):
            if line_num < 552794:
                continue
            if line_num >= 6701166:
                break
            
            if line.startswith('INSERT INTO') or line.startswith('--') or line.startswith('/*'):
                continue
                
            row = parse_csv_line(line)
            if row and len(row) >= 29:
                try:
                    selected = [row[i] if i < len(row) else None for i in keep_indices]
                    orders_batch.append(selected)
                    total_orders_extracted += 1
                except Exception:
                    continue
                    
            if len(orders_batch) >= 100000:
                chunk_idx += 1
                df_chunk = pd.DataFrame(orders_batch, columns=keep_cols)
                # Parse numeric types
                for num_col in ['id', 'user_id', 'order_status', 'branch_id', 'counter_id', 'sub_total', 'tax_amount', 'discount_amount', 'grand_total', 'is_refunded', 'is_preorder']:
                    df_chunk[num_col] = pd.to_numeric(df_chunk[num_col], errors='coerce')
                df_chunk['order_date'] = pd.to_datetime(df_chunk['order_date'], errors='coerce')
                
                chunk_file = os.path.join(DATA_DIR, f"orders_part_{chunk_idx:03d}.parquet")
                df_chunk.to_parquet(chunk_file, index=False)
                orders_batch = []
                print(f"Extracted {total_orders_extracted:,} orders -> part {chunk_idx:03d} ({time.time()-t0:.1f}s)")
                
    if orders_batch:
        chunk_idx += 1
        df_chunk = pd.DataFrame(orders_batch, columns=keep_cols)
        for num_col in ['id', 'user_id', 'order_status', 'branch_id', 'counter_id', 'sub_total', 'tax_amount', 'discount_amount', 'grand_total', 'is_refunded', 'is_preorder']:
            df_chunk[num_col] = pd.to_numeric(df_chunk[num_col], errors='coerce')
        df_chunk['order_date'] = pd.to_datetime(df_chunk['order_date'], errors='coerce')
        chunk_file = os.path.join(DATA_DIR, f"orders_part_{chunk_idx:03d}.parquet")
        df_chunk.to_parquet(chunk_file, index=False)
        orders_batch = []
        print(f"Extracted {total_orders_extracted:,} orders -> part {chunk_idx:03d}")

    print(f"Total orders extracted: {total_orders_extracted:,}")
    # Register views in DuckDB
    con.execute(f"CREATE OR REPLACE TABLE orders AS SELECT * FROM read_parquet('{DATA_DIR}/orders_part_*.parquet')")
    print("Orders table registered in DuckDB.")

    print("\n=== Phase 4: Extract Order Details Stream (Lines 6,701,168 to 14,162,333) ===")
    od_keep_indices = [0, 1, 2, 9, 10, 11, 15, 17, 18]
    od_keep_cols = ['id', 'order_id', 'dish_id', 'dish_name', 'order_quantity', 'order_status', 'dish_price', 'dish_cal_price', 'counter_id']
    
    od_batch = []
    od_chunk_idx = 0
    total_od_extracted = 0
    t0_od = time.time()
    
    with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f):
            if line_num < 6701171:
                continue
            if line_num >= 14162333:
                break
                
            if line.startswith('INSERT INTO') or line.startswith('--') or line.startswith('/*'):
                continue
                
            row = parse_csv_line(line)
            if row and len(row) >= 19:
                try:
                    selected = [row[i] if i < len(row) else None for i in od_keep_indices]
                    od_batch.append(selected)
                    total_od_extracted += 1
                except Exception:
                    continue
                    
            if len(od_batch) >= 150000:
                od_chunk_idx += 1
                df_od = pd.DataFrame(od_batch, columns=od_keep_cols)
                for num_col in ['id', 'order_id', 'dish_id', 'order_quantity', 'order_status', 'dish_price', 'dish_cal_price', 'counter_id']:
                    df_od[num_col] = pd.to_numeric(df_od[num_col], errors='coerce')
                chunk_file = os.path.join(DATA_DIR, f"order_details_part_{od_chunk_idx:03d}.parquet")
                df_od.to_parquet(chunk_file, index=False)
                od_batch = []
                print(f"Extracted {total_od_extracted:,} order_details -> part {od_chunk_idx:03d} ({time.time()-t0_od:.1f}s)")
                
    if od_batch:
        od_chunk_idx += 1
        df_od = pd.DataFrame(od_batch, columns=od_keep_cols)
        for num_col in ['id', 'order_id', 'dish_id', 'order_quantity', 'order_status', 'dish_price', 'dish_cal_price', 'counter_id']:
            df_od[num_col] = pd.to_numeric(df_od[num_col], errors='coerce')
        chunk_file = os.path.join(DATA_DIR, f"order_details_part_{od_chunk_idx:03d}.parquet")
        df_od.to_parquet(chunk_file, index=False)
        od_batch = []
        print(f"Extracted {total_od_extracted:,} order_details -> part {od_chunk_idx:03d}")

    print(f"Total order_details extracted: {total_od_extracted:,}")
    con.execute(f"CREATE OR REPLACE TABLE order_details AS SELECT * FROM read_parquet('{DATA_DIR}/order_details_part_*.parquet')")
    print("Order details table registered in DuckDB.")
    
    con.close()
    print(f"\n==================================================")
    print(f"🎉 FULL PIPELINE EXTRACTION COMPLETED IN {time.time()-start_total:.1f}s!")
    print(f"==================================================")

if __name__ == '__main__':
    run_extraction()
