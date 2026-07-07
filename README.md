# Bitcoin Market Sentiment vs. Trader Performance Analysis

An empirical study of Hyperliquid derivative trading performance analyzed against the Bitcoin Fear & Greed Index, submitted for a Data Science Internship review.

---

## 1. Project Overview
This repository analyzes the relationship between market sentiment (as measured by the Crypto Fear & Greed Index) and historical trader performance data on the Hyperliquid exchange. The objective is to verify whether trader activity, profitability, and win rates show statistically significant differences under different market sentiment regimes.

By integrating derivative trading executions with daily sentiment metrics, this study addresses:
1. **Profitability Correlation**: Does average profit-and-loss (Closed PnL) vary with sentiment zones?
2. **Win Rate Analysis**: Are win rates higher in bullish states (Extreme Greed) compared to bearish states (Extreme Fear)?
3. **Volume and Volatility**: Under which sentiment zones do traders deploy the most capital?
4. **Statistical Validity**: Are these differences statistically significant, or are they random?

---

## 2. Industry-Standard Repository Structure
To meet professional hiring-assignment standards, this repository is organized as follows:
```text
bitcoin_sentiment_analysis/
├── data/                       # Raw immutable data files
│   ├── fear_greed_index.csv    # Crypto Fear & Greed daily index values (2018-2025)
│   └── historical_data.csv    # Hyperliquid trader transactions (2023-2025)
├── notebooks/                  # Jupyter notebooks for interactive analysis
│   └── analysis.ipynb          # Executed, clean, and fully annotated analysis notebook
├── outputs/                    # Output visual artifacts (PNG plots)
│   ├── average_pnl_by_sentiment.png
│   ├── win_rate_by_sentiment.png
│   ├── trading_volume_by_sentiment.png
│   ├── top_10_traders_by_pnl.png
│   └── pnl_distribution_by_sentiment.png
├── report/                     # Publication-grade reporting materials
│   ├── final_report.pdf        # Automatically compiled report with embedded charts and stats
│   └── generate_report.py      # Python ReportLab script to generate the final PDF report
├── src/                        # Modular Python source code
│   └── data_processing.py      # Production-ready data cleaning and plotting module
├── .gitignore                  # Standard configurations to ignore caches and checkpoints
├── README.md                   # Recruiter/hiring manager documentation (this file)
└── requirements.txt            # Locked Python environment dependencies
```

---

## 3. Dataset Description
* **Hyperliquid Historical Trader Data** (`data/historical_data.csv`)
  * **Size**: 211,224 transaction records (May 2023 to May 2025)
  * **Key Columns**: `Account` (address), `Closed PnL` (USD), `Size USD`, `Side` (BUY/SELL), `Direction` (Open/Close positions), `Timestamp IST` (execution date and time).
* **Bitcoin Fear & Greed Index** (`data/fear_greed_index.csv`)
  * **Size**: 2,644 daily historical observations (February 2018 to May 2025)
  * **Key Columns**: `value` (daily index score 0-100), `classification` (Extreme Fear, Fear, Neutral, Greed, Extreme Greed), `date`.

---

## 4. Methodology & Data Quality Assurance

### A. Data Quality Review & Gaps Handling
* **Gap Resolution**: The Crypto Fear & Greed Index daily records lacked an entry for **2024-10-26**. Without preprocessing, a standard left-join drops all trader executions on this date (6 rows). This gap was programmatically resolved using linear value interpolation and forward-filling classifications. The date was correctly filled as `Greed` (value `73`), preserving all trader executions.
* **Precision Loss Review**: The Unix `Timestamp` column in the raw trader dataset suffered scientific notation conversion limits during export (losing precision to only 7 unique values). The `Timestamp IST` column was identified as the single source of truth for full-resolution temporal alignment.

### B. Win Rate Methodologies
To provide analytical depth, we evaluate win rates under two distinct definitions:
1. **All Trades Win Rate (%)**: Includes all transaction executions (including position-opening trades which always carry a `$0.0` Closed PnL).
   $$\text{All Trades Win Rate} = \frac{\text{Profitable Trades}}{\text{Total Trade Executions}}$$
2. **Realized Win Rate (%)**: Excludes opening/non-pnl executions, focusing only on realized profit/loss trades.
   $$\text{Realized Win Rate} = \frac{\text{Profitable Trades}}{\text{Profitable Trades} + \text{Loss-Making Trades}}$$

### C. Statistical Significance Testing
Given that trading profits typically show severe skewness and heavy tails, standard ANOVA tests fail normality assumptions. We run the non-parametric **Kruskal-Wallis H-test** to verify whether Closed PnL distributions vary across sentiments in a statistically significant way.
* **Test Results**: H-statistic = **1,225.3291**, p-value = **5.1417e-264**
* **Conclusion**: With a p-value virtually zero ($p < 0.05$), we reject the null hypothesis. The differences in Closed PnL across sentiment classes are highly statistically significant.

---

## 5. Key Findings & Analytics

| Sentiment Classification | Total Trades | Avg Closed PnL (USD) | All-Trades Win % | Realized Win % | Total Volume (M USD) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Extreme Fear** | 21,400 | $34.54 | 37.1% | 76.2% | $114.5M |
| **Fear** | 61,837 | $54.29 | 42.1% | 87.3% | $483.3M |
| **Neutral** | 37,686 | $34.31 | 39.7% | 82.4% | $180.2M |
| **Greed** | 50,309 | $43.58 | 38.5% | 76.9% | $288.7M |
| **Extreme Greed** | 39,992 | $67.89 | 46.5% | 89.2% | $124.5M |

### Key Takeaways
1. **Extreme Greed Outperformance**: Traders achieve their highest average Closed PnL per transaction ($67.89) and the highest realized win rate (89.2%) during Extreme Greed states, reflecting strong bullish momentum.
2. **Fear-Driven Volume**: The largest trading volume ($483.3M across 61,837 trades) occurs during Fear states, indicating that traders increase capital deployment and derivatives activity during market drawdowns and volatile corrections.
3. **Concentration of Profits**: A tiny fraction of active accounts generate the vast majority of total profits. The top address (`0xb123...ed23`) generated over $2.14M in profits across 14,733 trades.

---

## 6. How to Reproduce the Analysis

### 1. Install Dependencies
Set up your python environment using the requirements file:
```bash
pip install -r requirements.txt
```

### 2. Run Data Processing & Rebuild Figures
Run the clean Python module to perform preprocessing, run significance tests, and save visual assets to `outputs/`:
```bash
python src/data_processing.py
```

### 3. Recompile the Jupyter Notebook
If you need to programmatically regenerate or check the notebook file:
```bash
python notebooks/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/analysis.ipynb
```

### 4. Generate the PDF Report
To compile the publication-grade PDF report programmatically:
```bash
python report/generate_report.py
```
This will compile a dynamic PDF containing matching tables, embedded charts, and analysis notes under `report/final_report.pdf`.
