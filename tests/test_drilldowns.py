from datetime import date

import pytest

from src.drilldowns import bar_target, revenue_target


def test_product_target_preserves_country_and_dates():
    target = bar_target("product", {"y": "00123"}, ["00123", "B"], "2011-11-01", "2011-11-30", ["France"], ["00123", "B"])
    assert target.products == ("00123",)
    assert target.countries == ("France",)
    assert (target.start, target.end) == (date(2011, 11, 1), date(2011, 11, 30))


def test_country_target_preserves_product_selection():
    target = bar_target("country", {"y": "France"}, ["France"], "2011-11-01", "2011-11-30", [], ["A", "B"])
    assert target.countries == ("France",)
    assert target.products == ("A", "B")


@pytest.mark.parametrize("point", [{"y": "stale"}, {}, None, ["France"]])
def test_unknown_or_malformed_bar_values_are_rejected(point):
    assert bar_target("country", point, ["France"], "2011-11-01", "2011-11-30") is None


def test_weekly_drilldown_clips_a_partial_edge_bucket():
    target = revenue_target({"curve_number": 1, "x": "2011-10-31"}, 1, ["2011-10-31"], "2011-11-02", "2011-11-30", "Weekly")
    assert (target.start, target.end) == (date(2011, 11, 2), date(2011, 11, 6))


def test_monthly_drilldown_clips_both_edges_and_handles_leap_day():
    target = revenue_target({"curve_number": 0, "x": "2024-02-01"}, 0, ["2024-02-01"], "2024-02-03", "2024-02-29", "Monthly")
    assert (target.start, target.end) == (date(2024, 2, 3), date(2024, 2, 29))


@pytest.mark.parametrize("point", [
    {"curve_number": 0, "x": "2011-11-01"},
    {"curve_number": 1, "x": "2000-01-01"},
    {"curve_number": 1, "x": "invalid"},
    {"curve_number": 1},
    None,
])
def test_previous_series_and_stale_or_malformed_dates_are_not_reinterpreted(point):
    assert revenue_target(point, 1, ["2011-11-01"], "2011-11-01", "2011-11-30", "Daily") is None


def test_callback_navigation_restores_origin_and_keeps_calculation_policy():
    from unittest.mock import patch
    from src.drilldown_views import open_records, return_to_chart

    original = {
        "navigation": "Overview", "date_range": (date(2011, 11, 1), date(2011, 11, 30)),
        "countries": ["France", "Germany"], "products": [], "source_id": ("local", 123),
        "revenue_aggregation": "Monthly", "product_ranking": "Units", "exclude_duplicates": True,
    }
    state = dict(original)
    target = bar_target("country", {"y": "France"}, ["France"], *original["date_range"], original["countries"])
    with patch("src.drilldown_views.st.session_state", state):
        open_records(target)
        assert state["navigation"] == "Data Explorer"
        assert state["countries"] == ["France"]
        assert state["transaction_types"] == ["Sale"]
        assert state["exclude_duplicates"] is True
        assert state["transaction_search"] == ""
        return_to_chart()
        for key, value in original.items():
            assert state[key] == value
        assert "drilldown_origin" not in state


def test_a_changed_workbook_cannot_restore_stale_filter_values():
    from unittest.mock import patch
    from src.drilldown_views import open_records, return_to_chart

    state = {"navigation": "Overview", "date_range": (date(2011, 11, 1), date(2011, 11, 30)), "source_id": "first"}
    target = bar_target("country", {"y": "France"}, ["France"], *state["date_range"])
    with patch("src.drilldown_views.st.session_state", state):
        open_records(target)
        state["source_id"] = "new-workbook"
        return_to_chart()
        assert state["navigation"] == "Data Explorer"
        assert "drilldown_origin" not in state
