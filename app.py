
import streamlit as st
import pandas as pd
import plotly.express as px
from analysis import generate_sample_data, analyze_data

st.set_page_config(
    page_title="E-Commerce Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Churn & Sales Trend Analysis")
st.caption("E-Commerce Business Intelligence Dashboard")

st.sidebar.header("Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload your E-Commerce CSV",
    type=["csv"]
)

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.sidebar.success("CSV uploaded successfully!")
    except Exception as e:
        st.error(f"Unable to read CSV: {e}")
        st.stop()
else:
    df = generate_sample_data()

required_columns = {"OrderDate", "CustomerID", "Revenue"}

if not required_columns.issubset(df.columns):
    st.error(f"Missing required columns: {required_columns - set(df.columns)}")
    st.stop()

try:
    churn_days = st.sidebar.slider(
        "Churn Threshold (Days)",
        30, 180, 90, 15
    )

    results = analyze_data(df, churn_days)

    transactions = results["transactions"]
    customers = results["customers"]

except Exception as e:
    st.error(f"Analysis error: {e}")
    st.stop()

regions = sorted(transactions["Region"].unique())
categories = sorted(transactions["Category"].unique())

selected_regions = st.sidebar.multiselect(
    "Select Regions", regions, default=regions
)

selected_categories = st.sidebar.multiselect(
    "Select Categories", categories, default=categories
)

filtered = transactions[
    transactions["Region"].isin(selected_regions)
    & transactions["Category"].isin(selected_categories)
]

if filtered.empty:
    st.warning("No matching data. Showing the complete dataset.")
    filtered = transactions.copy()

filtered_customers = customers[
    customers["CustomerID"].isin(filtered["CustomerID"])
]

revenue = filtered["Revenue"].sum()
orders = filtered["OrderID"].nunique()
aov = revenue / orders if orders else 0
churn = (
    filtered_customers["IsChurned"].mean() * 100
    if not filtered_customers.empty else 0
)
active = (
    (~filtered_customers["IsChurned"]).sum()
    if not filtered_customers.empty else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Revenue", f"${revenue:,.2f}")
c2.metric("Total Orders", f"{orders:,}")
c3.metric("Average Order Value", f"${aov:,.2f}")
c4.metric("Active Customers", f"{active:,}")
c5.metric("Churn Rate", f"{churn:.1f}%")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Sales Trends",
    "👥 Customer Churn",
    "🧮 Pivot Analysis",
    "🎯 Recommendations"
])

# TAB 1: SALES TRENDS

with tab1:
    st.subheader("Monthly Revenue Trends")

    monthly = (
        filtered.groupby("YearMonth", as_index=False)
        .agg(
            Revenue=("Revenue", "sum"),
            Orders=("OrderID", "nunique")
        )
        .sort_values("YearMonth")
    )

    monthly["Growth_%"] = (
        monthly["Revenue"].pct_change().fillna(0) * 100
    )

    monthly["Rolling_Average"] = (
        monthly["Revenue"].rolling(3, min_periods=1).mean()
    )

    fig = px.bar(
        monthly,
        x="YearMonth",
        y="Revenue",
        title="Monthly Revenue",
        color="Revenue",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.line(
        monthly,
        x="YearMonth",
        y="Rolling_Average",
        markers=True,
        title="Three-Month Rolling Revenue Average"
    )

    st.plotly_chart(fig2, use_container_width=True)

    category_sales = (
        filtered.groupby("Category", as_index=False)["Revenue"]
        .sum()
        .sort_values("Revenue", ascending=False)
    )

    st.subheader("Revenue by Product Category")

    st.plotly_chart(
        px.bar(category_sales, x="Category", y="Revenue",
               color="Revenue"),
        use_container_width=True
    )

    st.dataframe(monthly, use_container_width=True)

# TAB 2: CUSTOMER CHURN

with tab2:
    st.subheader("Customer Segmentation")

    if not filtered_customers.empty:
        segment_data = (
            filtered_customers.groupby("CustomerSegment")
            .agg(
                Customers=("CustomerID", "count"),
                Revenue=("Monetary", "sum")
            )
            .reset_index()
        )

        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                px.pie(
                    segment_data,
                    names="CustomerSegment",
                    values="Customers",
                    hole=0.4,
                    title="Customer Distribution"
                ),
                use_container_width=True
            )

        with col2:
            st.plotly_chart(
                px.bar(
                    segment_data,
                    x="CustomerSegment",
                    y="Revenue",
                    color="CustomerSegment",
                    title="Revenue by Customer Segment"
                ),
                use_container_width=True
            )

        st.dataframe(segment_data, use_container_width=True)

    else:
        st.info("No customers match the selected filters.")

# TAB 3: PIVOT TABLE

with tab3:
    st.subheader("Interactive Pivot Table")

    metric = st.selectbox(
        "Select Metric",
        ["Revenue", "Quantity", "NetMarginEst"]
    )

    row = st.selectbox(
        "Select Rows",
        ["Region", "Category", "CustomerSegment", "Quarter"]
    )

    column = st.selectbox(
        "Select Columns",
        ["Quarter", "Region", "ChurnStatus", "IsWeekend"]
    )

    if row == column:
        st.warning("Choose different fields for rows and columns.")
    else:
        pivot = pd.pivot_table(
            filtered,
            values=metric,
            index=row,
            columns=column,
            aggfunc="sum",
            fill_value=0
        )

        st.dataframe(pivot, use_container_width=True)

    st.subheader("Engineered Data Preview")
    st.dataframe(filtered.head(30), use_container_width=True)

# TAB 4: RECOMMENDATIONS

with tab4:
    st.subheader("Business Recommendations")

    if filtered.empty or filtered_customers.empty:
        st.info("Insufficient data for recommendations.")
    else:
        top_category = (
            filtered.groupby("Category")["Revenue"].sum().idxmax()
        )

        top_region = (
            filtered.groupby("Region")["Revenue"].sum().idxmax()
        )

        high_value_risk = filtered_customers.loc[
            filtered_customers["CustomerSegment"] == "Churned High-Value",
            "Monetary"
        ].sum()

        champions = filtered_customers.loc[
            filtered_customers["CustomerSegment"] == "Champions",
            "Monetary"
        ].sum()

        total_customer_revenue = filtered_customers["Monetary"].sum()

        champions_share = (
            champions / total_customer_revenue * 100
            if total_customer_revenue else 0
        )

        st.success(f"Top Category: {top_category}")
        st.info(f"Top Region: {top_region}")
        st.warning(f"High-value churned customer historical revenue: ${high_value_risk:,.2f}")

        st.write(
            f"Champions contribute {champions_share:.1f}% "
            "of customer revenue."
        )

        recommendations = [
            {
                "Segment": "Churned High-Value",
                "Action": "Launch personalized win-back campaigns.",
                "Goal": "Improve customer reactivation."
            },
            {
                "Segment": "Champions",
                "Action": "Offer VIP rewards and early access.",
                "Goal": "Improve customer loyalty."
            },
            {
                "Segment": "New Customers",
                "Action": "Send second-purchase incentives.",
                "Goal": "Increase repeat purchases."
            },
            {
                "Segment": "At-Risk Customers",
                "Action": "Send targeted retention offers.",
                "Goal": "Reduce customer churn."
            }
        ]

        st.dataframe(
            pd.DataFrame(recommendations),
            use_container_width=True
        )

st.divider()

st.caption(
    "E-Commerce Customer Intelligence | "
    "Built using Python, Pandas, Plotly and Streamlit"
)
