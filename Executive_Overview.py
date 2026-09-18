from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="UK Online Retail Intelligence",
    page_icon="📊",
    layout="wide"
)

DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"


@st.cache_data
def load_sales():
    file_path = DATA_DIR / "online_retail_clean_v2.csv"

    return pd.read_csv(
        file_path,
        parse_dates=["InvoiceDate"],
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string"
        },
        low_memory=False
    )


try:
    sales = load_sales()
except FileNotFoundError:
    st.error(
        "online_retail_clean_v2.csv was not found "
        "inside data/processed."
    )
    st.stop()


st.title("UK Online Retail Intelligence")
st.caption(
    "Interactive sales, customer and forecasting analytics"
)

total_revenue = sales["Revenue"].sum()
total_orders = sales["InvoiceNo"].nunique()
total_customers = sales["CustomerID"].nunique()
total_units = sales["Quantity"].sum()
average_order_value = total_revenue / total_orders

column1, column2, column3, column4, column5 = st.columns(5)

column1.metric("Gross Revenue", f"£{total_revenue:,.0f}")
column2.metric("Orders", f"{total_orders:,}")
column3.metric("Customers", f"{total_customers:,}")
column4.metric("Units Sold", f"{total_units:,.0f}")
column5.metric("Average Order", f"£{average_order_value:,.2f}")

sales["Month"] = (
    sales["InvoiceDate"]
    .dt.to_period("M")
    .dt.to_timestamp()
)

monthly_revenue = (
    sales.groupby("Month", as_index=False)["Revenue"]
    .sum()
)

revenue_chart = px.line(
    monthly_revenue,
    x="Month",
    y="Revenue",
    markers=True,
    title="Monthly Revenue Trend"
)

revenue_chart.update_traces(
    line_color="#00539F",
    line_width=3
)

revenue_chart.update_layout(
    yaxis_title="Revenue (£)",
    xaxis_title="Month"
)

st.plotly_chart(
    revenue_chart,
    use_container_width=True
)

country_revenue = (
    sales.groupby("Country", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
    .head(10)
)

country_chart = px.bar(
    country_revenue,
    x="Revenue",
    y="Country",
    orientation="h",
    title="Top 10 Countries by Revenue",
    color_discrete_sequence=["#E31837"]
)

country_chart.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    },
    xaxis_title="Revenue (£)",
    yaxis_title=""
)

st.plotly_chart(
    country_chart,
    use_container_width=True
)

st.success("Sales data loaded successfully.")