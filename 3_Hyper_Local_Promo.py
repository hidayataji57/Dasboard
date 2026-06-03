
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Hyper Local Promo",
    layout="wide"
)

st.title("🎯 Hyper Local Promo Recommender")

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_data():

    cols = [
        "transaction_id",
        "final_amount",
        "hour",
        "city",
        "transaction_period",
        "is_weekend_bool",
        "is_voucher_used_bool"
    ]

    return pd.read_parquet(
        "Data\df_transaction_features.parquet",
        columns=cols
    )

df = load_data()

# ==================================================
# FILTER CITY
# ==================================================

city_list = sorted(
    df["city"].dropna().unique()
)

selected_city = st.selectbox(
    "📍 Select City",
    city_list
)

city_df = df[
    df["city"] == selected_city
]

# ==================================================
# KPI
# ==================================================

total_revenue = city_df["final_amount"].sum()

total_transaction = (
    city_df["transaction_id"]
    .nunique()
)

avg_transaction = (
    city_df["final_amount"]
    .mean()
)

voucher_rate = (
    city_df["is_voucher_used_bool"]
    .mean() * 100
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Revenue",
    f"RM {total_revenue:,.0f}"
)

c2.metric(
    "Transactions",
    f"{total_transaction:,}"
)

c3.metric(
    "Avg Transaction",
    f"RM {avg_transaction:.2f}"
)

c4.metric(
    "Voucher Usage",
    f"{voucher_rate:.1f}%"
)

st.divider()

# ==================================================
# TRAFFIC BY HOUR
# ==================================================

st.subheader("⏰ Traffic by Hour")

hourly = (
    city_df
    .groupby("hour")
    .size()
    .reset_index(name="traffic")
)

fig_hour = px.line(
    hourly,
    x="hour",
    y="traffic",
    markers=True
)

st.plotly_chart(
    fig_hour,
    use_container_width=True
)

# ==================================================
# OFF PEAK ANALYSIS
# ==================================================

avg_traffic = hourly["traffic"].mean()

off_peak = hourly[
    hourly["traffic"] < avg_traffic
]

st.subheader("📉 Off Peak Hours")

st.dataframe(
    off_peak,
    use_container_width=True
)

# ==================================================
# TRANSACTION PERIOD
# ==================================================

st.subheader("🌞 Transaction Period Analysis")

period_df = (
    city_df
    .groupby("transaction_period")
    .size()
    .reset_index(name="transactions")
)

fig_period = px.bar(
    period_df,
    x="transaction_period",
    y="transactions",
    color="transactions"
)

st.plotly_chart(
    fig_period,
    use_container_width=True
)

# ==================================================
# WEEKEND VS WEEKDAY
# ==================================================

st.subheader("📅 Weekend vs Weekday")

week_df = (
    city_df
    .groupby("is_weekend_bool")
    .agg(
        revenue=("final_amount","sum"),
        transactions=("transaction_id","count")
    )
    .reset_index()
)

week_df["is_weekend_bool"] = (
    week_df["is_weekend_bool"]
    .map({
        0:"Weekday",
        1:"Weekend"
    })
)

fig_week = px.bar(
    week_df,
    x="is_weekend_bool",
    y="revenue",
    color="is_weekend_bool"
)

st.plotly_chart(
    fig_week,
    use_container_width=True
)

# ==================================================
# PROMO GENERATOR
# ==================================================

st.subheader("🚀 Promo Recommendation")

if len(off_peak) > 0:

    worst_hour = (
        off_peak
        .sort_values(
            "traffic"
        )
        .iloc[0]["hour"]
    )

    st.success(
        f"""
📍 City : {selected_city}

⏰ Lowest Traffic Hour : {int(worst_hour)}:00

🎯 Recommendation :

• Voucher Discount 10%

• Buy 2 Get 1 Promotion

• Happy Hour Campaign

• Push Notification Campaign

Expected Result:
Increase transaction volume during off-peak periods.
"""
    )

else:

    st.info(
        "No off-peak hour detected."
    )

# ==================================================
# REVENUE OPPORTUNITY
# ==================================================

st.subheader("💰 Revenue Opportunity")

if len(off_peak) > 0:

    potential_tx = (
        off_peak["traffic"]
        .mean()
    )

    potential_revenue = (
        potential_tx
        * avg_transaction
        * 0.15
    )

    st.metric(
        "Estimated Revenue Lift",
        f"RM {potential_revenue:,.2f}"
    )

# ==================================================
# FUTURE ML
# ==================================================

st.divider()

st.info(
    """
🤖 Future Enhancement

Random Forest Regressor

Features:
- Hour
- City
- Weekend
- Transaction Period

Output:
- Traffic Prediction
- Dynamic Promo Recommendation
"""
)

