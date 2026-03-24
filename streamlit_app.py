import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="AI Usage Dashboard", layout="wide")

# ---------------------------
# DARK THEME (IMPROVED)
# ---------------------------
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #E5E7EB;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #111827;
        padding: 15px;
        border-radius: 10px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #020617;
    }

    /* Tables */
    .stDataFrame {
        background-color: #111827;
    }

    /* Labels */
    label, .stMarkdown {
        color: #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------
# GENERATE SAMPLE DATA
# ---------------------------
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", periods=365)

models = ["GPT-4", "Claude", "Gemini", "Llama"]
industries = ["Finance", "Healthcare", "Retail", "Education", "Tech"]

data = pd.DataFrame({
    "date": np.random.choice(dates, 1000),
    "model": np.random.choice(models, 1000),
    "industry": np.random.choice(industries, 1000),
    "users": np.random.randint(50, 1000, 1000),
    "cost": np.random.uniform(100, 10000, 1000),
    "requests": np.random.randint(100, 5000, 1000)
})

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("Filters")

selected_model = st.sidebar.multiselect(
    "Select Model", data["model"].unique(), default=data["model"].unique()
)
selected_industry = st.sidebar.multiselect(
    "Select Industry", data["industry"].unique(), default=data["industry"].unique()
)

date_range = st.sidebar.date_input(
    "Select Date Range", [data["date"].min(), data["date"].max()]
)

# Filter data
filtered_df = data[
    (data["model"].isin(selected_model)) &
    (data["industry"].isin(selected_industry)) &
    (data["date"] >= pd.to_datetime(date_range[0])) &
    (data["date"] <= pd.to_datetime(date_range[1]))
]

# ---------------------------
# TITLE
# ---------------------------
st.title("AI Usage Analytics Dashboard")

# ---------------------------
# KPI SCORECARDS
# ---------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Users", f"{filtered_df['users'].sum():,}")
col2.metric("Total Requests", f"{filtered_df['requests'].sum():,}")
col3.metric("Total Cost ($)", f"${filtered_df['cost'].sum():,.0f}")

if filtered_df['requests'].sum() > 0:
    avg_cost = filtered_df['cost'].sum() / filtered_df['requests'].sum()
else:
    avg_cost = 0

col4.metric("Avg Cost per Request", f"${avg_cost:.2f}")

# ---------------------------
# CHARTS
# ---------------------------

# Trend over time
trend = filtered_df.groupby("date").agg({"users": "sum", "requests": "sum"}).reset_index()

fig_trend = px.line(trend, x="date", y=["users", "requests"], title="Usage Trends")
fig_trend.update_layout(template="plotly_dark")
st.plotly_chart(fig_trend, use_container_width=True)

# Usage by model
model_usage = filtered_df.groupby("model")["requests"].sum().reset_index()
fig_model = px.bar(model_usage, x="model", y="requests", title="Requests by Model")
fig_model.update_layout(template="plotly_dark")
st.plotly_chart(fig_model, use_container_width=True)

# Cost by industry
cost_industry = filtered_df.groupby("industry")["cost"].sum().reset_index()
fig_cost = px.pie(cost_industry, names="industry", values="cost", title="Cost Distribution by Industry")
fig_cost.update_layout(template="plotly_dark")
st.plotly_chart(fig_cost, use_container_width=True)

# ---------------------------
# PIVOT TABLE
# ---------------------------
st.subheader("Pivot Table")

pivot = pd.pivot_table(
    filtered_df,
    values="requests",
    index="industry",
    columns="model",
    aggfunc="sum",
    fill_value=0
)

st.dataframe(pivot, use_container_width=True)

# ---------------------------
# DATA TABLE
# ---------------------------
st.subheader("Raw Data")
st.dataframe(filtered_df, use_container_width=True)

# ---------------------------
# INSIGHTS SECTION
# ---------------------------
st.subheader("Insights")

if not filtered_df.empty:
    top_model = model_usage.sort_values(by="requests", ascending=False).iloc[0]["model"]
    top_industry = cost_industry.sort_values(by="cost", ascending=False).iloc[0]["industry"]

    st.write(f"- Top performing model: **{top_model}**")
    st.write(f"- Highest spending industry: **{top_industry}**")
    st.write("- AI adoption is increasing over time based on request trends.")
else:
    st.write("No data available for selected filters.")

