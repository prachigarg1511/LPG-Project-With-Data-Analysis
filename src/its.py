import numpy as np
import pandas as pd
import statsmodels.api as sm

def fit_its(df: pd.DataFrame, date_col="date", y_col="price", event_date="2022-02-24"):
    d = df[[date_col, y_col]].dropna().copy()
    d[date_col] = pd.to_datetime(d[date_col])
    d = d.sort_values(date_col)

    d["time"] = np.arange(len(d), dtype=float)
    event_dt = pd.to_datetime(event_date)

    d["post"] = (d[date_col] >= event_dt).astype(int)
    event_idx = d.loc[d[date_col] >= event_dt, "time"].min()
    if np.isnan(event_idx):
        raise ValueError("Event date is after last observation.")

    d["time_post"] = np.clip(d["time"] - event_idx, 0, None)

    X = sm.add_constant(d[["time", "post", "time_post"]])
    y = d[y_col].astype(float)

    model = sm.OLS(y, X).fit(cov_type="HC3")
    d["yhat"] = model.predict(X)
    return d, model