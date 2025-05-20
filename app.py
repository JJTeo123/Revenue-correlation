import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Revenue Correlation App", layout="wide")

st.title("📊 Revenue Correlation Analysis")
st.write("Analyze and compare revenue trends across companies using Yahoo Finance data.")

# Sidebar input
tickers_input = st.sidebar.text_area(
    "Enter stock tickers (comma-separated):",
    value="AAPL, MSFT, GOOGL, AMZN, META"
)

start_year = st.sidebar.selectbox("Select start year", list(range(2015, 2025))[::-1])
end_year = st.sidebar.selectbox("Select end year", list(range(2015, 2025))[::-1])

if start_year > end_year:
    st.sidebar.error("Start year must be before or equal to end year")

# Process tickers
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

def get_revenue_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.quarterly_financials.T
        df.index = pd.to_datetime(df.index)
        revenue = df["Total Revenue"]
        revenue.name = ticker
        return revenue
    except Exception as e:
        st.warning(f"Could not fetch revenue for {ticker}: {e}")
        return None

if tickers and start_year <= end_year:
    st.subheader("📥 Fetching Revenue Data...")
    revenue_data = []

    for ticker in tickers:
        rev = get_revenue_data(ticker)
        if rev is not None:
            rev = rev[(rev.index.year >= start_year) & (rev.index.year <= end_year)]
            revenue_data.append(rev)

    if revenue_data:
        df_revenue = pd.concat(revenue_data, axis=1)
        df_revenue = df_revenue.dropna(how='all')  # drop rows with all NaNs

        st.subheader("📊 Revenue Table")
        st.dataframe(df_revenue.style.format("${:,.0f}"))

        # Plot revenue trends
        st.subheader("📈 Revenue Trends")
        fig, ax = plt.subplots(figsize=(12, 6))
        df_revenue.plot(ax=ax, marker="o")
        ax.set_ylabel("Revenue (USD)")
        ax.set_title("Quarterly Revenue Trends")
        ax.grid(True)
        st.pyplot(fig)

        # Correlation heatmap
        st.subheader("🔗 Revenue Correlation Heatmap")
        corr = df_revenue.corr()
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax2)
        ax2.set_title("Correlation of Quarterly Revenues")
        st.pyplot(fig2)

    else:
        st.warning("No valid revenue data found for the selected tickers and date range.")
