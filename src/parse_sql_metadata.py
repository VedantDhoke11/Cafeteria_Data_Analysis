import os
import re
import csv
import sqlite3
import pandas as pd

ASSIGNMENT_DIR = r"E:\Personal Projects\Kanishka Software Assignment"
SQL_FILE = os.path.join(ASSIGNMENT_DIR, "Cafeteria Order Data.sql")
USERS_SQL = os.path.join(ASSIGNMENT_DIR, "users.sql")
OUTPUT_DB = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge\data\cafeteria.db"
OUTPUT_DIR = r"C:\Users\Administrator\.gemini\antigravity-ide\scratch\kanishka_cafeteria_challenge\data"

print("Starting metadata extraction...")
conn = sqlite3.connect(OUTPUT_DB)

def parse_insert_values(sql_text):
    """
    Parses MySQL INSERT statements values tuple into Python list of tuples.
    Handles strings with escaped quotes, NULLs, numbers.
    """
    rows = []
    # Find all tuples inside VALUES (...)
    # A robust regex or state machine parser
    pattern = re.compile(r"\((.*?)\)(?:,|;)", re.DOTALL)
    for match in pattern.finditer(sql_text):
        val_str = match.group(1)
        # Parse CSV format handling quotes and escapes
        reader = csv.reader([val_str], quotechar="'", escapechar='\\', skipinitialspace=True)
        try:
            for r in reader:
                row = [None if v == 'NULL' or v == '' else v for v in r]
                rows.append(row)
        except Exception:
            continue
    return rows

print("Parser ready.")
