
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Executive Dashboard",
    layout="wide"
    
)

st.title("📊 Executive Dashboard")

# ==================================================
# LOAD DATA
# ==================================================


@st.cache_data
def load_data():

    cols = [
        "transaction_id",
        "final_amount",
        "basket_size",
        "city",
        "member_status",
        "payment_category",
        "hour",
        "day_name",
        "transaction_period",
        "is_voucher_used_bool",
        "is_weekend_bool",
        "created_at"
    ]

    df = pd.read_parquet(
        "Data/df_transaction_features.parquet",
        columns=cols,
        engine="pyarrow"
    )

    for c in [
        "city",
        "member_status",
        "payment_category",
        "day_name",
        "transaction_period"
    ]:
        df[c] = df[c].astype("category")

    df["hour"] = df["hour"].astype("int8")
    df["basket_size"] = df["basket_size"].astype("int16")
    df["is_voucher_used_bool"] = df["is_voucher_used_bool"].astype("int8")
    df["is_weekend_bool"] = df["is_weekend_bool"].astype("int8")

    return df


# ==========================
# LOAD DATA
# ==========================
df = load_data()

if df.empty:
    st.error("Data kosong")
    st.stop()
    
# ==================================================
# FILTER
# ==================================================

with st.sidebar:

    st.header("🔍 Filters")

    city_filter = st.multiselect(
        "City",
        options=sorted(df["city"].dropna().unique())
    )

    member_filter = st.multiselect(
        "Member Status",
        options=sorted(df["member_status"].dropna().unique())
    )

    payment_filter = st.multiselect(
        "Payment Category",
        options=sorted(df["payment_category"].dropna().unique())
    )

filtered_df = df.copy()

if city_filter:
    filtered_df = filtered_df[
        filtered_df["city"].isin(city_filter)
    ]

if member_filter:
    filtered_df = filtered_df[
        filtered_df["member_status"].isin(member_filter)
    ]

if payment_filter:
    filtered_df = filtered_df[
        filtered_df["payment_category"].isin(payment_filter)
    ]

if filtered_df.empty:

    st.warning(
        "⚠️ Tidak ada data yang sesuai dengan filter yang dipilih."
    )

    st.stop()
# ==================================================
# KPI SECTION
# ==================================================

total_revenue = filtered_df["final_amount"].sum()

total_transaction = filtered_df["transaction_id"].nunique()

avg_basket = filtered_df["basket_size"].mean()

voucher_rate = (
    filtered_df["is_voucher_used_bool"].mean() * 100
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Total Revenue",
    f"RM {total_revenue:,.0f}"
)

c2.metric(
    "🧾 Transactions",
    f"{total_transaction:,}"
)

c3.metric(
    "🛒 Avg Basket Size",
    f"{avg_basket:.2f}"
)

c4.metric(
    "🎟 Voucher Usage",
    f"{voucher_rate:.2f}%"
)

st.divider()

# ==================================================
# REVENUE BY CITY
# ==================================================

st.subheader("🏙 Revenue by City")

city_rev = (
    filtered_df.groupby("city")["final_amount"]
      .sum()
      .reset_index()
      .sort_values(
          "final_amount",
          ascending=False
      )
)

fig_city = px.bar(
    city_rev.head(15),
    x="city",
    y="final_amount",
    color="final_amount",
    title="Top 15 Cities by Revenue"
)

st.plotly_chart(
    fig_city,
    use_container_width=True
)

# ==================================================
# PAYMENT CATEGORY
# ==================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("💳 Revenue by Payment Category")

    payment_rev = (
        filtered_df.groupby("payment_category")
          ["final_amount"]
          .sum()
          .reset_index()
    )

    fig_payment = px.pie(
        payment_rev,
        names="payment_category",
        values="final_amount",
        hole=0.5
    )

    st.plotly_chart(
        fig_payment,
        use_container_width=True
    )

with col2:

    st.subheader("👥 Member vs Guest")

    member_count = (
        filtered_df["member_status"]
        .value_counts()
        .reset_index()
    )

    member_count.columns = [
        "member_status",
        "count"
    ]

    fig_member = px.pie(
        member_count,
        names="member_status",
        values="count",
        hole=0.5
    )

    st.plotly_chart(
        fig_member,
        use_container_width=True
    )

# ==================================================
# PEAK HOUR ANALYSIS
# ==================================================

st.subheader("⏰ Peak Hour Analysis")

st.subheader("🔥 Hourly Heatmap")

heatmap_df = (
    filtered_df
    .groupby(["day_name","hour"])
    .size()
    .reset_index(name="transactions")
)

fig_heatmap = px.density_heatmap(
    heatmap_df,
    x="hour",
    y="day_name",
    z="transactions",
    color_continuous_scale="Blues"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)

hourly = (
    filtered_df.groupby("hour")
      .agg(
          transaction_count=(
              "transaction_id",
              "count"
          ),
          revenue=(
              "final_amount",
              "sum"
          )
      )
      .reset_index()
)

fig_hour = px.line(
    hourly,
    x="hour",
    y="transaction_count",
    markers=True,
    title="Transactions by Hour"
)

st.plotly_chart(
    fig_hour,
    use_container_width=True
)

# ==================================================
# TRANSACTION PERIOD
# ==================================================

st.subheader("🌞 Transaction Period")

period_df = (
    filtered_df.groupby("transaction_period")
      ["transaction_id"]
      .count()
      .reset_index()
)

fig_period = px.bar(
    period_df,
    x="transaction_period",
    y="transaction_id",
    color="transaction_id"
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
    filtered_df.groupby("is_weekend_bool")
      .agg(
          revenue=("final_amount","sum"),
          transactions=("transaction_id","count")
      )
      .reset_index()
)

week_df["is_weekend_bool"] = (
    week_df["is_weekend_bool"]
    .map(
        {
            0:"Weekday",
            1:"Weekend"
        }
    )
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

st.divider()

st.subheader("🤖 AI Business Insight")

if not filtered_df.empty:

    best_city = (
        filtered_df
        .groupby("city")["final_amount"]
        .sum()
        .idxmax()
    )

    best_hour = (
        filtered_df
        .groupby("hour")["transaction_id"]
        .count()
        .idxmax()
    )

    st.success(
    f"""
📍 Best Performing City:
{best_city}

⏰ Peak Hour:
{best_hour}:00

📈 Recommendation:
Increase staffing during peak hours and run promotional campaigns during off-peak periods.
"""
    )
# ==================================================
# DATA PREVIEW
# ==================================================

with st.expander("🔍 Preview Data"):

    st.dataframe(
        df.head(100),
        use_container_width=True
    )

