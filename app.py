import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page setup
st.set_page_config(page_title="Revenue Correlation App", layout="wide")
st.title("📊 Financial Metric Correlation Analysis")

# Sidebar inputs
tickers_input = st.sidebar.text_area(
    "Enter stock tickers (comma-separated):",
    value="AAPL, MSFT, GOOGL, AMZN, META, NVDA"
)

start_year = st.sidebar.selectbox("Select start year", list(range(2015, 2026))[::-1])
end_year = st.sidebar.selectbox("Select end year", list(range(2015, 2026))[::-1])

# Metric selection
metric_map = {
    "Total Revenue": "Total Revenue",
    "Cost of Revenue": "Cost Of Revenue",
    "Gross Profit": "Gross Profit",
    "EBIT (Operating Income)": "Operating Income",
    "EBITDA": "EBITDA"
}

selected_metric_label = st.sidebar.selectbox("Select financial metric to analyze:", list(metric_map.keys()))
selected_metric = metric_map[selected_metric_label]

# Normalization option
normalize_data = st.sidebar.checkbox("Normalize values for better comparison", value=True)

# Ticker processing
if start_year > end_year:
    st.sidebar.error("Start year must be before or equal to end year")

tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]
run_button = st.button(f"📥 Run {selected_metric_label} Correlation Analysis")

# Fetch and process financial data
def get_metric_data(ticker, metric_name):
    try:
        stock = yf.Ticker(ticker)
        df = stock.quarterly_financials.T
        df.index = pd.to_datetime(df.index)
        if metric_name in df.columns:
            data = df[metric_name]
            data.name = ticker
            return data.sort_index()
        else:
            st.warning(f"{metric_name} not available for {ticker}")
            return None
    except Exception as e:
        st.warning(f"Could not fetch data for {ticker}: {e}")
        return None

# Generate quarter-end calendar
def get_quarter_end_dates(start, end):
    return pd.date_range(start=f"{start}-01-01", end=f"{end}-12-31", freq="Q")

# Run analysis
if run_button and tickers:
    st.subheader(f"⏳ Fetching and aligning '{selected_metric_label}' data...")

    calendar_dates = get_quarter_end_dates(start_year, end_year)
    aligned_data = pd.DataFrame(index=calendar_dates)

    for ticker in tickers:
        data = get_metric_data(ticker, selected_metric)
        if data is not None:
            aligned = data.reindex(calendar_dates, method='ffill')
            aligned_data[ticker] = aligned

    aligned_data = aligned_data.dropna(how='all')

    if not aligned_data.empty:
        st.subheader(f"📊 Aligned {selected_metric_label} Table")
        st.dataframe(aligned_data.style.format("${:,.0f}"))

        # 📈 Line chart
        st.subheader(f"📈 {selected_metric_label} Trend Line Chart")
        fig_trend, ax_trend = plt.subplots(figsize=(12, 6))

        plot_data = aligned_data.copy()

        if normalize_data:
            plot_data = plot_data.divide(plot_data.max())

        plot_data.plot(ax=ax_trend, marker="o", linewidth=2)
        ax_trend.set_title(
            f"{selected_metric_label} Trend Over Time" +
            (" (Normalized)" if normalize_data else "")
        )
        ax_trend.set_ylabel("Normalized Value" if normalize_data else f"{selected_metric_label} (USD)")
        ax_trend.grid(True)
        st.pyplot(fig_trend)

        # 🔗 Correlation heatmap
        st.subheader(f"🔗 {selected_metric_label} Correlation Heatmap")
        corr = aligned_data.corr()
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax_corr)
        ax_corr.set_title(f"Correlation of Quarterly {selected_metric_label}")
        st.pyplot(fig_corr)

        st.success("✅ Analysis Complete")
    else:
        st.warning("⚠️ No valid data found for the selected tickers and metric.")
