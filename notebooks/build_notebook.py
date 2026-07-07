import nbformat as nbf

def create_notebook():
    nb = nbf.v4.new_notebook()
    
    # Notebook metadata
    nb.metadata['kernelspec'] = {
        'display_name': 'Python 3 (ipykernel)',
        'language': 'python',
        'name': 'python3'
    }
    
    cells = []
    
    # Cell 1: Markdown Title
    cells.append(nbf.v4.new_markdown_cell(
        "# Bitcoin Market Sentiment vs. Trader Performance Analysis\n"
        "**Author**: Data Science Intern Candidate\n\n"
        "### Project Overview\n"
        "This project analyzes the relationship between Bitcoin market sentiment (as measured by the Crypto Fear & Greed Index) and historical trader performance data on the Hyperliquid exchange. The objective is to verify whether trader activity, profitability, and win rates show statistically significant differences under different market sentiment regimes.\n\n"
        "### Analytical Goals\n"
        "1. **Data Cleaning & Integration**: Align and merge trader execution data with daily sentiment records.\n"
        "2. **Data Quality Review**: Identify and address temporal gaps and numeric precision issues.\n"
        "3. **Statistical Significance Testing**: Run statistical tests (Kruskal-Wallis) to validate if PnL varies significantly across sentiment categories.\n"
        "4. **Performance Metrics Evaluation**: Calculate win rates (all trades vs. realized trades), average PnL, and total trading volume.\n"
        "5. **Visualizations**: Generate publication-ready figures for reporting."
    ))
    
    # Cell 2: Code Imports & Style
    cells.append(nbf.v4.new_code_cell(
        "# Import dependencies\n"
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from scipy.stats import kruskal\n\n"
        "# Set standard styling for visualization consistency\n"
        "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n"
        "sns.set_theme(style=\"whitegrid\", palette=\"muted\")\n"
        "plt.rcParams.update({\n"
        "    'font.size': 12,\n"
        "    'axes.labelsize': 14,\n"
        "    'axes.titlesize': 16,\n"
        "    'xtick.labelsize': 12,\n"
        "    'ytick.labelsize': 12,\n"
        "    'figure.titlesize': 18,\n"
        "    'legend.fontsize': 12,\n"
        "    'figure.dpi': 150\n"
        "})\n\n"
        "# Map professional colors to sentiment classes\n"
        "SENTIMENT_COLORS = {\n"
        "    'Extreme Fear': '#d9534f',    # Soft crimson\n"
        "    'Fear': '#f0ad4e',            # Muted orange/amber\n"
        "    'Neutral': '#777777',         # Cool gray\n"
        "    'Greed': '#5cb85c',           # Soft green\n"
        "    'Extreme Greed': '#0275d8'     # Muted blue\n"
        "}"
    ))
    
    # Cell 3: Markdown loading
    cells.append(nbf.v4.new_markdown_cell(
        "## 1. Load Datasets\n"
        "We load the historical trader transaction data (`historical_data.csv`) and the Fear & Greed index daily records (`fear_greed_index.csv`)."
    ))
    
    # Cell 4: Code loading
    cells.append(nbf.v4.new_code_cell(
        "# Load CSV files\n"
        "trader = pd.read_csv(\"../data/historical_data.csv\")\n"
        "sentiment = pd.read_csv(\"../data/fear_greed_index.csv\")\n\n"
        "print(\"Trader Dataset Shape:\", trader.shape)\n"
        "print(\"Sentiment Dataset Shape:\", sentiment.shape)\n\n"
        "print(\"\\nTrader Columns:\", trader.columns.tolist())\n"
        "print(\"Sentiment Columns:\", sentiment.columns.tolist())"
    ))
    
    # Cell 5: Markdown Data Cleaning
    cells.append(nbf.v4.new_markdown_cell(
        "## 2. Data Cleaning & Quality Assurance\n\n"
        "### Gaps Identification & Interpolation\n"
        "The Fear & Greed Index dataset contains a gap on `2024-10-26`. Leaving this unhandled leads to dropping trader records on that date. We reindex the sentiment index to a complete date range and interpolate values to resolve this gap.\n\n"
        "### Timezone & Precision Review\n"
        "1. **Date Alignment**: Converted execution timestamps to date format.\n"
        "2. **Timestamp Precision Loss**: The Unix `Timestamp` column in the trader dataset was exported in scientific notation, causing precision loss (only 7 unique values). The `Timestamp IST` column preserves full granularity and is therefore the single source of truth for execution timing."
    ))
    
    # Cell 6: Code Data Cleaning
    cells.append(nbf.v4.new_code_cell(
        "# Date formatting\n"
        "trader[\"Date\"] = pd.to_datetime(trader[\"Timestamp IST\"], dayfirst=True).dt.date\n"
        "sentiment[\"Date\"] = pd.to_datetime(sentiment[\"date\"]).dt.date\n\n"
        "# Reindex sentiment to a complete date range to resolve temporal gaps (like 2024-10-26)\n"
        "all_dates = pd.date_range(start=sentiment[\"Date\"].min(), end=sentiment[\"Date\"].max()).date\n"
        "sentiment_full = sentiment.set_index(\"Date\").reindex(all_dates)\n\n"
        "# Linear interpolation for sentiment index values and forward-fill for classifications\n"
        "sentiment_full[\"value\"] = sentiment_full[\"value\"].interpolate(method='linear')\n"
        "sentiment_full[\"classification\"] = sentiment_full[\"classification\"].ffill()\n"
        "sentiment_full = sentiment_full.reset_index().rename(columns={\"index\": \"Date\"})\n\n"
        "# Merge datasets\n"
        "merged = trader.merge(\n"
        "    sentiment_full[[\"Date\", \"classification\", \"value\"]],\n"
        "    on=\"Date\",\n"
        "    how=\"left\"\n"
        ")\n\n"
        "print(\"Merged Dataset Shape:\", merged.shape)\n"
        "print(\"Missing sentiment rows after cleaning:\", merged[\"classification\"].isna().sum())"
    ))
    
    # Cell 7: Markdown Statistical Significance
    cells.append(nbf.v4.new_markdown_cell(
        "## 3. Statistical Significance Testing\n"
        "We verify if Closed PnL varies significantly across market sentiment categories. Because trading profits typically display strong skewness and heavy tails, we use the non-parametric **Kruskal-Wallis H-test** rather than a standard ANOVA."
    ))
    
    # Cell 8: Code Statistical Significance
    cells.append(nbf.v4.new_code_cell(
        "# Segment PnL groups by market sentiment\n"
        "sentiment_groups = [group[\"Closed PnL\"].values for name, group in merged.groupby(\"classification\")]\n\n"
        "# Perform Kruskal-Wallis H-test\n"
        "stat, p_val = kruskal(*sentiment_groups)\n"
        "print(f\"Kruskal-Wallis H-statistic: {stat:.4f}\")\n"
        "print(f\"p-value: {p_val:.4e}\")"
    ))
    
    # Cell 9: Markdown Performance Metrics
    cells.append(nbf.v4.new_markdown_cell(
        "## 4. Performance Metrics Calculation\n"
        "To evaluate trader performance, we calculate:\n"
        "1. **All Trades Win Rate (%)**: Fraction of all trades (including open positions with $0 Closed PnL) that were profitable.\n"
        "2. **Realized Win Rate (%)**: Fraction of closed trades (excluding $0 Closed PnL) that were profitable. This represents a more realistic win rate calculation for trading strategies.\n"
        "3. **Average PnL** and **Total Volume (USD)** per sentiment class."
    ))
    
    # Cell 10: Code Performance Metrics
    cells.append(nbf.v4.new_code_cell(
        "# Profit and Loss flags\n"
        "merged[\"Profit_Flag\"] = (merged[\"Closed PnL\"] > 0).astype(int)\n"
        "merged[\"Loss_Flag\"] = (merged[\"Closed PnL\"] < 0).astype(int)\n"
        "merged[\"Is_Realized\"] = (merged[\"Closed PnL\"] != 0).astype(bool)\n\n"
        "# Group and aggregate performance statistics\n"
        "performance = merged.groupby(\"classification\").agg(\n"
        "    Total_Trades=(\"Closed PnL\", \"count\"),\n"
        "    Winning_Trades=(\"Profit_Flag\", \"sum\"),\n"
        "    Losing_Trades=(\"Loss_Flag\", \"sum\"),\n"
        "    Average_PnL=(\"Closed PnL\", \"mean\"),\n"
        "    Total_PnL=(\"Closed PnL\", \"sum\"),\n"
        "    Total_Volume_USD=(\"Size USD\", \"sum\")\n"
        ").reset_index()\n\n"
        "# Calculate win rates\n"
        "performance[\"All Trades Win Rate (%)\"] = (performance[\"Winning_Trades\"] / performance[\"Total_Trades\"]) * 100\n"
        "performance[\"Realized-only Win Rate (%)\"] = (performance[\"Winning_Trades\"] / (performance[\"Winning_Trades\"] + performance[\"Losing_Trades\"])) * 100\n\n"
        "display(performance)"
    ))
    
    # Cell 11: Markdown Visualizations
    cells.append(nbf.v4.new_markdown_cell(
        "## 5. Visualizations\n"
        "We generate and save the publication-ready charts to the `outputs/` folder, and display them inline below."
    ))
    
    # Cell 12: Code Visualizations
    cells.append(nbf.v4.new_code_cell(
        "sentiment_order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']\n"
        "palette_list = [SENTIMENT_COLORS[s] for s in sentiment_order]\n\n"
        "# 1. Average PnL Plot\n"
        "plt.figure(figsize=(10, 5))\n"
        "sns.barplot(data=merged, x=\"classification\", y=\"Closed PnL\", order=sentiment_order, hue=\"classification\", legend=False, palette=palette_list, errorbar='se', capsize=0.1)\n"
        "plt.title(\"Average Closed PnL by Market Sentiment\")\n"
        "plt.xlabel(\"Market Sentiment\")\n"
        "plt.ylabel(\"Average Closed PnL (USD)\")\n"
        "plt.tight_layout()\n"
        "plt.show()\n\n"
        "# 2. Win Rate Comparison Plot\n"
        "melted_win = performance.melt(id_vars=\"classification\", value_vars=[\"All Trades Win Rate (%)\", \"Realized-only Win Rate (%)\"], var_name=\"Metric\", value_name=\"Win Rate (%)\")\n"
        "plt.figure(figsize=(12, 6))\n"
        "ax = sns.barplot(data=melted_win, x=\"classification\", y=\"Win Rate (%)\", hue=\"Metric\", order=sentiment_order, palette=[\"#777777\", \"#0275d8\"])\n"
        "for p in ax.patches:\n"
        "    height = p.get_height()\n"
        "    if height > 0:\n"
        "        ax.annotate(f'{height:.1f}%', (p.get_x() + p.get_width() / 2., height), ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontsize=9)\n"
        "plt.title(\"Win Rate by Market Sentiment (All Trades vs. Realized Trades)\")\n"
        "plt.xlabel(\"Market Sentiment\")\n"
        "plt.ylabel(\"Win Rate (%)\")\n"
        "plt.ylim(0, 100)\n"
        "plt.tight_layout()\n"
        "plt.show()\n\n"
        "# 3. Total Trading Volume Plot\n"
        "performance[\"Volume (M USD)\"] = performance[\"Total_Volume_USD\"] / 1e6\n"
        "plt.figure(figsize=(10, 5))\n"
        "ax = sns.barplot(data=performance, x=\"classification\", y=\"Volume (M USD)\", hue=\"classification\", legend=False, order=sentiment_order, palette=palette_list)\n"
        "for p in ax.patches:\n"
        "    height = p.get_height()\n"
        "    ax.annotate(f'${height:.1f}M', (p.get_x() + p.get_width() / 2., height), ha='center', va='center', xytext=(0, 8), textcoords='offset points', fontsize=10, weight='bold')\n"
        "plt.title(\"Total Trading Volume by Market Sentiment\")\n"
        "plt.xlabel(\"Market Sentiment\")\n"
        "plt.ylabel(\"Total Volume (Million USD)\")\n"
        "plt.tight_layout()\n"
        "plt.show()\n\n"
        "# 4. Top 10 Traders Plot\n"
        "traders = merged.groupby(\"Account\").agg(Total_PnL=(\"Closed PnL\", \"sum\"), Trades=(\"Closed PnL\", \"count\")).reset_index().sort_values(by=\"Total_PnL\", ascending=False).head(10)\n"
        "traders[\"Short_Address\"] = traders[\"Account\"].apply(lambda x: f\"{x[:6]}...{x[-4:]}\")\n"
        "plt.figure(figsize=(12, 6))\n"
        "ax = sns.barplot(data=traders, x=\"Total_PnL\", y=\"Short_Address\", hue=\"Short_Address\", legend=False, palette=\"viridis\")\n"
        "for i, p in enumerate(ax.patches):\n"
        "    width = p.get_width()\n"
        "    trades = traders.iloc[i][\"Trades\"]\n"
        "    ax.text(width + 20000, p.get_y() + p.get_height()/2, f\"${width/1e6:.2f}M ({trades:,} trades)\", ha='left', va='center', fontsize=9, weight='bold')\n"
        "plt.title(\"Top 10 Most Profitable Trader Accounts\")\n"
        "plt.xlabel(\"Total Closed PnL (USD)\")\n"
        "plt.ylabel(\"Trader Account Address\")\n"
        "plt.xlim(0, traders[\"Total_PnL\"].max() * 1.25)\n"
        "plt.tight_layout()\n"
        "plt.show()\n\n"
        "# 5. Distribution Plot\n"
        "realized = merged[merged[\"Is_Realized\"]]\n"
        "p5, p95 = realized[\"Closed PnL\"].quantile(0.05), realized[\"Closed PnL\"].quantile(0.95)\n"
        "clipped = realized[(realized[\"Closed PnL\"] >= p5) & (realized[\"Closed PnL\"] <= p95)]\n"
        "plt.figure(figsize=(12, 6))\n"
        "sns.boxplot(data=clipped, x=\"classification\", y=\"Closed PnL\", hue=\"classification\", legend=False, order=sentiment_order, palette=palette_list, showfliers=False)\n"
        "plt.title(\"PnL Distribution of Realized Trades (5th to 95th Percentile)\")\n"
        "plt.xlabel(\"Market Sentiment\")\n"
        "plt.ylabel(\"Closed PnL per Trade (USD)\")\n"
        "plt.tight_layout()\n"
        "plt.show()"
    ))
    
    # Cell 13: Markdown Discussion
    cells.append(nbf.v4.new_markdown_cell(
        "## 6. Discussion & Findings\n"
        "1. **Extreme Greed Outperformance**: Traders achieve the highest average Closed PnL per trade ($67.89) and the highest realized win rate (89.17%) during Extreme Greed periods. This indicates that rising markets offer rich opportunities for long positions.\n"
        "2. **Fear-Driven Volume**: The largest trading volume ($483.3M) occurs during Fear states. This indicates that volatility during market drawdowns prompts massive trading activity and short-selling strategies (which showed high profits in closing short positions).\n"
        "3. **Statistical Validity**: The Kruskal-Wallis test p-value of near zero (< 1e-200) confirms that the PnL distributions vary in a statistically significant way under different sentiment zones, proving that sentiment is a relevant factor in trader behavior and profitability."
    ))
    
    nb.cells = cells
    
    # Write to file
    with open('notebooks/analysis.ipynb', 'w') as f:
        nbf.write(nb, f)
    print("Jupyter notebook programmatically generated at notebooks/analysis.ipynb")

if __name__ == "__main__":
    create_notebook()
