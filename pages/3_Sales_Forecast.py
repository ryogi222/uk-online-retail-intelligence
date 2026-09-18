from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Sales Forecast",
    page_icon="📈",
    layout="wide"
)

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "processed"


@st.cache_data
def load_forecast_data():
    weekly = pd.read_csv(
        DATA_DIR / "weekly_revenue.csv"
    )

    forecast = pd.read_csv(
        DATA_DIR / "eight_week_sales_forecast.csv"
    )

    performance = pd.read_csv(
        DATA_DIR / "forecast_model_comparison.csv"
    )

    return weekly, forecast, performance


try:
    weekly, forecast, performance = load_forecast_data()
except FileNotFoundError as error:
    st.error(f"Forecast file was not found: {error}")
    st.stop()


# Identify and standardise the date column
if "InvoiceDate" in weekly.columns:
    weekly_date_column = "InvoiceDate"
else:
    weekly_date_column = weekly.columns[0]

weekly = weekly.rename(
    columns={weekly_date_column: "Week"}
)

weekly["Week"] = pd.to_datetime(
    weekly["Week"],
    errors="coerce"
)

forecast["Week"] = pd.to_datetime(
    forecast["Week"],
    errors="coerce"
)

weekly = weekly.dropna(
    subset=["Week", "Revenue"]
).sort_values("Week")

forecast = forecast.dropna(
    subset=["Week", "ForecastRevenue"]
).sort_values("Week")

performance = performance.sort_values("RMSE")

best_result = performance.iloc[0]
best_model = best_result["Model"]
best_mae = best_result["MAE"]
best_rmse = best_result["RMSE"]
best_mape = best_result["MAPE_Percent"]

forecast_total = forecast["ForecastRevenue"].sum()
average_weekly_forecast = forecast["ForecastRevenue"].mean()


st.title("Sales Forecast")
st.caption(
    "Weekly revenue forecasting and model-performance comparison"
)

column1, column2, column3, column4 = st.columns(4)

column1.metric(
    "Best Model",
    best_model
)

column2.metric(
    "MAPE",
    f"{best_mape:.2f}%"
)

column3.metric(
    "RMSE",
    f"£{best_rmse:,.0f}"
)

column4.metric(
    "Eight-Week Forecast",
    f"£{forecast_total:,.0f}"
)


forecast_chart = go.Figure()

forecast_chart.add_trace(
    go.Scatter(
        x=weekly["Week"].tail(20),
        y=weekly["Revenue"].tail(20),
        mode="lines+markers",
        name="Historical Revenue",
        line={
            "color": "#00539F",
            "width": 3
        }
    )
)

forecast_chart.add_trace(
    go.Scatter(
        x=forecast["Week"],
        y=forecast["ForecastRevenue"],
        mode="lines+markers",
        name="Forecast Revenue",
        line={
            "color": "#E31837",
            "width": 3,
            "dash": "dash"
        }
    )
)

forecast_chart.add_vline(
    x=weekly["Week"].max().timestamp() * 1000,
    line_dash="dot",
    line_color="white",
    annotation_text="Forecast begins"
)

forecast_chart.update_layout(
    title="Historical and Forecast Weekly Revenue",
    xaxis_title="Week",
    yaxis_title="Revenue (£)",
    hovermode="x unified"
)

st.plotly_chart(
    forecast_chart,
    use_container_width=True
)


left_column, right_column = st.columns(2)

with left_column:
    comparison_chart = px.bar(
        performance,
        x="Model",
        y=["MAE", "RMSE"],
        barmode="group",
        title="Model Error Comparison",
        color_discrete_sequence=[
            "#00539F",
            "#E31837"
        ]
    )

    comparison_chart.update_layout(
        yaxis_title="Forecast Error (£)",
        xaxis_title="Model",
        legend_title=""
    )

    st.plotly_chart(
        comparison_chart,
        use_container_width=True
    )


with right_column:
    st.subheader("Model Performance")

    st.dataframe(
        performance,
        use_container_width=True,
        hide_index=True,
        column_config={
            "MAE": st.column_config.NumberColumn(
                "MAE",
                format="£%.2f"
            ),
            "RMSE": st.column_config.NumberColumn(
                "RMSE",
                format="£%.2f"
            ),
            "MAPE_Percent": st.column_config.NumberColumn(
                "MAPE (%)",
                format="%.2f%%"
            )
        }
    )


st.subheader("Eight-Week Forecast")

st.dataframe(
    forecast,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Week": st.column_config.DateColumn(
            "Week",
            format="DD MMM YYYY"
        ),
        "ForecastRevenue": st.column_config.NumberColumn(
            "Forecast Revenue",
            format="£%.2f"
        )
    }
)


st.info(
    f"""
    {best_model} achieved the strongest holdout performance,
    with an MAE of £{best_mae:,.0f}, RMSE of £{best_rmse:,.0f}
    and MAPE of {best_mape:.2f}%.

    The average predicted weekly revenue is
    £{average_weekly_forecast:,.0f}.
    """
)


with st.expander("Forecast limitations"):
    st.write(
        """
        This is a trend-based scenario forecast. The dataset contains
        approximately one annual cycle and does not include promotional,
        holiday, economic or inventory variables. The forecast should not
        be treated as a live prediction of current UK retail revenue.
        """
    )