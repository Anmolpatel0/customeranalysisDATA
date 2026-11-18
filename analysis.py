
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_data(n_rows=5000, seed=42):
    rng = np.random.default_rng(seed)

    customers = [f"CUST-{1000+i}" for i in range(850)]

    regions = ["North", "South", "East", "West"]

    categories = {
        "Electronics": (120, 850),
        "Apparel": (25, 180),
        "Home & Kitchen": (40, 320),
        "Beauty & Health": (15, 95),
        "Sports & Outdoors": (30, 260)
    }

    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 10, 31)

    total_days = (end_date - start_date).days

    records = []

    for i in range(n_rows):

        order_date = start_date + timedelta(
            days=int(rng.integers(0, total_days + 1))
        )

        category = rng.choice(list(categories.keys()))

        low, high = categories[category]

        price = round(float(rng.uniform(low, high)), 2)

        quantity = int(rng.choice([1, 2, 3, 4]))

        discount = float(rng.choice([0, 0.05, 0.10, 0.20]))

        revenue = round(price * quantity * (1 - discount), 2)

        records.append({
            "OrderID": f"ORD-{100000+i}",
            "OrderDate": order_date,
            "CustomerID": rng.choice(customers),
            "Region": rng.choice(regions),
            "Category": category,
            "Quantity": quantity,
            "UnitPrice": price,
            "Discount": discount,
            "Revenue": revenue
        })

    return pd.DataFrame(records)


def safe_score(series, ascending=True):
    ranks = series.rank(method="first", ascending=ascending)

    if len(series) < 4:
        return np.ceil(ranks / max(len(series), 1) * 4).astype(int)

    return pd.qcut(
        ranks,
        4,
        labels=[1, 2, 3, 4]
    ).astype(int)


def analyze_data(df, churn_days=90):

    data = df.copy()

    required = {"OrderDate", "CustomerID", "Revenue"}

    missing = required - set(data.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    defaults = {
        "OrderID": [f"ORD-{i+1}" for i in range(len(data))],
        "Region": "All Regions",
        "Category": "General",
        "Quantity": 1,
        "Discount": 0
    }

    for col, default in defaults.items():
        if col not in data.columns:
            data[col] = default

    data["OrderDate"] = pd.to_datetime(
        data["OrderDate"], errors="coerce"
    )

    data["Revenue"] = pd.to_numeric(
        data["Revenue"], errors="coerce"
    )

    data["Quantity"] = pd.to_numeric(
        data["Quantity"], errors="coerce"
    ).fillna(1)

    data["Discount"] = pd.to_numeric(
        data["Discount"], errors="coerce"
    ).fillna(0)

    data = data.dropna(
        subset=["OrderDate", "CustomerID", "Revenue"]
    ).copy()

    if data.empty:
        raise ValueError("No valid transaction rows found.")

    data["CustomerID"] = data["CustomerID"].astype(str)

    # DATE FEATURE ENGINEERING

    data["Year"] = data["OrderDate"].dt.year
    data["Month"] = data["OrderDate"].dt.month
    data["YearMonth"] = data["OrderDate"].dt.to_period("M").astype(str)
    data["Quarter"] = data["OrderDate"].dt.to_period("Q").astype(str)
    data["DayOfWeek"] = data["OrderDate"].dt.day_name()

    data["IsWeekend"] = np.where(
        data["OrderDate"].dt.dayofweek >= 5,
        "Weekend",
        "Weekday"
    )

    data["NetMarginEst"] = (
        data["Revenue"] * (0.38 - data["Discount"])
    ).round(2)

    # RFM ANALYSIS

    snapshot_date = data["OrderDate"].max() + timedelta(days=1)

    customers = data.groupby("CustomerID").agg(
        LastOrderDate=("OrderDate", "max"),
        FirstOrderDate=("OrderDate", "min"),
        Frequency=("OrderID", "nunique"),
        Monetary=("Revenue", "sum"),
        AvgOrderValue=("Revenue", "mean"),
        PrimaryRegion=("Region", "first")
    ).reset_index()

    customers["RecencyDays"] = (
        snapshot_date - customers["LastOrderDate"]
    ).dt.days

    customers["TenureDays"] = (
        customers["LastOrderDate"] -
        customers["FirstOrderDate"]
    ).dt.days + 1

    customers["IsChurned"] = (
        customers["RecencyDays"] > churn_days
    )

    customers["ChurnStatus"] = np.where(
        customers["IsChurned"],
        "Churned",
        "Active"
    )

    customers["R_Score"] = safe_score(
        customers["RecencyDays"], ascending=False
    )

    customers["F_Score"] = safe_score(
        customers["Frequency"]
    )

    customers["M_Score"] = safe_score(
        customers["Monetary"]
    )

    customers["RFM_Total"] = (
        customers["R_Score"] +
        customers["F_Score"] +
        customers["M_Score"]
    )

    def segment(row):

        if row["RFM_Total"] >= 10 and not row["IsChurned"]:
            return "Champions"

        elif row["F_Score"] >= 3 and not row["IsChurned"]:
            return "Loyal Customers"

        elif row["IsChurned"] and row["M_Score"] >= 3:
            return "Churned High-Value"

        elif row["IsChurned"]:
            return "Churned Low-Value"

        elif row["R_Score"] >= 3 and row["Frequency"] == 1:
            return "New / Promising"

        return "Needs Attention"

    customers["CustomerSegment"] = customers.apply(
        segment, axis=1
    )

    data = data.merge(
        customers[
            [
                "CustomerID",
                "CustomerSegment",
                "ChurnStatus",
                "RecencyDays"
            ]
        ],
        on="CustomerID",
        how="left"
    )

    return {
        "transactions": data,
        "customers": customers
    }
