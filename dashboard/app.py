import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys
import subprocess

# ----------------------------------
# Page Config
# ----------------------------------
st.set_page_config(
    page_title="Sales Data Warehouse Dashboard",
    layout="wide"
)

st.title("📊 Sales Data Warehouse Dashboard")

# ----------------------------------
# Helper functions
# ----------------------------------
def section_divider():
    st.markdown("---")

def safe_metric(value):
    return f"{value:,.0f}" if value is not None else "0"

# ----------------------------------
# Resolve base paths (CLOUD SAFE)
# ----------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "sales_dw.db")
LOAD_SCRIPT = os.path.join(BASE_DIR, "etl", "load.py")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------------
# Auto-create DB if missing
# ----------------------------------
if not os.path.exists(DB_PATH):
    subprocess.run(
        [sys.executable, LOAD_SCRIPT],
        check=True
    )

# ----------------------------------
# Database connection
# ----------------------------------
conn = sqlite3.connect(DB_PATH)

# ----------------------------------
# Filter Options
# ----------------------------------
years_df = pd.read_sql(
    "SELECT DISTINCT order_year FROM fact_sales ORDER BY order_year",
    conn
)

months_df = pd.read_sql(
    "SELECT DISTINCT order_month FROM fact_sales ORDER BY order_month",
    conn
)

available_years = years_df["order_year"].tolist()
available_months = months_df["order_month"].tolist()

# ----------------------------------
# Sidebar Filters
# ----------------------------------
st.sidebar.header("🔍 Filters")
st.sidebar.markdown(
    "Use the filters below to explore sales performance by time period."
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    options=["All"] + available_years
)

selected_month = st.sidebar.selectbox(
    "Select Month",
    options=["All"] + available_months
)

# ----------------------------------
# Build Dynamic WHERE clause
# ----------------------------------
where_conditions = []

if selected_year != "All":
    where_conditions.append(f"order_year = {selected_year}")

if selected_month != "All":
    where_conditions.append(f"order_month = {selected_month}")

where_clause = ""
if where_conditions:
    where_clause = " WHERE " + " AND ".join(where_conditions)

# ----------------------------------
# KPI Calculations
# ----------------------------------
total_revenue = pd.read_sql(
    f"SELECT SUM(order_amount) AS revenue FROM fact_sales {where_clause}",
    conn
).iloc[0, 0]

total_orders = pd.read_sql(
    f"SELECT COUNT(*) AS orders FROM fact_sales {where_clause}",
    conn
).iloc[0, 0]

total_customers = pd.read_sql(
    f"""
    SELECT COUNT(DISTINCT customer_id) AS customers
    FROM fact_sales
    {where_clause}
    """,
    conn
).iloc[0, 0]

avg_order_value = pd.read_sql(
    f"SELECT AVG(order_amount) AS aov FROM fact_sales {where_clause}",
    conn
).iloc[0, 0]

# ----------------------------------
# KPI Layout
# ----------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Total Revenue", safe_metric(total_revenue))

with col2:
    st.metric("📦 Total Orders", safe_metric(total_orders))

with col3:
    st.metric("👥 Total Customers", safe_metric(total_customers))

with col4:
    st.metric("📊 Avg Order Value", safe_metric(avg_order_value))

# ----------------------------------
# Monthly Revenue Trend
# ----------------------------------
section_divider()
st.subheader("📈 Monthly Revenue Trend")

monthly_revenue_df = pd.read_sql(
    f"""
    SELECT
        order_year,
        order_month,
        SUM(order_amount) AS revenue
    FROM fact_sales
    {where_clause}
    GROUP BY order_year, order_month
    ORDER BY order_year, order_month
    """,
    conn
)

monthly_revenue_df["year_month"] = (
    monthly_revenue_df["order_year"].astype(str)
    + "-"
    + monthly_revenue_df["order_month"].astype(str).str.zfill(2)
)

fig_monthly = px.line(
    monthly_revenue_df,
    x="year_month",
    y="revenue",
    markers=True,
    title="Monthly Revenue Trend"
)

fig_monthly.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Year-Month",
    yaxis_title="Revenue"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# ----------------------------------
# Top Products by Revenue
# ----------------------------------
section_divider()
st.subheader("🏆 Top Products by Revenue")

product_revenue_df = pd.read_sql(
    f"""
    SELECT
        p.product_name,
        SUM(f.order_amount) AS revenue
    FROM fact_sales f
    JOIN dim_products p
        ON f.product_id = p.product_id
    {where_clause}
    GROUP BY p.product_name
    ORDER BY revenue DESC
    """,
    conn
)

fig_products = px.bar(
    product_revenue_df,
    x="product_name",
    y="revenue",
    text_auto=".2s",
    title="Revenue by Product"
)

fig_products.update_layout(
    height=400,
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis_title="Product",
    yaxis_title="Revenue",
    xaxis_tickangle=-30
)

st.plotly_chart(fig_products, use_container_width=True)

# ----------------------------------
# Customer Spend Analysis
# ----------------------------------
section_divider()
st.subheader("👥 Customer Spend Analysis")

customer_spend_df = pd.read_sql(
    f"""
    SELECT
        c.customer_name,
        SUM(f.order_amount) AS total_spent,
        COUNT(f.order_id) AS total_orders
    FROM fact_sales f
    JOIN dim_customers c
        ON f.customer_id = c.customer_id
    {where_clause}
    GROUP BY c.customer_name
    ORDER BY total_spent DESC
    """,
    conn
)

col_table, col_chart = st.columns([1, 2])

with col_table:
    st.dataframe(
        customer_spend_df,
        hide_index=True,
        use_container_width=True,
        height=400
    )

with col_chart:
    fig_customers = px.bar(
        customer_spend_df,
        x="customer_name",
        y="total_spent",
        text_auto=".2s",
        title="Total Spend by Customer"
    )

    fig_customers.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis_title="Customer",
        yaxis_title="Total Spend",
        xaxis_tickangle=-30
    )

    st.plotly_chart(fig_customers, use_container_width=True)

# ----------------------------------
# Close DB
# ----------------------------------
conn.close()
