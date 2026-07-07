import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import kruskal

# Set standard plotting style for publication-quality charts
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'figure.titlesize': 18,
    'legend.fontsize': 12,
    'figure.dpi': 150
})

# Custom high-contrast professional color palette matching market sentiment
SENTIMENT_COLORS = {
    'Extreme Fear': '#d9534f',    # Soft crimson
    'Fear': '#f0ad4e',            # Muted orange/amber
    'Neutral': '#777777',         # Cool gray
    'Greed': '#5cb85c',           # Soft green
    'Extreme Greed': '#0275d8'     # Muted blue
}

def load_and_clean_data(historical_path='data/historical_data.csv', sentiment_path='data/fear_greed_index.csv'):
    """
    Loads, cleans, and merges historical trading data with market sentiment data.
    Performs interpolation to fill the missing date (2024-10-26) in sentiment index.
    """
    print("Loading datasets...")
    trader = pd.read_csv(historical_path)
    sentiment = pd.read_csv(sentiment_path)
    
    # Date formatting
    trader["Date"] = pd.to_datetime(trader["Timestamp IST"], dayfirst=True).dt.date
    sentiment["Date"] = pd.to_datetime(sentiment["date"]).dt.date
    
    # 1. Handle gap in sentiment dataset (2024-10-26 is missing)
    # Generate complete date range for sentiment dataset to identify gaps
    min_date = sentiment["Date"].min()
    max_date = sentiment["Date"].max()
    all_dates = pd.date_range(start=min_date, end=max_date).date
    
    # Reindex sentiment dataset to ensure no missing dates
    sentiment_full = sentiment.set_index("Date").reindex(all_dates)
    
    # Interpolate values (linear) and forward fill classifications
    sentiment_full["value"] = sentiment_full["value"].interpolate(method='linear')
    sentiment_full["classification"] = sentiment_full["classification"].ffill()
    sentiment_full = sentiment_full.reset_index().rename(columns={"index": "Date"})
    
    # Merge datasets
    merged = trader.merge(
        sentiment_full[["Date", "classification", "value"]],
        on="Date",
        how="left"
    )
    
    # Verify missing values after cleaning
    missing_sentiment = merged["classification"].isna().sum()
    print(f"Merged Dataset Shape: {merged.shape}")
    print(f"Missing sentiment records after cleaning: {missing_sentiment}")
    
    # 2. Add Profit/Loss flags and categorize realized trades
    merged["Profit_Flag"] = (merged["Closed PnL"] > 0).astype(int)
    merged["Loss_Flag"] = (merged["Closed PnL"] < 0).astype(int)
    merged["Is_Realized"] = (merged["Closed PnL"] != 0).astype(bool)
    
    return merged

def run_statistical_tests(merged):
    """
    Runs Kruskal-Wallis non-parametric test to check statistical significance of PnL variations.
    """
    print("\n--- Statistical Significance Test ---")
    groups = [group["Closed PnL"].values for name, group in merged.groupby("classification")]
    stat, p_val = kruskal(*groups)
    print(f"Kruskal-Wallis H-statistic: {stat:.4f}")
    print(f"p-value: {p_val:.4e}")
    if p_val < 0.05:
        print("Insight: The distribution of Closed PnL across market sentiments is statistically significant (p < 0.05).")
    else:
        print("Insight: No statistically significant difference in Closed PnL across market sentiments.")
    return stat, p_val

