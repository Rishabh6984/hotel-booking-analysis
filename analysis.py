"""Hotel Booking Analysis — exploratory data analysis (EDA).

Questions answered:
 1. Which hotel type gets more bookings, and how many are cancelled?
 2. How does Average Daily Rate (ADR) move across the year?
 3. Does a longer lead time mean more cancellations?
 4. Which market segments and agents bring the most bookings?
Charts are saved to charts/, a summary is printed to the console.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DATA = Path("data/hotel_bookings.csv")
OUT = Path("charts"); OUT.mkdir(exist_ok=True)
MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
sns.set_theme(style="whitegrid", palette=["#0891b2", "#8b5cf6", "#ec4899", "#10b981"])


def load() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    # --- cleaning ---
    df["children"] = df["children"].fillna(0)
    df = df[(df["adults"] + df["children"]) > 0]          # drop zero-guest bookings
    df = df[df["adr"].between(0, 5000)]                    # drop ADR outliers / negatives
    # --- feature engineering ---
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["revenue"] = df["adr"] * df["total_nights"]
    df["arrival_date_month"] = pd.Categorical(df["arrival_date_month"], MONTHS, ordered=True)
    df["lead_bucket"] = pd.cut(df["lead_time"], [-1, 7, 30, 90, 180, 365, 10_000],
                               labels=["0-7d", "8-30d", "31-90d", "91-180d", "181-365d", "365d+"])
    return df


def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=120); plt.close(fig)


def main():
    df = load()
    kept = df[df["is_canceled"] == 0]

    # 1. bookings & cancellation rate by hotel
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.countplot(data=df, x="hotel", hue="is_canceled", ax=ax)
    ax.set_title("Bookings by hotel (1 = cancelled)"); ax.set_xlabel("")
    save(fig, "01_bookings_by_hotel.png")

    # 2. ADR by month
    fig, ax = plt.subplots(figsize=(9, 4))
    sns.lineplot(data=kept, x="arrival_date_month", y="adr", hue="hotel", marker="o", errorbar=None, ax=ax)
    ax.set_title("Average Daily Rate by arrival month"); ax.set_xlabel(""); ax.tick_params(axis="x", rotation=45)
    save(fig, "02_adr_by_month.png")

    # 3. cancellation rate by lead time
    rate = df.groupby("lead_bucket", observed=True)["is_canceled"].mean().mul(100)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=rate.index.astype(str), y=rate.values, color="#0891b2", ax=ax)
    ax.set_title("Cancellation rate by lead time (%)"); ax.set_xlabel("Lead time"); ax.set_ylabel("%")
    save(fig, "03_cancellation_by_lead_time.png")

    # 4. top agents by bookings
    top = kept["agent"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=top.values, y=top.index.astype(str), color="#8b5cf6", ax=ax)
    ax.set_title("Top 10 agents by confirmed bookings"); ax.set_xlabel("Bookings"); ax.set_ylabel("Agent ID")
    save(fig, "04_top_agents.png")

    # 5. market segment share
    seg = kept["market_segment"].value_counts(normalize=True).mul(100)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.barplot(x=seg.values, y=seg.index, color="#ec4899", ax=ax)
    ax.set_title("Market segment share of confirmed bookings (%)"); ax.set_xlabel("%"); ax.set_ylabel("")
    save(fig, "05_market_segments.png")

    # console summary
    summary = df.groupby("hotel").agg(bookings=("hotel", "size"),
                                      cancel_rate=("is_canceled", "mean"),
                                      avg_adr=("adr", "mean"),
                                      avg_nights=("total_nights", "mean"))
    summary["cancel_rate"] = (summary["cancel_rate"] * 100).round(1)
    print("\n=== Summary by hotel ===\n", summary.round(2).to_string())
    print(f"\nPeak ADR month (resort): {kept[kept.hotel=='Resort Hotel'].groupby('arrival_date_month', observed=True)['adr'].mean().idxmax()}")
    print(f"Charts saved to {OUT.resolve()}")


if __name__ == "__main__":
    main()
