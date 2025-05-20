import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(page_title="Revenue Correlation App", layout="wide")
st.title("📊 Revenue Correlation Analysis")

# Sidebar inputs
tickers_input = st.sidebar.text_area(
    "Enter stock tickers (comma-separated):",
    value="AAPL, MSFT, GOOGL, AMZN, META, NVDA"
)

start_year = st.sidebar.selectbox("Select start year", list(range(2015, 2025))[::-1])
end_year = st.sidebar.selectbox("Select end year", list(range(2015, 2025))[::-1])

if start_year > end_year:
    st.sidebar.error("Start year must be before or equal to end year")

tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# Button to run analysis
run_button = st.button("📥 Run Revenue Correlation Analysis")

# Function to fetch and process revenue data
def get_revenue_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.quarterly_financials.T
        df.index = pd.to_datetime(df.index)
        revenue = df["Total Revenue"]
        revenue.name = ticker
        return revenue.sort_index()
    except Exception as e:
        st.warning(f"Could not fetch revenue for {ticker}: {e}")
        return None

# Generate standard quarter-end dates
def get_quarter_end_dates(start, end):
    return pd.date_range(start=f"{start}-01-01", end=f"{end}-12-31", freq="Q")

# Main analysis logic
if run_button and tickers:
    st.subheader("⏳ Fetching and Aligning Revenue Data...")

    # Generate calendar-based quarter-end dates
    calendar_dates = get_quarter_end_dates(start_year, end_year)
    aligned_revenues = pd.DataFrame(index=calendar_dates)

    for ticker in tickers:
        rev = get_revenue_data(ticker)
        if rev is not None:
            # Align each ticker’s revenue to standard quarter-ends using forward-fill logic
            reindexed = rev.reindex(calendar_dates, method='ffill')
            aligned_revenues[ticker] = reindexed

    aligned_revenues = aligned_revenues.dropna(how='all')

    if not aligned_revenues.empty:
        st.subheader("📊 Aligned Revenue Table")
        st.dataframe(aligned_revenues.style.format("${:,.0f}"))

        # 📈 Revenue trend chart
        st.subheader("📈 Revenue Trend Line Chart")
        fig_trend, ax_trend = plt.subplots(figsize=(12, 6))
        aligned_revenues.plot(ax=ax_trend, marker="o", linewidth=2)
        ax_trend.set_title("Quarterly Revenue Trends (Aligned to Quarter-End)")
        ax_trend.set_ylabel("Revenue (USD)")
        ax_trend.grid(True)
        st.pyplot(fig_trend)

        # 🔗 Correlation heatmap
        st.subheader("🔗 Revenue Correlation Heatmap")
        corr = aligned_revenues.corr()
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_corr)
        ax_corr.set_title("Correlation of Quarterly Revenues")
        st.pyplot(fig_corr)

        st.success("✅ Analysis Complete")

    else:
        st.warning("⚠️ No revenue data found for the selected tickers and time range.")