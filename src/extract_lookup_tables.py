import os
import re
import csv
import pandas as pd
import duckdb

ASSIGNMENT_DIR = r"E:\Personal Projects\Kanishka Software Assignment"
SQL_FILE = os.path.join(ASSIGNMENT_DIR, "Cafeteria Order Data.sql")
PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
DATA_DIR = os.path.join(PROJECT_DIR, "data")
DUCKDB_PATH = os.path.join(DATA_DIR, "cafeteria.duckdb")

lookup_tables = ['branches', 'categories', 'counters', 'dishes', 'locations', 'mode_has_payments']

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

data = {t: [] for t in lookup_tables}
current_table = None

def parse_csv_line(line):
    line = line.strip()
    if line.startswith('(') and (line.endswith('),') or line.endswith(');')):
        inner = line[1:-2]
        reader = csv.reader([inner], quotechar="'", escapechar='\\', skipinitialspace=True)
        for r in reader:
            return [None if (v == 'NULL' or v == '' or v == '0000-00-00 00:00:00') else v for v in r]
    return None

with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
    for line_num, line in enumerate(f):
        if line_num > 400000:
            break
        if 'Dumping data for table' in line:
            for t in lookup_tables:
                if f"`{t}`" in line:
                    current_table = t
                    print(f"Found section for {t} at line {line_num}")
                    break
            else:
                current_table = None
        elif current_table:
            if line.startswith('INSERT INTO') or line.startswith('--') or line.startswith('/*') or not line.strip():
                continue
            if line.startswith('UNLOCK TABLES') or line.startswith('LOCK TABLES'):
                current_table = None
                continue
            row = parse_csv_line(line)
            if row:
                cols = lookup_schemas[current_table]
                if len(row) >= len(cols):
                    data[current_table].append(row[:len(cols)])
                else:
                    data[current_table].append(row + [None]*(len(cols)-len(row)))
            if line.rstrip().endswith(';'):
                current_table = None

con = duckdb.connect(DUCKDB_PATH)
for t, rows in data.items():
    print(f"Extracted {len(rows)} rows for {t}")
    if rows:
        cols = lookup_schemas[t]
        df = pd.DataFrame(rows, columns=cols)
        for c in ['id', 'branch_id', 'counter_id', 'category_id', 'company_id']:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce')
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df.to_parquet(os.path.join(DATA_DIR, f"{t}.parquet"), index=False)
        con.execute(f"CREATE OR REPLACE TABLE {t} AS SELECT * FROM df")

# Also register orders and order_details in DuckDB
con.execute(f"CREATE OR REPLACE TABLE orders AS SELECT * FROM read_parquet('{DATA_DIR}/orders_part_*.parquet')")
con.execute(f"CREATE OR REPLACE TABLE order_details AS SELECT * FROM read_parquet('{DATA_DIR}/order_details_part_*.parquet')")
print("DuckDB database tables fully initialized and registered!")
con.close()
