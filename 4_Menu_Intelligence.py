import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Menu Intelligence",
    layout="wide"
)

st.title("🍽 Menu Intelligence")

# ==========================
# LOAD DATA
# ==========================

@st.cache_data
def load_menu():
    return pd.read_parquet(
        "Data/menu_cleaned.parquet"
    )

menu = load_menu()

# ==========================
# KPI
# ==========================

total_menu = len(menu)

avg_price = menu["price"].mean()

seasonal_count = (
    menu["is_seasonal"]
    .sum()
)

non_seasonal = (
    len(menu)
    - seasonal_count
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "🍽 Total Menu",
    total_menu
)

c2.metric(
    "💰 Avg Price",
    f"RM {avg_price:.2f}"
)

c3.metric(
    "🎄 Seasonal",
    seasonal_count
)

c4.metric(
    "📋 Non Seasonal",
    non_seasonal
)

st.divider()

# ==========================
# CATEGORY
# ==========================

st.subheader(
    "📊 Menu by Category"
)

cat_df = (
    menu["category"]
    .value_counts()
    .reset_index()
)

cat_df.columns = [
    "category",
    "count"
]

fig_cat = px.bar(
    cat_df,
    x="category",
    y="count",
    color="count"
)

st.plotly_chart(
    fig_cat,
    use_container_width=True
)

# ==========================
# PRICE DISTRIBUTION
# ==========================

st.subheader(
    "💰 Price Distribution"
)

fig_price = px.histogram(
    menu,
    x="price",
    nbins=20
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)

# ==========================
# SEASONAL
# ==========================

col1, col2 = st.columns(2)

with col1:

    seasonal_df = (
        menu["is_seasonal"]
        .value_counts()
        .reset_index()
    )

    seasonal_df.columns = [
        "seasonal",
        "count"
    ]

    fig_seasonal = px.pie(
        seasonal_df,
        names="seasonal",
        values="count",
        hole=0.5
    )

    st.plotly_chart(
        fig_seasonal,
        use_container_width=True
    )

with col2:

    st.subheader(
        "🏆 Top Expensive Menu"
    )

    st.dataframe(
        menu.sort_values(
            "price",
            ascending=False
        ).head(10),
        use_container_width=True
    )

# ==========================
# PRICE SIMULATOR
# ==========================

st.divider()

st.subheader(
    "🧮 Price Simulation"
)

selected_item = st.selectbox(
    "Choose Product",
    sorted(
        menu["item_name"]
        .unique()
    )
)

selected_row = (
    menu[
        menu["item_name"]
        ==
        selected_item
    ]
    .iloc[0]
)

current_price = (
    selected_row["price"]
)

discount = st.slider(
    "Price Increase (%)",
    0,
    30,
    10
)

new_price = (
    current_price
    *
    (1 + discount/100)
)

c1, c2 = st.columns(2)

c1.metric(
    "Current Price",
    f"RM {current_price:.2f}"
)

c2.metric(
    "New Price",
    f"RM {new_price:.2f}"
)

st.success(
    f"""
Product : {selected_item}

Current Price : RM {current_price:.2f}

New Price : RM {new_price:.2f}

Estimated Revenue Impact :
+{discount}%
"""
)

# ==========================
# RAW DATA
# ==========================

with st.expander(
    "🔍 View Menu Data"
):

    st.dataframe(
        menu,
        use_container_width=True
    )