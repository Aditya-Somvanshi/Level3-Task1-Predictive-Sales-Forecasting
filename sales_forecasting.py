"""
Level 3 - Task 1: Predictive Sales Forecasting
RaushByte Technologies - Data Analytics Internship

What this script does
  1. Aggregates the 8,000 orders into monthly revenue (overall, by region, by product)
  2. Analyzes historical patterns (trend, volatility, autocorrelation, best/worst month)
  3. Fits six forecasting models and compares them with a rolling-origin backtest
  4. Forecasts the next 12 months with prediction intervals taken from backtest errors
  5. Saves everything to forecast_results.json (embedded in dashboard.html)

Run:  python sales_forecasting.py [path/to/data_analytics_sales_dataset.xlsx]
"""
import json
import sys
import numpy as np
import pandas as pd
from scipy import stats

DATA = sys.argv[1] if len(sys.argv) > 1 else "data_analytics_sales_dataset.xlsx"
HORIZON = 12          # months to forecast
MIN_TRAIN = 8         # smallest training window used in the backtest
BACKTEST_H = 3        # longest horizon scored in the backtest

# --------------------------------------------------------------------------- data
df = pd.read_excel(DATA)
df["Date"] = pd.to_datetime(df["Date"])
last_date = df["Date"].max()
partial_month = last_date.to_period("M")                 # month that is not complete
days_in_month = partial_month.days_in_month
partial_days = last_date.day
print(f"Rows: {len(df):,} | {df.Date.min().date()} to {last_date.date()} | "
      f"{partial_month} covers only {partial_days}/{days_in_month} days")

months_all = pd.period_range(df.Date.min(), last_date, freq="M")
months_full = [m for m in months_all if m != partial_month]        # complete months only
labels = [m.strftime("%b-%y") for m in months_full]
fc_months = pd.period_range(months_full[-1] + 1, periods=HORIZON, freq="M")
fc_labels = [m.strftime("%b-%y") for m in fc_months]

SERIES = {"All": df}
for r in sorted(df.Region.unique()):
    SERIES[r] = df[df.Region == r]
for p in sorted(df.Product.unique()):
    SERIES[p] = df[df.Product == p]


def monthly(sub, col="Sales", how="sum"):
    s = sub.assign(m=sub.Date.dt.to_period("M")).groupby("m")[col].agg(how)
    return s.reindex(months_all, fill_value=0)


# --------------------------------------------------------------------------- models
def f_naive(y, h):
    return np.repeat(y[-1], h)


def f_ma3(y, h):
    return np.repeat(np.mean(y[-3:]), h)


def f_mean(y, h):
    return np.repeat(np.mean(y), h)


def f_ses(y, h):
    best = (np.inf, 0.3, y[0])
    for a in np.arange(0.05, 0.96, 0.05):
        l, sse = y[0], 0.0
        for v in y[1:]:
            sse += (v - l) ** 2
            l = a * v + (1 - a) * l
        if sse < best[0]:
            best = (sse, a, l)
    return np.repeat(best[2], h)


def f_linear(y, h):
    x = np.arange(len(y))
    b, a = np.polyfit(x, y, 1)
    return a + b * np.arange(len(y), len(y) + h)


def f_holt(y, h, phi=0.9):
    best = None
    for a in np.arange(0.1, 0.91, 0.1):
        for be in np.arange(0.05, 0.51, 0.05):
            l, b, sse = y[0], y[1] - y[0], 0.0
            for v in y[1:]:
                pred = l + phi * b
                sse += (v - pred) ** 2
                l_new = a * v + (1 - a) * pred
                b = be * (l_new - l) + (1 - be) * phi * b
                l = l_new
            if best is None or sse < best[0]:
                best = (sse, l, b)
    _, l, b = best
    return np.array([l + sum(phi ** i for i in range(1, k + 1)) * b for k in range(1, h + 1)])


MODELS = {
    "Naive (last month)": f_naive,
    "3-month moving average": f_ma3,
    "Average level (all history)": f_mean,
    "Exponential smoothing": f_ses,
    "Linear trend": f_linear,
    "Damped trend (Holt)": f_holt,
}


def backtest(y):
    """Rolling-origin evaluation: train on y[:t], forecast up to BACKTEST_H months ahead."""
    out = {}
    for name, fn in MODELS.items():
        errs, one_step = [], {}
        for t in range(MIN_TRAIN, len(y)):
            h = min(BACKTEST_H, len(y) - t)
            fc = fn(y[:t], h)
            for k in range(h):
                errs.append((y[t + k] - fc[k], y[t + k]))
            one_step[t] = float(fc[0])
        e = np.array([a for a, _ in errs])
        act = np.array([b for _, b in errs])
        out[name] = {"mae": float(np.mean(np.abs(e))), "rmse": float(np.sqrt(np.mean(e ** 2))),
                     "mape": float(np.mean(np.abs(e) / act) * 100), "bias": float(np.mean(e)),
                     "n": len(e), "one_step": one_step}
    return out


