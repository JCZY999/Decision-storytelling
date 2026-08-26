"""Reproducible examples of decision-focused data visualization techniques."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUTPUT_DIR = Path(__file__).parent / "outputs"
COLORS = {"blue": "#2563eb", "green": "#16a34a", "orange": "#f59e0b", "red": "#ef4444", "gray": "#94a3b8"}


def make_marketing_data(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create deterministic campaign and monthly funnel data for the examples."""
    rng = np.random.default_rng(seed)
    channels = ["Search", "Social", "Email", "Display", "Affiliate"]
    campaign = pd.DataFrame(
        {
            "channel": channels,
            "spend": [180, 150, 45, 95, 65],
            "revenue": [570, 315, 210, 180, 195],
            "conversion_rate": [0.092, 0.061, 0.118, 0.043, 0.079],
            "cac": [72, 96, 31, 121, 58],
        }
    )
    dates = pd.date_range("2025-01-01", periods=12, freq="MS")
    sessions = np.linspace(42_000, 67_000, 12) + rng.normal(0, 2_200, 12)
    conversion_rate = np.linspace(0.072, 0.089, 12) + rng.normal(0, 0.004, 12)
    monthly = pd.DataFrame(
        {
            "month": dates,
            "sessions": sessions.astype(int),
            "conversion_rate": conversion_rate.clip(0, 1),
        }
    )
    monthly["conversions"] = (monthly["sessions"] * monthly["conversion_rate"]).astype(int)
    monthly["rolling_conversion_rate"] = monthly["conversion_rate"].rolling(3, min_periods=1).mean()
    return campaign, monthly


def apply_style() -> None:
    """Apply an accessible, presentation-ready chart style."""
    plt.rcParams.update(
        {
            "figure.figsize": (10, 6),
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.alpha": 0.2,
            "font.size": 11,
        }
    )


def save(fig: plt.Figure, filename: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return path


def comparison_bar(campaign: pd.DataFrame) -> Path:
    """Rank categories and emphasize the most decision-relevant item."""
    data = campaign.sort_values("conversion_rate")
    colors = [COLORS["blue"] if value == data["conversion_rate"].max() else COLORS["gray"] for value in data["conversion_rate"]]
    fig, ax = plt.subplots()
    bars = ax.barh(data["channel"], data["conversion_rate"] * 100, color=colors)
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.set(title="Email has the highest conversion rate", xlabel="Conversion rate (%)", ylabel="")
    return save(fig, "01_ranked_comparison.png")


def trend_with_baseline(monthly: pd.DataFrame) -> Path:
    """Show a noisy time series together with a rolling baseline."""
    fig, ax = plt.subplots()
    ax.plot(monthly["month"], monthly["conversion_rate"] * 100, marker="o", color=COLORS["blue"], label="Monthly")
    ax.plot(monthly["month"], monthly["rolling_conversion_rate"] * 100, linewidth=3, color=COLORS["green"], label="3-month average")
    ax.set(title="Conversion improved despite monthly volatility", xlabel="", ylabel="Conversion rate (%)")
    ax.legend(frameon=False)
    return save(fig, "02_trend_and_baseline.png")


def relationship_scatter(campaign: pd.DataFrame) -> Path:
    """Compare investment and return while labeling every observation."""
    fig, ax = plt.subplots()
    ax.scatter(campaign["spend"], campaign["revenue"], s=campaign["conversion_rate"] * 1_800, color=COLORS["blue"], alpha=0.75)
    for row in campaign.itertuples():
        ax.annotate(row.channel, (row.spend, row.revenue), xytext=(5, 5), textcoords="offset points")
    ax.set(title="Search scales with the strongest revenue", xlabel="Spend ($K)", ylabel="Revenue ($K)")
    return save(fig, "03_relationship_scatter.png")


def variance_waterfall(campaign: pd.DataFrame) -> Path:
    """Explain how channel-level changes combine into a total variance."""
    labels = ["Search", "Social", "Email", "Display", "Affiliate"]
    changes = np.array([45, -28, 22, -12, 18])
    starts = np.r_[0, np.cumsum(changes)[:-1]]
    fig, ax = plt.subplots()
    ax.bar(labels, changes, bottom=starts, color=[COLORS["green"] if x > 0 else COLORS["red"] for x in changes])
    ax.axhline(0, color="#334155", linewidth=0.8)
    ax.set(title="Search and email offset weaker social and display", ylabel="Revenue variance ($K)")
    return save(fig, "04_variance_waterfall.png")


def funnel_chart() -> Path:
    """Show stage volume and where the largest loss occurs."""
    stages = ["Sessions", "Leads", "Qualified", "Customers"]
    values = np.array([100_000, 18_500, 7_200, 3_150])
    fig, ax = plt.subplots()
    bars = ax.barh(stages[::-1], values[::-1], color=[COLORS["green"], COLORS["blue"], COLORS["orange"], COLORS["gray"]])
    ax.bar_label(bars, labels=[f"{v:,}" for v in values[::-1]], padding=4)
    ax.set(title="Lead qualification is the largest funnel loss", xlabel="Customers", ylabel="")
    return save(fig, "05_funnel.png")


def heatmap() -> Path:
    """Use a heatmap to reveal two-dimensional performance patterns."""
    matrix = np.array([[7.2, 8.1, 9.4, 8.8], [5.1, 6.4, 6.9, 7.3], [9.0, 10.4, 11.2, 10.8], [4.0, 4.9, 5.5, 5.2], [6.8, 7.2, 8.0, 8.4]])
    fig, ax = plt.subplots()
    image = ax.imshow(matrix, cmap="Blues", aspect="auto")
    ax.set_xticks(range(4), ["Q1", "Q2", "Q3", "Q4"])
    ax.set_yticks(range(5), ["Search", "Social", "Email", "Display", "Affiliate"])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, f"{matrix[i, j]:.1f}%", ha="center", va="center", color="white" if matrix[i, j] > 7.5 else "#0f172a")
    fig.colorbar(image, ax=ax, label="Conversion rate (%)")
    ax.set(title="Email leads conversion across every quarter")
    return save(fig, "06_segment_heatmap.png")


