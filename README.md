# Level 3 – Task 1: Predictive Sales Forecasting
**RaushByte Technologies – Data Analytics Internship**

---

## 📌 Objective
Predict future sales trends from historical data: analyze past sales patterns, build forecasts with uncertainty ranges, test which model is most accurate, and report the insights.

---

## ✅ Requirements Completed

| # | Requirement | Status |
|---|-------------|--------|
| 1 | Analyze historical sales patterns | ✅ Done |
| 2 | Create forecasting charts | ✅ Done |
| 3 | Predict future revenue trends | ✅ Done (12 months ahead) |
| 4 | Prepare insight reports | ✅ Done (dashboard + this README) |

---

## 📊 Dataset
- **File:** `data_analytics_sales_dataset`
- **Rows:** 8,000 orders | **Missing values:** 0 | **Duplicates:** 0
- **Period:** 1 Jan 2024 to 15 May 2025
- **Series built:** monthly revenue (Sales) overall, by region (4) and by product (5)
- **Model data:** 16 complete months (Jan 2024 to Apr 2025). May 2025 has only 15 of 31 days, so it is **excluded from model fitting** and used only as a cross-check.

---

## 📈 Key Findings

### 1. Historical sales pattern
| Metric | Value |
|--------|-------|
| Average month | ₹12.25 Cr |
| Month-to-month swing (CV) | 7.0% |
| Best month | Dec 2024 (₹13.81 Cr) |
| Worst month | Feb 2025 (₹10.38 Cr) |
| Trend | +₹2.2 L per month, **not statistically significant** (p = 0.65) |
| 2024 monthly average vs Jan–Apr 2025 | ₹12.31 Cr vs ₹12.06 Cr |

**Revenue is a stable level with normal monthly noise, not a growing or shrinking trend.** Orders (about 485 a month) and average order value (about ₹2.5L) are both flat as well.

### 2. Model comparison (rolling-origin backtest, 1–3 months ahead)
| Model | MAE (₹ Cr) | RMSE (₹ Cr) | MAPE |
|-------|-----------|-------------|------|
| **Average level (all history)** | **0.95** | **1.12** | **7.7%** ✅ best |
| 3-month moving average | 1.08 | 1.32 | 9.0% |
| Linear trend | 1.10 | 1.33 | 9.0% |
| Exponential smoothing | 1.28 | 1.54 | 10.6% |
| Naive (last month) | 1.35 | 1.59 | 11.1% |
| Damped trend (Holt) | 1.48 | 1.82 | 12.4% |

The **simplest model won**. Trend-following models did worse because there is no real trend to follow, and chasing last month's value adds noise. This is an honest result: more complex does not mean better.

### 3. Forecast (starting after the end of the data)
| Month | Forecast | 80% range |
|-------|----------|-----------|
| May 2025 | ₹12.25 Cr | ₹10.82 – 13.68 Cr |
| Aug 2025 | ₹12.25 Cr | ₹10.59 – 13.90 Cr |
| Dec 2025 | ₹12.25 Cr | ₹9.91 – 14.58 Cr |
| Apr 2026 | ₹12.25 Cr | ₹9.39 – 15.11 Cr |
| **Next 12 months** | **₹146.97 Cr** | vs ₹147.80 Cr in the same 12 months before (−0.6%) |

**Cross-check:** May 2025 had ₹5.82 Cr in its first 15 days, a full-month pace of ₹12.02 Cr, only 1.9% below the ₹12.25 Cr forecast.

### 4. By region and product (best model per series)
| Series | Best model | MAPE | Avg month | 12-month forecast | Trend p-value |
|--------|-----------|------|-----------|-------------------|---------------|
| All sales | Average level | 7.7% | ₹12.25 Cr | ₹146.97 Cr | 0.65 |
| North | 3-month moving avg | 10.3% | ₹3.01 Cr | ₹36.62 Cr | 0.21 |
| South | 3-month moving avg | 13.7% | ₹3.06 Cr | ₹34.65 Cr | 0.60 |
| East | Average level | 18.0% | ₹3.06 Cr | ₹36.74 Cr | 0.55 |
| West | Average level | 10.9% | ₹3.12 Cr | ₹37.39 Cr | 0.95 |
| Headphones | Exp. smoothing | 8.9% | ₹2.59 Cr | ₹30.93 Cr | 0.27 |
| Laptop | Average level | 13.7% | ₹2.40 Cr | ₹28.81 Cr | 0.86 |
| Mobile | Average level | 14.4% | ₹2.24 Cr | ₹26.86 Cr | 0.96 |
| Smartwatch | Average level | 11.3% | ₹2.47 Cr | ₹29.67 Cr | 0.36 |
| Tablet | Average level | 11.2% | ₹2.55 Cr | ₹30.58 Cr | 0.34 |

No region or product shows a significant trend. Smaller series are noisier, so their forecasts are less accurate (East is the least predictable at 18% error).

### 5. Business takeaways
- **Plan for roughly ₹12 Cr a month**, with ±₹1.4 Cr as normal variation. Do not budget for growth the data does not show.
- **South is forecast ~7% below last year's level** (₹34.65 Cr vs ₹37.33 Cr) because recent months were weaker. Worth watching, but not proven by the data.
- **Forecast ranges are the useful output**, not the single number. Use the low end for cost planning and the high end for capacity planning.

### ⚠️ Limitations
- Only 16 full months exist, so **seasonality cannot be confirmed**. December was the best month, but one year is not enough to call it a pattern.
- Forecasts assume conditions stay similar (no price changes, campaigns or market shifts).
- Intervals beyond 3 months are extrapolated, because the backtest can only measure up to 3 months ahead.

---

## 🖥️ Dashboard Features

- **Controls:** series (all, 4 regions, 5 products), model (auto-best or any of 6), horizon (3 / 6 / 12 months), interval (80% / 95%)
- **6 KPI cards:** next-month forecast, horizon total vs last year, average month, trend, backtest error, May run rate
- **Charts:** history + forecast with prediction band, forecast table, model comparison, backtest predicted vs actual, orders and average order value, historical pattern summary
- **"What this view says"** panel that rewrites itself for every selection
- Works offline, no install, light and dark mode

---

## 📁 Project Structure

```
Level3-Task1-Predictive-Sales-Forecasting/
│
├── dashboard.html          ← Interactive forecasting dashboard (results embedded)
├── sales_forecasting.py    ← Python script: patterns, 6 models, backtest, forecast
├── README.md               ← This file
└── requirements.txt        ← Python dependencies
```

---

## 🚀 How to Use

**Open the dashboard:** download `dashboard.html` and double-click it.

**Re-run the forecasting (optional):**
```bash
pip install -r requirements.txt
python sales_forecasting.py data_analytics_sales_dataset.xlsx
```
This prints the pattern summary, backtest table and forecast, and saves `forecast_results.json`.

---

## 🛠️ Tools Used

- **Python 3** (pandas, NumPy, SciPy): monthly aggregation, six forecasting models, rolling-origin backtest, trend significance tests
- **HTML + CSS + JavaScript:** interactive dashboard with hand-built SVG charts (no external libraries)

---

*Level 3 – Task 1 | RaushByte Technologies Data Analytics Internship*
