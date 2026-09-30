import os
import re
import csv
import sqlite3
import pandas as pd
import time

ASSIGNMENT_DIR = r"E:\Personal Projects\Kanishka Software Assignment"
SQL_FILE = os.path.join(ASSIGNMENT_DIR, "Cafeteria Order Data.sql")
USERS_SQL = os.path.join(ASSIGNMENT_DIR, "users.sql")
PROJECT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge"
OUTPUT_DB = os.path.join(PROJECT_DIR, "data", "cafeteria.db")
DATA_DIR = os.path.join(PROJECT_DIR, "data")

def extract_tables():
    start_time = time.time()
    conn = sqlite3.connect(OUTPUT_DB)
    cursor = conn.cursor()
    
    print("=== Step 1: Parsing Users from users.sql ===")
    # Extract users schema and data
    users_rows = []
    user_cols = []
    
    with open(USERS_SQL, 'r', encoding='utf-8', errors='ignore') as f:
        in_insert = False
        current_insert = []
        for line in f:
            if line.startswith('INSERT INTO `users`'):
                # Extract column names if present
                match = re.search(r"INSERT INTO `users` \((.*?)\) VALUES", line)
                if match and not user_cols:
                    user_cols = [c.strip(' `') for c in match.group(1).split(',')]
                in_insert = True
                current_insert = [line]
            elif in_insert:
                current_insert.append(line)
                if line.rstrip().endswith(';'):
                    in_insert = False
                    full_text = ''.join(current_insert)
                    # parse values
                    val_matches = re.findall(r"\((.*?)\)(?:,|\;)", full_text, re.DOTALL)
                    for vm in val_matches:
                        try:
                            reader = csv.reader([vm], quotechar="'", escapechar='\\', skipinitialspace=True)
                            for row in reader:
                                row_cleaned = [None if v == 'NULL' or v == '' else v for v in row]
                                users_rows.append(row_cleaned)
                        except Exception:
                            continue
                    current_insert = []

    print(f"Extracted {len(users_rows)} users rows. Columns: {len(user_cols)}")
    if user_cols and users_rows:
        df_users = pd.DataFrame(users_rows, columns=user_cols)
        # Drop password / sensitive hashes if present or keep sanitized
        if 'password' in df_users.columns:
            df_users['password'] = '[PROTECTED]'
        df_users.to_sql('users', conn, if_exists='replace', index=False)
        df_users.to_parquet(os.path.join(DATA_DIR, "users.parquet"), index=False)
        print("Saved users to DB and Parquet.")

    print("\n=== Step 2: Streaming Cafeteria Order Data.sql for lookup tables and orders ===")
    
    # We want tables: branches, counters, categories, dishes, locations, mode_has_payments, orders, order_details
    target_lookup_tables = ['branches', 'counters', 'categories', 'dishes', 'locations', 'mode_has_payments']
    
    table_data = {t: [] for t in target_lookup_tables}
    table_cols = {t: [] for t in target_lookup_tables}
    
    orders_count = 0
    order_details_count = 0
    
    # Stream orders and order_details in batches directly to DB/Parquet to manage memory
    current_table = None
    insert_buffer = []
    
    orders_batch = []
    orders_cols = []
    order_details_batch = []
    order_details_cols = []
    
    # Create tables in SQLite with proper indices
    conn.execute("PRAGMA synchronous = OFF")
    conn.execute("PRAGMA journal_mode = MEMORY")
    
    line_num = 0
    with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line_num += 1
            if line_num % 500000 == 0:
                print(f"Processed {line_num:,} lines... Orders: {orders_count:,} | Order Details: {order_details_count:,} (Elapsed: {time.time()-start_time:.1f}s)")
            
            if line.startswith('INSERT INTO '):
                # Identify table
                match = re.search(r"INSERT INTO `([^`]+)`(?: \((.*?)\))? VALUES", line)
                if match:
                    tname = match.group(1)
                    cols_str = match.group(2)
                    current_table = tname
                    insert_buffer = [line]
                    
                    if tname in target_lookup_tables and not table_cols[tname] and cols_str:
                        table_cols[tname] = [c.strip(' `') for c in cols_str.split(',')]
                    elif tname == 'orders' and not orders_cols and cols_str:
                        orders_cols = [c.strip(' `') for c in cols_str.split(',')]
                    elif tname == 'order_details' and not order_details_cols and cols_str:
                        order_details_cols = [c.strip(' `') for c in cols_str.split(',')]
                else:
                    current_table = None
                    insert_buffer = []
            elif current_table:
                insert_buffer.append(line)
                if line.rstrip().endswith(';'):
                    full_text = ''.join(insert_buffer)
                    val_matches = re.findall(r"\((.*?)\)(?:,|\;)", full_text, re.DOTALL)
                    
                    if current_table in target_lookup_tables:
                        for vm in val_matches:
                            try:
                                reader = csv.reader([vm], quotechar="'", escapechar='\\', skipinitialspace=True)
                                for row in reader:
                                    row_cleaned = [None if v == 'NULL' or v == '' else v for v in row]
                                    table_data[current_table].append(row_cleaned)
                            except Exception:
                                continue
                                
                    elif current_table == 'orders':
                        for vm in val_matches:
                            try:
                                reader = csv.reader([vm], quotechar="'", escapechar='\\', skipinitialspace=True)
                                for row in reader:
                                    row_cleaned = [None if v == 'NULL' or v == '' else v for v in row]
                                    orders_batch.append(row_cleaned)
                                    orders_count += 1
                            except Exception:
                                continue
                        if len(orders_batch) >= 50000:
                            df_o = pd.DataFrame(orders_batch, columns=orders_cols if orders_cols else None)
                            df_o.to_sql('orders', conn, if_exists='append', index=False)
                            orders_batch = []
                            
                    elif current_table == 'order_details':
                        for vm in val_matches:
                            try:
                                reader = csv.reader([vm], quotechar="'", escapechar='\\', skipinitialspace=True)
                                for row in reader:
                                    row_cleaned = [None if v == 'NULL' or v == '' else v for v in row]
                                    order_details_batch.append(row_cleaned)
                                    order_details_count += 1
                            except Exception:
                                continue
                        if len(order_details_batch) >= 50000:
                            df_od = pd.DataFrame(order_details_batch, columns=order_details_cols if order_details_cols else None)
                            df_od.to_sql('order_details', conn, if_exists='append', index=False)
                            order_details_batch = []
                            
                    current_table = None
                    insert_buffer = []
                    
    # Flush remaining
    if orders_batch:
        df_o = pd.DataFrame(orders_batch, columns=orders_cols if orders_cols else None)
        df_o.to_sql('orders', conn, if_exists='append', index=False)
        orders_batch = []
    if order_details_batch:
        df_od = pd.DataFrame(order_details_batch, columns=order_details_cols if order_details_cols else None)
        df_od.to_sql('order_details', conn, if_exists='append', index=False)
        order_details_batch = []
        
    print(f"\nFinal Totals: Orders = {orders_count:,}, Order Details = {order_details_count:,}")
    
    # Save lookup tables
    for tname, rows in table_data.items():
        print(f"Saving lookup table `{tname}` with {len(rows)} rows...")
        if rows:
            cols = table_cols[tname] if table_cols[tname] else None
            df_lookup = pd.DataFrame(rows, columns=cols)
            df_lookup.to_sql(tname, conn, if_exists='replace', index=False)
            df_lookup.to_parquet(os.path.join(DATA_DIR, f"{tname}.parquet"), index=False)
            
    # Create helpful indexes
    print("Creating DB indexes for high-speed queries...")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_branch ON orders(branch_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_id ON orders(id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_details_dish_id ON order_details(dish_id)")
    conn.commit()
    conn.close()
    print(f"Extraction and loading complete in {time.time()-start_time:.1f} seconds!")

if __name__ == "__main__":
    extract_tables()
