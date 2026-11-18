
# 📊 Customer Churn & Sales Trend Analysis

An interactive E-Commerce Business Intelligence project built using Python, Pandas, NumPy, Plotly and Streamlit.

## Project Overview

This project analyzes e-commerce sales transactions to understand revenue trends, customer purchasing behavior, customer segmentation and churn risk.

It provides an interactive dashboard that converts raw sales data into useful business insights.

## Features

- E-commerce sales analysis
- Customer RFM segmentation
- Customer churn classification
- Revenue and order KPIs
- Monthly revenue trends
- Three-month rolling average
- Product category analysis
- Interactive pivot tables
- Date-based feature engineering
- Business recommendations
- Custom CSV upload

## Technology Stack

- Python
- Pandas
- NumPy
- Plotly
- Streamlit

## Project Structure

```text
Customer-Churn-Analysis/
│
├── app.py
├── analysis.py
├── requirements.txt
├── README.md
└── data/
    └── ecommerce_sales.csv
```

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Open the project directory:

```bash
cd Customer-Churn-Analysis
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run app.py
```

## Analytical Methodology

### 1. Feature Engineering

Extracted:
- Year
- Month
- Quarter
- YearMonth
- Day of Week
- Weekend / Weekday

### 2. RFM Analysis

Customers are analyzed using:

- Recency: Days since last purchase
- Frequency: Number of orders
- Monetary: Total customer spending

### 3. Churn Classification

Customers inactive beyond the selected threshold are classified as churned.

### 4. Business Intelligence

The dashboard provides:
- Revenue trends
- Customer segment analysis
- Category performance
- Pivot tables
- Retention recommendations

## Business Recommendations

- Win-back campaigns for churned customers
- VIP benefits for champions
- Cross-selling for new customers
- Retention offers for at-risk customers

## Dataset

The application includes synthetic sample data.

Users can upload their own CSV containing:

- OrderDate
- CustomerID
- Revenue

Optional columns include:

- OrderID
- Region
- Category
- Quantity
- Discount

## Important Note

The churn classification uses an inactivity-based business rule. It is not a machine learning prediction model.

The estimated net margin uses an assumed base margin of 38%, not verified business cost data.

## Author

Anmol Patel

## License

MIT License