def generate_visualizations(merged, output_dir='outputs'):
    """
    Generates and saves professional charts to outputs/ directory.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Categorical ordering for charts
    sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    palette_list = [SENTIMENT_COLORS[s] for s in sentiment_order]
    
    # 1. Average PnL by Sentiment (with standard error bars)
    print("Generating Chart: Average PnL by Sentiment...")
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=merged,
        x="classification",
        y="Closed PnL",
        order=sentiment_order,
        palette=palette_list,
        errorbar='se',
        capsize=0.1
    )
    plt.title("Average Closed PnL by Market Sentiment", pad=15)
    plt.xlabel("Market Sentiment Classification")
    plt.ylabel("Average Closed PnL (USD)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/average_pnl_by_sentiment.png", dpi=300)
    plt.close()
    
    # 2. Win Rate by Sentiment (Grouped Bar Chart: All Trades vs Realized Trades)
    print("Generating Chart: Win Rate by Sentiment...")
    win_stats = merged.groupby("classification").agg(
        Total_Trades=("Closed PnL", "count"),
        Winning_Trades=("Profit_Flag", "sum"),
        Losing_Trades=("Loss_Flag", "sum")
    ).reindex(sentiment_order).reset_index()
    
    win_stats["All Trades Win Rate (%)"] = (win_stats["Winning_Trades"] / win_stats["Total_Trades"]) * 100
    win_stats["Realized-only Win Rate (%)"] = (win_stats["Winning_Trades"] / (win_stats["Winning_Trades"] + win_stats["Losing_Trades"])) * 100
    
    # Melt for side-by-side plotting
    melted_win = win_stats.melt(
        id_vars="classification",
        value_vars=["All Trades Win Rate (%)", "Realized-only Win Rate (%)"],
        var_name="Metric",
        value_name="Win Rate (%)"
    )
    
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=melted_win,
        x="classification",
        y="Win Rate (%)",
        hue="Metric",
        order=sentiment_order,
        palette=["#777777", "#0275d8"]  # Cool Gray vs Deep Blue
    )
    
    # Annotate bars
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.1f}%',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center',
                        xytext=(0, 8),
                        textcoords='offset points',
                        fontsize=10)
            
    plt.title("Trading Win Rate by Market Sentiment (All Trades vs. Realized Trades)", pad=15)
    plt.xlabel("Market Sentiment Classification")
    plt.ylabel("Win Rate (%)")
    plt.ylim(0, 100)
    plt.legend(title="Methodology", frameon=True)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/win_rate_by_sentiment.png", dpi=300)
    plt.close()
    
    # 3. Trading Volume by Sentiment
    print("Generating Chart: Trading Volume by Sentiment...")
    volume_stats = merged.groupby("classification")["Size USD"].sum().reindex(sentiment_order) / 1e6
    volume_df = volume_stats.reset_index().rename(columns={"Size USD": "Volume (M USD)"})
    
    plt.figure(figsize=(10, 6))
    ax = sns.barplot(
        data=volume_df,
        x="classification",
        y="Volume (M USD)",
        order=sentiment_order,
        palette=palette_list
    )
    
    # Annotate volume values
    for p in ax.patches:
        height = p.get_height()
        ax.annotate(f'${height:.1f}M',
                    (p.get_x() + p.get_width() / 2., height),
                    ha='center', va='center',
                    xytext=(0, 8),
                    textcoords='offset points',
                    fontsize=11,
                    weight='bold')
                    
    plt.title("Total Trading Volume by Market Sentiment", pad=15)
    plt.xlabel("Market Sentiment Classification")
    plt.ylabel("Total Volume (Million USD)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/trading_volume_by_sentiment.png", dpi=300)
    plt.close()
    
    # 4. Top 10 Traders by Total PnL
    print("Generating Chart: Top 10 Traders by PnL...")
    traders_stats = merged.groupby("Account").agg(
        Total_PnL=("Closed PnL", "sum"),
        Trades_Count=("Closed PnL", "count")
    ).reset_index().sort_values(by="Total_PnL", ascending=False).head(10)
    
    # Shorten addresses for labels
    traders_stats["Short_Address"] = traders_stats["Account"].apply(lambda x: f"{x[:6]}...{x[-4:]}")
    
    plt.figure(figsize=(12, 7))
    ax = sns.barplot(
        data=traders_stats,
        x="Total_PnL",
        y="Short_Address",
        palette="viridis"
    )
    
    # Annotate bar values with trade counts and profits
    for i, p in enumerate(ax.patches):
        width = p.get_width()
        trades = traders_stats.iloc[i]["Trades_Count"]
        ax.text(width + 20000, p.get_y() + p.get_height()/2,
                f"${width/1e6:.2f}M ({trades:,} trades)",
                ha='left', va='center', fontsize=10, weight='bold')
                
    plt.title("Top 10 Most Profitable Trader Accounts (by Total Closed PnL)", pad=15)
    plt.xlabel("Total Closed PnL (USD)")
    plt.ylabel("Trader Account Address (Truncated)")
    # Extend x-axis slightly for labels
    plt.xlim(0, traders_stats["Total_PnL"].max() * 1.25)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/top_10_traders_by_pnl.png", dpi=300)
    plt.close()
    
    # 5. PnL Distribution (Box Plot focusing on the 5th-95th percentile range to handle outliers)
    print("Generating Chart: PnL Distribution...")
    realized_trades = merged[merged["Is_Realized"]].copy()
    
    # Clip extreme outliers for visual clarity, but document the full range
    p5 = realized_trades["Closed PnL"].quantile(0.05)
    p95 = realized_trades["Closed PnL"].quantile(0.95)
    clipped_trades = realized_trades[(realized_trades["Closed PnL"] >= p5) & (realized_trades["Closed PnL"] <= p95)]
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(
        data=clipped_trades,
        x="classification",
        y="Closed PnL",
        order=sentiment_order,
        palette=palette_list,
        showfliers=False  # Hide remaining outliers to focus on box shape
    )
    plt.title("Closed PnL Distribution of Realized Trades (5th to 95th Percentiles)", pad=15)
    plt.xlabel("Market Sentiment Classification")
    plt.ylabel("Closed PnL per Trade (USD)")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/pnl_distribution_by_sentiment.png", dpi=300)
    plt.close()
    
    print("All visualizations generated and saved successfully!")

if __name__ == "__main__":
    df = load_and_clean_data()
    run_statistical_tests(df)
    generate_visualizations(df)
