import os
import json
import zipfile
import pandas as pd

from app.db.database import engine
from app.services.schema_detector import detect_foreign_keys

RAW_FOLDER = "data/raw"
EXTRACT_FOLDER = "data/extracted"


# -------------------------
# STEP 1: UNZIP FILES
# -------------------------
def unzip_files():
    os.makedirs(EXTRACT_FOLDER, exist_ok=True)

    for file in os.listdir(RAW_FOLDER):
        if file.endswith(".zip"):
            path = os.path.join(RAW_FOLDER, file)

            print(f"Unzipping {file}...")

            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(EXTRACT_FOLDER)


# -------------------------
# STEP 2: LOAD JSONL FILES
# -------------------------
def load_jsonl_files():
    all_dfs = []

    for root, dirs, files in os.walk(EXTRACT_FOLDER):
        for file in files:
            if not file.endswith(".jsonl"):
                continue

            path = os.path.join(root, file)
            print(f"Loading {file}...")

            data = []
            with open(path, "r") as f:
                for line in f:
                    data.append(json.loads(line))

            df = pd.json_normalize(data)
            df.columns = df.columns.str.lower().str.strip()

            all_dfs.append(df)

    # merge everything into one table
    final_df = pd.concat(all_dfs, ignore_index=True)

    return {"invoices": final_df}


# -------------------------
# STEP 3: CLEAN DATA
# -------------------------
def clean_tables(tables):
    cleaned = {}

    for name, df in tables.items():
        df = df.copy()

        # ---- standard column mapping ----
        if "billingdocument" in df.columns:
            df.rename(columns={"billingdocument": "id"}, inplace=True)

        if "salesdocument" in df.columns:
            df.rename(columns={"salesdocument": "order_id"}, inplace=True)

        if "soldtoparty" in df.columns:
            df.rename(columns={"soldtoparty": "customer_id"}, inplace=True)

        if "accountingdocument" in df.columns:
            df.rename(columns={"accountingdocument": "invoice_id"}, inplace=True)

        # ---- date parsing ----
        for col in df.columns:
            if "date" in col:
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except:
                    pass

        cleaned[name] = df

    return cleaned


# -------------------------
# STEP 4: SAVE TO SQLITE
# -------------------------
def save_to_sqlite(tables):
    for name, df in tables.items():
        print(f"Saving table: {name}")
        df.to_sql(name, engine, if_exists="replace", index=False)


# -------------------------
# STEP 5: SUMMARY
# -------------------------
def print_summary(tables, relationships):
    print("\n===== TABLE SUMMARY =====\n")

    for name, df in tables.items():
        print(f"{name}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print("-" * 50)

    print("\n===== RELATIONSHIPS =====\n")

    for r in relationships:
        print(
            f"{r['from_table']}.{r['from_column']} -> "
            f"{r['to_table']}.{r['to_column']}"
        )


# -------------------------
# MAIN RUNNER
# -------------------------
def run_ingestion():
    print("Step 1: Unzipping...")
    unzip_files()

    print("Step 2: Loading JSONL...")
    tables = load_jsonl_files()

    print("Step 3: Cleaning...")
    tables = clean_tables(tables)

    print("Step 4: Saving to DB...")
    save_to_sqlite(tables)

    print("Step 5: Detecting relationships...")
    relationships = detect_foreign_keys(tables)

    print_summary(tables, relationships)

    print("\nDONE.\n")