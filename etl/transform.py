import pandas as pd
from pathlib import Path

Raw_Data_Path = Path("data/raw")
Proccessed_Data_Path = Path("data/processed")

Proccessed_Data_Path.mkdir(parents=True, exist_ok=True)

#Load Raw Data from Raw_Data_Path
customers = pd.read_csv(Raw_Data_Path/"customer.csv")
products = pd.read_csv(Raw_Data_Path/"product.csv")
orders = pd.read_csv(Raw_Data_Path/"order.csv")

#Data Type Casting
customers["signup_date"] = pd.to_datetime(customers["signup_date"])
orders["order_date"] = pd.to_datetime(orders['order_date'])
orders["quantity"] = orders["quantity"].astype(int)
orders["order_amount"] = orders["order_amount"].astype(float)
products["price"] = products["price"].astype(float)

#Data Quality checks 
assert customers["customer_id"].is_unique, "Dupliacte Customer Id Found"
assert products["product_id"].is_unique,"Dupliacte Product Id Found"
assert orders["order_id"].is_unique,"Duplicate Order Id Found"

assert orders["quantity"].min()>0,"Invalid Qunatity Detected"
assert orders["order_amount"].min()>=0 , "Invaid Order Amount Detected"

#create Dimension Table
dim_customer = customers.copy()
dim_products = products.copy()

# Fact Table
fact_sales = orders.merge(dim_customer[["customer_id"]],on="customer_id",how = "left").merge(dim_products[["product_id"]],on= "product_id",how = "left")
fact_sales["order_year"] = fact_sales["order_date"].dt.year
fact_sales["order_month"] = fact_sales["order_date"].dt.month

#Final Column Section(Star Schema)
fact_sales= fact_sales[[
    "order_id","order_date","order_year","order_month","customer_id","product_id","quantity","order_amount"
]]

#Save Proccessed output

dim_customer.to_csv(Proccessed_Data_Path/"dim_customers.csv",index= False)
dim_products.to_csv(Proccessed_Data_Path/"dim_products.csv",index= False)
fact_sales.to_csv(Proccessed_Data_Path/"fact_sales.csv",index = False)

print("Transformation Complete")
print(f"Customers : {dim_customer.shape}")
print(f"Products : {dim_products.shape}")
print(f"Fact_Sales : {fact_sales.shape}")