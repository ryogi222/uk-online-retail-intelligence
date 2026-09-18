from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Customer Segmentation",
    page_icon="ðŸ‘¥",
    layout="wide"
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"


@st.cache_data
def load_customer_segments():
    return pd.read_csv(
        DATA_DIR / "rfm_customer_segments.csv"
    )


try:
    customers = load_customer_segments()
except FileNotFoundError:
    st.error(
        "rfm_customer_segments.csv was not found "
        "inside data/processed."
    )
    st.stop()


# Create business-friendly cluster names if not already present
if "ClusterName" not in customers.columns:
    high_value_cluster = (
        customers.groupby("Cluster")["Monetary"]
        .mean()
        .idxmax()
    )

    customers["ClusterName"] = np.where(
        customers["Cluster"] == high_value_cluster,
        "High Value and Engaged",
        "Low Engagement or Inactive"
    )


st.title("Customer Segmentation")
st.caption(
    "RFM analysis and K-Means customer clustering"
)

total_customers = customers["CustomerID"].nunique()

champions = (
    customers["RFM_Segment"]
    .eq("Champions")
    .sum()
)

loyal_customers = (
    customers["RFM_Segment"]
    .eq("Loyal Customers")
    .sum()
)

at_risk = (
    customers["RFM_Segment"]
    .eq("At Risk")
    .sum()
)

column1, column2, column3, column4 = st.columns(4)

column1.metric("Customers", f"{total_customers:,}")
column2.metric("Champions", f"{champions:,}")
column3.metric("Loyal Customers", f"{loyal_customers:,}")
column4.metric("At-Risk Customers", f"{at_risk:,}")


segment_summary = (
    customers.groupby("RFM_Segment", as_index=False)
    .agg(
        Customers=("CustomerID", "count"),
        Revenue=("Monetary", "sum"),
        AverageSpending=("Monetary", "mean")
    )
    .sort_values("Revenue", ascending=False)
)

left_column, right_column = st.columns(2)

with left_column:
    segment_chart = px.bar(
        segment_summary,
        x="Customers",
        y="RFM_Segment",
        orientation="h",
        title="Customers by RFM Segment",
        color="Revenue",
        color_continuous_scale="Blues"
    )

    segment_chart.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        },
        yaxis_title="",
        xaxis_title="Number of Customers"
    )

    st.plotly_chart(
        segment_chart,
        width="stretch"
    )


with right_column:
    revenue_chart = px.bar(
        segment_summary,
        x="Revenue",
        y="RFM_Segment",
        orientation="h",
        title="Revenue by RFM Segment",
        color_discrete_sequence=["#E31837"]
    )

    revenue_chart.update_layout(
        yaxis={
            "categoryorder": "total ascending"
        },
        yaxis_title="",
        xaxis_title="Revenue (Â£)"
    )

    st.plotly_chart(
        revenue_chart,
        width="stretch"
    )


scatter_chart = px.scatter(
    customers,
    x="Recency",
    y="Monetary",
    color="ClusterName",
    size="Frequency",
    size_max=35,
    log_y=True,
    hover_data=[
        "CustomerID",
        "RFM_Segment",
        "Frequency"
    ],
    title="Customer Clusters: Recency and Spending"
)

scatter_chart.update_layout(
    xaxis_title="Days Since Last Purchase",
    yaxis_title="Customer Spending (Â£, Log Scale)"
)

st.plotly_chart(
    scatter_chart,
    width="stretch"
)


selected_segments = st.multiselect(
    "Filter customer segments",
    options=sorted(
        customers["RFM_Segment"].unique()
    ),
    default=sorted(
        customers["RFM_Segment"].unique()
    )
)

filtered_customers = customers[
    customers["RFM_Segment"].isin(selected_segments)
]

st.subheader("Customer Details")

st.dataframe(
    filtered_customers[
        [
            "CustomerID",
            "RFM_Segment",
            "ClusterName",
            "Recency",
            "Frequency",
            "Monetary",
            "RFM_Total"
        ]
    ].sort_values(
        "Monetary",
        ascending=False
    ),
    width="stretch",
    hide_index=True
)
