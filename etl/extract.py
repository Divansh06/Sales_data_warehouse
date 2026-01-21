import pandas as pd
from pathlib import Path

Raw_Data_Path = Path("data/raw")
Files = {"customers":"customer.csv","products":"product.csv","orders":"order.csv"}

Expected_Columns = {
    "customers":["customer_id","customer_name","email","city","state", "signup_date"],
    "products": ["product_id", "product_name", "category", "price"],
    "orders": ["order_id", "order_date", "customer_id", "product_id", "quantity", "order_amount"]
}
def load_csv(file_key:str)-> pd.DataFrame:
    file_path = Raw_Data_Path /Files[file_key]

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found")
    
    df = pd.read_csv(file_path)

    expected_columns = Expected_Columns[file_key]
    if list(df.columns) != expected_columns:
        raise ValueError("f scehema mismatch in {file key}.",f"Expected  {expected_columns}, got {list(df.columns)}")
    print(f"Loaded{file_key}: {df.shape[0]} rows")
    return df

if __name__ == "__main__":
    customers_df = load_csv("customers")
    products_df= load_csv("products")
    orders_df = load_csv("orders")

    print("All Row Data Loaded Successfully")