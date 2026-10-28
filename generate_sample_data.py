"""Generate a synthetic sample with the same columns as the public Kaggle
'Hotel booking demand' dataset, so the analysis runs out of the box.
Replace data/hotel_bookings.csv with the full Kaggle file for real results."""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
N = 3000
months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
season = np.array([.06, .06, .08, .09, .09, .10, .12, .13, .08, .07, .06, .06])

hotel = rng.choice(["City Hotel", "Resort Hotel"], N, p=[.62, .38])
month = rng.choice(months, N, p=season / season.sum())
m_idx = np.array([months.index(m) for m in month])
summer = np.isin(m_idx, [5, 6, 7]).astype(float)
base_adr = np.where(hotel == "City Hotel", 105, 90) + summer * np.where(hotel == "Resort Hotel", 70, 15)
adr = np.clip(rng.normal(base_adr, 25), 20, None).round(2)
lead = rng.gamma(1.6, 60, N).astype(int)
cancel_p = np.clip(0.12 + lead / 900 + (hotel == "City Hotel") * 0.12, 0, 0.85)

df = pd.DataFrame({
    "hotel": hotel,
    "is_canceled": (rng.random(N) < cancel_p).astype(int),
    "lead_time": lead,
    "arrival_date_year": rng.choice([2015, 2016, 2017], N, p=[.2, .47, .33]),
    "arrival_date_month": month,
    "stays_in_weekend_nights": rng.poisson(0.9, N),
    "stays_in_week_nights": rng.poisson(2.4, N),
    "adults": rng.choice([1, 2, 3], N, p=[.2, .72, .08]),
    "children": rng.choice([0, 1, 2], N, p=[.9, .07, .03]),
    "meal": rng.choice(["BB", "HB", "SC", "FB"], N, p=[.77, .12, .09, .02]),
    "country": rng.choice(["PRT", "GBR", "FRA", "ESP", "DEU", "ITA", "IRL", "IND"], N,
                          p=[.4, .11, .09, .08, .07, .05, .04, .16]),
    "market_segment": rng.choice(["Online TA", "Offline TA/TO", "Groups", "Direct", "Corporate"], N,
                                 p=[.47, .2, .16, .11, .06]),
    "customer_type": rng.choice(["Transient", "Transient-Party", "Contract", "Group"], N, p=[.75, .21, .03, .01]),
    "agent": rng.choice([9, 240, 1, 14, 7, 6, 250, 241, 28, 8], N),
    "adr": adr,
    "total_of_special_requests": rng.poisson(0.57, N),
})
Path("data").mkdir(exist_ok=True)
df.to_csv("data/hotel_bookings.csv", index=False)
print(f"wrote {len(df)} rows -> data/hotel_bookings.csv")
