from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Products and Returns",
    page_icon="📦",
    layout="wide"
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"


@st.cache_data
def load_data():
    sales = pd.read_csv(
        DATA_DIR / "online_retail_clean_v2.csv",
        parse_dates=["InvoiceDate"],
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string"
        },
        low_memory=False
    )

    returns = pd.read_csv(
        DATA_DIR / "online_retail_returns_v2.csv",
        parse_dates=["InvoiceDate"],
        dtype={
            "InvoiceNo": "string",
            "StockCode": "string"
        },
        low_memory=False
    )

    return sales, returns


try:
    sales, returns = load_data()
except FileNotFoundError as error:
    st.error(f"Required data file was not found: {error}")
    st.stop()


returns["ReturnValue"] = (
    returns["Quantity"].abs() *
    returns["UnitPrice"].abs()
)

returns["ReturnType"] = np.where(
    returns["InvoiceNo"]
    .str.upper()
    .str.startswith("C"),
    "Customer Cancellation",
    "Stock Adjustment"
)


gross_revenue = sales["Revenue"].sum()

customer_return_value = returns.loc[
    returns["ReturnType"] == "Customer Cancellation",
    "ReturnValue"
].sum()

estimated_net_revenue = (
    gross_revenue - customer_return_value
)

return_rate = (
    customer_return_value / gross_revenue
    if gross_revenue > 0
    else 0
)


st.title("Products and Returns")
st.caption(
    "Product performance, cancellations and stock adjustments"
)

column1, column2, column3, column4 = st.columns(4)

column1.metric(
    "Gross Revenue",
    f"£{gross_revenue:,.0f}"
)

column2.metric(
    "Customer Returns",
    f"£{customer_return_value:,.0f}"
)

column3.metric(
    "Estimated Net Revenue",
    f"£{estimated_net_revenue:,.0f}"
)

column4.metric(
    "Return Rate",
    f"{return_rate:.2%}"
)


non_product_codes = [
    "POST",
    "DOT",
    "M",
    "D",
    "S",
    "AMAZONFEE",
    "BANK CHARGES",
    "CRUK"
]


sales_activity = sales[
    [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "Revenue"
    ]
].copy()

sales_activity["NetRevenue"] = sales_activity["Revenue"]
sales_activity["NetUnits"] = sales_activity["Quantity"]


return_activity = returns[
    (returns["Quantity"] < 0) &
    (returns["UnitPrice"] > 0)
][
    [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "UnitPrice"
    ]
].copy()

return_activity["NetRevenue"] = (
    return_activity["Quantity"] *
    return_activity["UnitPrice"]
)

return_activity["NetUnits"] = return_activity["Quantity"]

return_activity = return_activity.drop(
    columns=["UnitPrice"]
)


all_activity = pd.concat(
    [
        sales_activity[
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "NetUnits",
                "NetRevenue"
            ]
        ],
        return_activity[
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "NetUnits",
                "NetRevenue"
            ]
        ]
    ],
    ignore_index=True
)

all_activity = all_activity[
    ~all_activity["StockCode"].isin(non_product_codes)
].dropna(subset=["Description"])


product_performance = (
    all_activity.groupby(
        ["StockCode", "Description"],
        as_index=False
    )
    .agg(
        NetRevenue=("NetRevenue", "sum"),
        NetUnits=("NetUnits", "sum"),
        Transactions=("InvoiceNo", "nunique")
    )
)

product_performance = product_performance[
    (product_performance["NetRevenue"] > 0) &
    (product_performance["NetUnits"] > 0)
]


top_products = (
    product_performance
    .sort_values("NetRevenue", ascending=False)
    .head(10)
)


return_type_summary = (
    returns.groupby("ReturnType", as_index=False)
    .agg(
        ReturnValue=("ReturnValue", "sum"),
        Rows=("InvoiceNo", "count")
    )
)


left_column, right_column = st.columns(2)

with left_column:
    product_chart = px.bar(
        top_products,
        x="NetRevenue",
        y="Description",
        orientation="h",
        title="Top 10 Products by Net Revenue",
        color_discrete_sequence=["#00539F"]
    )

    product_chart.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        },
        xaxis_title="Net Revenue (£)",
        yaxis_title=""
    )

    st.plotly_chart(
        product_chart,
        use_container_width=True
    )


with right_column:
    return_type_chart = px.pie(
        return_type_summary,
        names="ReturnType",
        values="ReturnValue",
        hole=0.55,
        title="Return Value by Type",
        color="ReturnType",
        color_discrete_map={
            "Customer Cancellation": "#E31837",
            "Stock Adjustment": "#00539F"
        }
    )

    st.plotly_chart(
        return_type_chart,
        use_container_width=True
    )


customer_returns = returns[
    (
        returns["ReturnType"] ==
        "Customer Cancellation"
    ) &
    returns["Description"].notna() &
    ~returns["StockCode"].isin(non_product_codes)
].copy()


top_returned_products = (
    customer_returns.groupby(
        "Description",
        as_index=False
    )
    .agg(
        ReturnedUnits=(
            "Quantity",
            lambda values: values.abs().sum()
        ),
        ReturnValue=("ReturnValue", "sum"),
        ReturnTransactions=("InvoiceNo", "nunique")
    )
    .sort_values("ReturnValue", ascending=False)
    .head(10)
)


returns_chart = px.bar(
    top_returned_products,
    x="ReturnValue",
    y="Description",
    orientation="h",
    title="Top Customer Returns by Value",
    color_discrete_sequence=["#E31837"]
)

returns_chart.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    },
    xaxis_title="Return Value (£)",
    yaxis_title=""
)

st.plotly_chart(
    returns_chart,
    use_container_width=True
)


st.subheader("Product Performance")

st.dataframe(
    product_performance[
        [
            "StockCode",
            "Description",
            "NetRevenue",
            "NetUnits",
            "Transactions"
        ]
    ].sort_values(
        "NetRevenue",
        ascending=False
    ),
    use_container_width=True,
    hide_index=True,
    column_config={
        "NetRevenue": st.column_config.NumberColumn(
            "Net Revenue",
            format="£%.2f"
        ),
        "NetUnits": st.column_config.NumberColumn(
            "Net Units",
            format="%d"
        )
    }
)


with st.expander("How returns are classified"):
    st.write(
        """
        Customer cancellations are invoices beginning with C.
        Other negative-quantity records are classified as stock
        adjustments, including damaged, unsaleable or corrected stock.
        """
    )