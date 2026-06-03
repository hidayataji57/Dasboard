import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Customer Intelligence",
    layout="wide"
)

st.title("👥 Customer Intelligence")

# ==================================================
# LOAD DATA
# ==================================================

@st.cache_data
def load_rfm():
    return pd.read_parquet(
        "Data/df_rfm.parquet"
    )

rfm = load_rfm()

# ==================================================
# SIDEBAR FILTER
# ==================================================

with st.sidebar:

    st.header("👥 Customer Filters")

    customer_type = st.multiselect(
        "Customer Type",
        options=sorted(
            rfm["is_repeat_customer"]
            .dropna()
            .unique()
        )
    )

filtered_rfm = rfm.copy()

if customer_type:

    filtered_rfm = filtered_rfm[
        filtered_rfm["is_repeat_customer"]
        .isin(customer_type)
    ]

if filtered_rfm.empty:

    st.warning(
        "⚠️ Tidak ada customer yang sesuai filter."
    )

    st.stop()

# ==================================================
# KPI
# ==================================================

total_customer = len(filtered_rfm)

avg_recency = filtered_rfm["Recency"].mean()

avg_frequency = filtered_rfm["Frequency"].mean()

avg_monetary = filtered_rfm["Monetary"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "👤 Total Customer",
    f"{total_customer:,}"
)

c2.metric(
    "📅 Avg Recency",
    f"{avg_recency:.1f}"
)

c3.metric(
    "🔁 Avg Frequency",
    f"{avg_frequency:.1f}"
)

c4.metric(
    "💰 Avg Monetary",
    f"RM {avg_monetary:,.2f}"
)

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Customer Health",
        "📈 Customer Explorer",
        "🤖 AI Insight"
    ]
)

# ==================================================
# TAB 1
# ==================================================

with tab1:

    st.subheader("💚 Customer Health")

    champion = filtered_rfm[
        (filtered_rfm["Monetary"] > 1000)
        &
        (filtered_rfm["Frequency"] > 20)
    ]

    loyal = filtered_rfm[
        filtered_rfm["Frequency"] > 10
    ]

    at_risk_count = filtered_rfm[
        filtered_rfm["Recency"] > 180
    ]

    cc1, cc2, cc3 = st.columns(3)

    cc1.metric(
        "🏆 Champion",
        f"{len(champion):,}"
    )

    cc2.metric(
        "❤️ Loyal",
        f"{len(loyal):,}"
    )

    cc3.metric(
        "⚠️ At Risk",
        f"{len(at_risk_count):,}"
    )

    sample_df = filtered_rfm.sample(
        min(50000, len(filtered_rfm)),
        random_state=42
    )

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "📅 Recency Trend"
        )

        recency_line = (
            sample_df
            .groupby("Recency")
            .size()
            .reset_index(name="customers")
            .sort_values("Recency")
        )

        fig_recency = px.line(
            recency_line,
            x="Recency",
            y="customers",
            markers=True
        )

        st.plotly_chart(
            fig_recency,
            use_container_width=True
        )

    with col2:

        st.subheader(
            "🔁 Frequency Trend"
        )

        frequency_line = (
            sample_df
            .groupby("Frequency")
            .size()
            .reset_index(name="customers")
            .sort_values("Frequency")
        )

        fig_frequency = px.line(
            frequency_line,
            x="Frequency",
            y="customers",
            markers=True
        )

        st.plotly_chart(
            fig_frequency,
            use_container_width=True
        )

    st.subheader(
        "💰 Monetary Trend"
    )

    sample_df["Monetary_Bin"] = pd.cut(
        sample_df["Monetary"],
        bins=30
    )

    monetary_line = (
        sample_df
        .groupby("Monetary_Bin")
        .size()
        .reset_index(name="customers")
    )

    monetary_line["Monetary_Bin"] = (
        monetary_line["Monetary_Bin"]
        .astype(str)
    )

    fig_monetary = px.line(
        monetary_line,
        x="Monetary_Bin",
        y="customers",
        markers=True
    )

    st.plotly_chart(
        fig_monetary,
        use_container_width=True
    )

# ==================================================
# TAB 2
# ==================================================

with tab2:

    st.subheader(
        "📈 Customer Explorer"
    )

    scatter_sample = filtered_rfm.sample(
        min(5000, len(filtered_rfm)),
        random_state=42
    )

    fig_scatter = px.scatter(
        scatter_sample,
        x="Frequency",
        y="Monetary",
        color="Recency",
        hover_data=["user_id"]
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

    st.subheader(
        "🏆 Top 100 Customers"
    )

    top_customer = (
        filtered_rfm
        .sort_values(
            "Monetary",
            ascending=False
        )
        .head(100)
    )

    st.dataframe(
        top_customer,
        use_container_width=True
    )

    st.subheader(
        "⚠️ At Risk Customers"
    )

    at_risk = (
        filtered_rfm[
            (filtered_rfm["Recency"] > 180)
            &
            (filtered_rfm["Frequency"] < 10)
        ]
        .sort_values(
            "Recency",
            ascending=False
        )
        .head(100)
    )

    st.dataframe(
        at_risk,
        use_container_width=True
    )

    st.subheader(
        "🔄 Repeat Customer Analysis"
    )

    repeat_df = (
        filtered_rfm["is_repeat_customer"]
        .value_counts()
        .reset_index()
    )

    repeat_df.columns = [
        "customer_type",
        "count"
    ]

    fig_repeat = px.pie(
        repeat_df,
        names="customer_type",
        values="count",
        hole=0.5
    )

    st.plotly_chart(
        fig_repeat,
        use_container_width=True
    )

    st.subheader(
        "🌐 RFM 3D Scatter"
    )

    rfm_sample = filtered_rfm.sample(
        min(5000, len(filtered_rfm)),
        random_state=42
    )

    fig_3d = px.scatter_3d(
        rfm_sample,
        x="Recency",
        y="Frequency",
        z="Monetary",
        color="Monetary",
        opacity=0.7
    )

    st.plotly_chart(
        fig_3d,
        use_container_width=True
    )

# ==================================================
# TAB 3
# ==================================================

with tab3:

    st.subheader(
        "🤖 AI Customer Insight"
    )

    best_customer = (
        filtered_rfm
        .sort_values(
            "Monetary",
            ascending=False
        )
        .iloc[0]
    )

    st.success(
    f"""
🏆 Top Customer

User ID : {best_customer['user_id']}

💰 Monetary :
RM {best_customer['Monetary']:,.2f}

🔁 Frequency :
{best_customer['Frequency']}

📅 Recency :
{best_customer['Recency']}

Recommendation :
Retain this customer using exclusive promotions.
"""
    )

    st.subheader(
        "🤖 Customer Segmentation"
    )

    st.warning(
    """
KMeans Model belum diaktifkan.

Planned Segments:

🏆 Champion

❤️ Loyal

🌱 Potential

⚠️ At Risk
"""
    )

# ==================================================
# RAW DATA
# ==================================================

with st.expander(
    "🔍 Preview RFM Data"
):

    st.dataframe(
        filtered_rfm.head(100),
        use_container_width=True
    )