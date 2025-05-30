import csv
import sqlite3
import os

# --- USER CONFIG ---
CSV_PATH   = "dbs (1).csv"     # source CSV
DB_PATH    = "dbs.db"     # destination SQLite file
TABLE_NAME = "dbs"          # SQLite table name
DELIM      = "/"             # delimiter between codes in column-3
# --------------------

def load_csv(path):
    """Read CSV and expand rows where column-3 contains multiple codes."""
    with open(path, newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        hdr = next(rdr)                 # full header row
        code_hdr, desc_hdr = hdr[2], hdr[3]

        expanded = []
        for row in rdr:
            codes = [c.strip() for c in row[2].split(DELIM) if c.strip()]
            desc  = row[3]
            expanded.extend([[c, desc] for c in codes])   # one row per code
        return (code_hdr, desc_hdr), expanded

def build_db(db_path, table, columns, rows):
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()

    cur.execute(f'DROP TABLE IF EXISTS "{table}"')
    cur.execute(f'''
        CREATE TABLE "{table}" (
            "{columns[0]}" TEXT,
            "{columns[1]}" TEXT
        )
    ''')
    cur.executemany(f'INSERT INTO "{table}" VALUES (?, ?)', rows)
    conn.commit()
    conn.close()
    print(f"{len(rows)} records written to {db_path} in table '{table}'.")

if __name__ == "__main__":
    headers, data_rows = load_csv(CSV_PATH)
    build_db(DB_PATH, TABLE_NAME, headers, data_rows)
