import csv
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

source = Path("data/raw/usda_corn_all_states_original.csv")
out = Path("figures")
out.mkdir(exist_ok=True)

data = defaultdict(dict)

with source.open(newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        if row["Period"] != "YEAR" or row["State"] == "OTHER STATES":
            continue
        try:
            data[row["State"]][int(row["Year"])] = float(
                row["Value"].replace(",", "")
            )
        except (ValueError, TypeError):
            continue

# Chart 1: Top 10 states in 2025
top = sorted(
    [(s, v[2025]) for s, v in data.items() if 2025 in v],
    key=lambda x: x[1], reverse=True
)[:10]

fig, ax = plt.subplots(figsize=(10, 6))
ax.barh([s for s, _ in reversed(top)],
        [v for _, v in reversed(top)])
ax.set_xlabel("Corn yield (bushels per acre)")
ax.set_title("Top 10 U.S. States by Corn Yield — 2025")
fig.tight_layout()
fig.savefig(out / "top_10_corn_yield_2025.png", dpi=200)
plt.close(fig)

# Chart 2: Annual average across available named states
years = range(2020, 2026)
averages = []
for year in years:
    values = [v[year] for v in data.values() if year in v]
    averages.append(sum(values) / len(values))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(list(years), averages, marker="o")
ax.set_xlabel("Year")
ax.set_ylabel("Mean state yield (BU/acre)")
ax.set_title("Unweighted Mean Corn Yield Across Reporting States")
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(out / "corn_yield_trend_2020_2025.png", dpi=200)
plt.close(fig)

# Chart 3: Largest year-over-year yield declines
changes = []
for state, values in data.items():
    for year in range(2021, 2026):
        if year in values and year - 1 in values:
            previous = values[year - 1]
            if previous > 0:
                pct = 100 * (values[year] - previous) / previous
                changes.append((f"{state} ({year})", pct))

worst = sorted(changes, key=lambda x: x[1])[:10]

fig, ax = plt.subplots(figsize=(11, 6))
ax.barh(
    [name for name, _ in reversed(worst)],
    [change for _, change in reversed(worst)]
)
ax.set_xlabel("Year-over-year change (%)")
ax.set_title("10 Largest Annual Corn Yield Declines, 2021–2025")
fig.tight_layout()
fig.savefig(out / "largest_corn_yield_declines.png", dpi=200)
plt.close(fig)

print("Created:")
for filename in sorted(out.glob("*.png")):
    print(" ", filename)

print("\nAnnual unweighted mean yields:")
for year, value in zip(years, averages):
    print(f"  {year}: {value:.2f} BU/acre")
