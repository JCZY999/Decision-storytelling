from pathlib import Path

from visualization_techniques import generate_all, make_marketing_data


def test_marketing_data_is_reproducible() -> None:
    campaign_a, monthly_a = make_marketing_data()
    campaign_b, monthly_b = make_marketing_data()
    assert campaign_a.equals(campaign_b)
    assert monthly_a.equals(monthly_b)


def test_all_visualizations_are_generated() -> None:
    outputs = generate_all()
    assert len(outputs) == 8
    assert all(isinstance(path, Path) and path.exists() and path.stat().st_size > 10_000 for path in outputs)