def small_multiples(monthly: pd.DataFrame) -> Path:
    """Compare trends on identical axes without overloading one chart."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, channel, offset in zip(axes, ["Search", "Social", "Email"], [0.01, -0.008, 0.025]):
        values = (monthly["conversion_rate"] + offset).clip(0, 1) * 100
        ax.plot(monthly["month"], values, color=COLORS["blue"], linewidth=2)
        ax.set_title(channel)
        ax.tick_params(axis="x", rotation=45)
    axes[0].set_ylabel("Conversion rate (%)")
    fig.suptitle("Small multiples make channel trends comparable", fontsize=15, weight="bold")
    return save(fig, "07_small_multiples.png")


def uncertainty_interval() -> Path:
    """Communicate estimates together with uncertainty rather than false precision."""
    labels = ["Search", "Social", "Email", "Display", "Affiliate"]
    effect = np.array([7.2, 1.8, 9.1, -0.8, 4.5])
    error = np.array([2.1, 2.8, 2.5, 3.1, 2.3])
    fig, ax = plt.subplots()
    ax.errorbar(effect, labels, xerr=error, fmt="o", markersize=8, color=COLORS["blue"], ecolor=COLORS["gray"], capsize=4)
    ax.axvline(0, color=COLORS["red"], linestyle="--", linewidth=1)
    ax.set(title="Only some channel lift estimates exclude zero", xlabel="Estimated incremental lift (percentage points)", ylabel="")
    return save(fig, "08_uncertainty_intervals.png")


def generate_all() -> list[Path]:
    """Generate all visualization examples and return their paths."""
    apply_style()
    campaign, monthly = make_marketing_data()
    return [
        comparison_bar(campaign),
        trend_with_baseline(monthly),
        relationship_scatter(campaign),
        variance_waterfall(campaign),
        funnel_chart(),
        heatmap(),
        small_multiples(monthly),
        uncertainty_interval(),
    ]


if __name__ == "__main__":
    for output in generate_all():
        print(output)
