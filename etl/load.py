import pandas as pd
import sqlite3
from pathlib import Path

PROCESSED_DATA_PATH = Path("data/processed")
DB_PATH = Path("data/sales_dw.db")

dim_customers = pd.read_csv(PROCESSED_DATA_PATH / "dim_customers.csv")
dim_products = pd.read_csv(PROCESSED_DATA_PATH / "dim_products.csv")
fact_sales = pd.read_csv(PROCESSED_DATA_PATH / "fact_sales.csv")

conn = sqlite3.connect(DB_PATH)

dim_customers.to_sql("dim_customers", conn, if_exists="replace", index=False)
dim_products.to_sql("dim_products", conn, if_exists="replace", index=False)
fact_sales.to_sql("fact_sales", conn, if_exists="replace", index=False)

cursor = conn.cursor()
for table in ["dim_customers", "dim_products", "fact_sales"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cursor.fetchone()[0]} rows")

conn.close()
print("Data successfully loaded into SQLite database.")