# --------------------------------------------------------------------------- run
res = {"months": labels, "fc_months": fc_labels, "series": {}, "models": list(MODELS),
       "partial": {"label": partial_month.strftime("%b-%y"), "days": int(partial_days),
                   "days_in_month": int(days_in_month)}}
overall_bt = None
for name, sub in SERIES.items():
    full = monthly(sub)
    y = full.loc[months_full].values.astype(float)
    part = float(full.loc[partial_month])
    bt = backtest(y)
    if name == "All":
        overall_bt = bt
    x = np.arange(len(y))
    lr = stats.linregress(x, y)
    ac1 = float(np.corrcoef(y[:-1], y[1:])[0, 1])
    pattern = {
        "mean": float(y.mean()), "cv": float(y.std(ddof=1) / y.mean() * 100),
        "slope": float(lr.slope), "slope_p": float(lr.pvalue), "autocorr1": ac1,
        "best": [labels[int(y.argmax())], float(y.max())], "worst": [labels[int(y.argmin())], float(y.min())],
        "h1_2024_avg": float(y[:12].mean()), "ytd_2025_avg": float(y[12:].mean()),
    }
    models = {}
    for mname, fn in MODELS.items():
        f = fn(y, HORIZON)
        sigma = bt[mname]["rmse"]
        # interval half-width grows once we go past the 3 months the backtest actually scored
        sig_h = [sigma * np.sqrt(max(1.0, (k + 1) / BACKTEST_H)) for k in range(HORIZON)]
        models[mname] = {"f": [round(float(v)) for v in f], "sigma": [round(float(s)) for s in sig_h],
                         "mae": round(bt[mname]["mae"]), "rmse": round(bt[mname]["rmse"]),
                         "mape": round(bt[mname]["mape"], 2), "bias": round(bt[mname]["bias"]),
                         "one_step": {str(k): round(v) for k, v in bt[mname]["one_step"].items()}}
    best_model = min(MODELS, key=lambda m: bt[m]["rmse"])
    res["series"][name] = {
        "y": [round(float(v)) for v in y], "partial": round(part),
        "orders": [int(v) for v in monthly(sub, "Order_ID", "count").loc[months_full].values],
        "aov": [round(float(a / b)) for a, b in zip(y, monthly(sub, "Order_ID", "count").loc[months_full].values)],
        "pattern": pattern, "models": models, "best": best_model,
    }

res["backtest_start"] = MIN_TRAIN
with open("forecast_results.json", "w") as fh:
    json.dump(res, fh, separators=(",", ":"))

# --------------------------------------------------------------------------- report
A = res["series"]["All"]
print("\nHISTORICAL PATTERN (all sales, complete months only)")
p = A["pattern"]
print(f"  Avg month ₹{p['mean']/1e7:.2f} Cr | volatility (CV) {p['cv']:.1f}% | trend ₹{p['slope']/1e5:+.2f}L/month (p={p['slope_p']:.2f})")
print(f"  Best {p['best'][0]} ₹{p['best'][1]/1e7:.2f} Cr | worst {p['worst'][0]} ₹{p['worst'][1]/1e7:.2f} Cr | lag-1 autocorrelation {p['autocorr1']:+.2f}")
print("\nBACKTEST (all sales, rolling origin, 1-3 months ahead)")
print(f"  {'Model':<30}{'MAE ₹Cr':>9}{'RMSE ₹Cr':>10}{'MAPE %':>8}")
for m in MODELS:
    d = A["models"][m]
    star = "  <- best" if m == A["best"] else ""
    print(f"  {m:<30}{d['mae']/1e7:>9.2f}{d['rmse']/1e7:>10.2f}{d['mape']:>8.1f}{star}")
b = A["models"][A["best"]]
print(f"\nFORECAST with '{A['best']}' (next 12 months, ₹ Cr)")
for lab, f, s in zip(fc_labels, b["f"], b["sigma"]):
    print(f"  {lab}: {f/1e7:6.2f}   80% range {max(0, f-1.28*s)/1e7:5.2f} to {(f+1.28*s)/1e7:5.2f}")
runrate = A["partial"] / partial_days * days_in_month
print(f"\nSanity check: {partial_month} so far = ₹{A['partial']/1e7:.2f} Cr in {partial_days} days "
      f"-> full-month run rate ₹{runrate/1e7:.2f} Cr vs forecast ₹{b['f'][0]/1e7:.2f} Cr")
print("\nSaved forecast_results.json")
