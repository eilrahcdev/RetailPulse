"""UI behavior tests use fixtures only; they do not claim real-dataset totals."""

from pathlib import Path
from unittest.mock import patch

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest


@pytest.fixture(autouse=True)
def local_workbook_metadata(tmp_path, monkeypatch):
    """Mocked workbook reads must also work without an on-disk UCI download."""
    dataset_path = Path(__file__).resolve().parents[1] / "data/raw/Online Retail.xlsx"
    placeholder = tmp_path / "workbook-metadata"
    placeholder.touch()
    metadata = placeholder.stat()
    original_exists = Path.exists
    original_stat = Path.stat

    def exists(path):
        return True if path == dataset_path else original_exists(path)

    def stat(path, *args, **kwargs):
        return metadata if path == dataset_path else original_stat(path, *args, **kwargs)

    monkeypatch.setattr(Path, "exists", exists)
    monkeypatch.setattr(Path, "stat", stat)


@pytest.fixture
def app(raw_transactions):
    st.cache_data.clear()
    with patch("src.data_processing.read_workbook", return_value=raw_transactions):
        application = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        application.run(timeout=30)
        yield application
    st.cache_data.clear()


def test_all_five_navigation_destinations_render(app):
    for page in ["Overview", "Sales Analysis", "Product Performance", "Geographic Analysis", "Data Explorer"]:
        app.radio(key="navigation").set_value(page).run(timeout=30)
        assert not app.exception
        assert app.title[0].value == ("Sales Overview" if page == "Overview" else page)


def test_country_product_filters_and_empty_state(app):
    assert not app.exception
    app.multiselect(key="countries").set_value(["France"]).run()
    assert not app.exception
    assert app.metric[0].value == "£12.00"
    assert app.metric[1].value == "1"
    app.multiselect(key="products").set_value(["B"]).run()
    assert not app.exception
    assert any("No transactions match" in message.value for message in app.info)


def test_duplicate_toggle_and_reset_filters(app):
    assert app.metric[0].value == "£57.00"
    app.toggle(key="exclude_duplicates").set_value(True).run()
    assert app.metric[0].value == "£37.00"
    app.multiselect(key="countries").set_value(["France"]).run()
    next(button for button in app.button if button.label == "Reset filters").click().run()
    assert not app.exception
    assert app.multiselect(key="countries").value == []
    assert app.metric[0].value == "£37.00"
    app.toggle(key="exclude_duplicates").set_value(False).run()
    assert app.multiselect(key="countries").value == []
    assert app.multiselect(key="products").value == []
    assert app.metric[0].value == "£57.00"


def test_explorer_search_updates_visible_rows(app):
    app.radio(key="navigation").set_value("Data Explorer").run()
    next(widget for widget in app.text_input if widget.label == "Search transactions").set_value("plate").run()
    assert not app.exception
    table = next(table.value for table in app.dataframe if "InvoiceNo" in table.value.columns)
    assert len(table) == 2
    assert table.StockCode.eq("B").all()


def test_explorer_transaction_type_selection(app):
    from src.data_processing import RETURN

    app.radio(key="navigation").set_value("Data Explorer").run()
    app.multiselect(key="transaction_types").set_value([RETURN]).run()
    assert not app.exception
    table = next(table.value for table in app.dataframe if "InvoiceNo" in table.value.columns)
    assert len(table) == 2
    assert table.TransactionType.eq(RETURN).all()
    app.multiselect(key="transaction_types").set_value([]).run()
    assert any("No transactions match this search" in message.value for message in app.info)


def test_empty_workbook_shows_actionable_state(raw_transactions):
    st.cache_data.clear()
    with patch("src.data_processing.read_workbook", return_value=raw_transactions.iloc[:0]):
        application = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    assert not application.exception
    assert any("no dated transactions" in message.value for message in application.warning)
    st.cache_data.clear()


def test_unreadable_workbook_shows_error():
    st.cache_data.clear()
    with patch("src.data_processing.read_workbook", side_effect=ValueError("Missing required columns: InvoiceNo")):
        application = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    assert not application.exception
    assert any("could not be loaded" in message.value for message in application.error)
    st.cache_data.clear()


def test_missing_local_workbook_shows_download_and_upload_guidance():
    original_exists = Path.exists
    dataset_path = Path(__file__).resolve().parents[1] / "data/raw/Online Retail.xlsx"

    def exists_without_dataset(path):
        return False if path == dataset_path else original_exists(path)

    with patch.object(Path, "exists", exists_without_dataset):
        application = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
    assert not application.exception
    assert any("Add the Online Retail workbook" in message.value for message in application.info)


def test_date_selection_and_uncovered_comparison(app):
    from datetime import date

    app.date_input(key="date_range").set_value((date(2011, 1, 2), date(2011, 1, 2))).run()
    assert not app.exception
    assert app.metric[0].value == "£12.00"
    assert app.metric[1].value == "1"
    app.date_input(key="date_range").set_value((date(2011, 1, 1), date(2011, 1, 1))).run()
    assert not app.exception
    assert all(metric.delta == "" for metric in app.metric)
    assert any("Comparison unavailable" in caption.value for caption in app.caption)


def test_quality_center_preserves_existing_navigation_and_source_scope(app):
    app.radio(key="navigation").set_value("Data Quality Center").run()
    assert not app.exception
    assert app.title[0].value == "Data Quality Center"
    assert app.metric[0].value == "7"
    assert app.metric[1].value == "4"
    assert app.date_input(key="date_range").disabled
    assert app.multiselect(key="countries").disabled
    checks = next(table.value for table in app.dataframe if "Validation" in table.value.columns)
    assert checks.Result.eq("PASS").all()
    app.radio(key="navigation").set_value("Overview").run()
    assert app.metric[0].value == "£57.00"
    assert not app.date_input(key="date_range").disabled


def test_quality_current_scope_respects_dates_and_keeps_audit_evidence(app):
    from datetime import date

    app.radio(key="navigation").set_value("Data Quality Center").run()
    app.radio(key="quality_scope").set_value("Current filters").run()
    app.date_input(key="date_range").set_value((date(2011, 1, 2), date(2011, 1, 2))).run()
    assert not app.exception
    assert app.metric[0].value == "1"
    assert app.metric[1].value == "1"
    app.selectbox(key="quality_check").set_value("missing_customer").run()
    evidence = next(table.value for table in app.dataframe if "QualityIssues" in table.value.columns)
    assert len(evidence) == 1
    assert evidence.SourceRow.iloc[0] == 5


def test_quality_center_can_inspect_an_entirely_undated_workbook(raw_transactions):
    raw_transactions["InvoiceDate"] = "invalid-date"
    st.cache_data.clear()
    with patch("src.data_processing.read_workbook", return_value=raw_transactions):
        application = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)
        application.radio(key="navigation").set_value("Data Quality Center").run()
    assert not application.exception
    assert application.metric[0].value == "7"
    evidence = next(table.value for table in application.dataframe if "QualityIssues" in table.value.columns)
    assert len(evidence) == 7
    assert evidence.InvoiceDate.eq("invalid-date").all()
    st.cache_data.clear()


def test_keyboard_product_drilldown_and_back_restore_global_filters(app):
    app.selectbox(key="record_picker_products_chart").set_value("A").run()
    app.button(key="inspect_picker_products_chart").click().run()
    assert not app.exception
    assert app.title[0].value == "Data Explorer"
    assert app.multiselect(key="products").value == ["A"]
    assert app.multiselect(key="transaction_types").value == ["Sale"]
    rows = next(table.value for table in app.dataframe if "InvoiceNo" in table.value.columns)
    assert len(rows) == 3
    assert rows.StockCode.eq("A").all()
    assert rows.TransactionType.eq("Sale").all()
    app.button(key="drilldown_back").click().run()
    assert not app.exception
    assert app.title[0].value == "Sales Overview"
    assert app.multiselect(key="products").value == []
    assert app.metric[0].value == "£57.00"


def test_returns_composition_is_observed_and_reconciles_in_ui(app):
    app.radio(key="navigation").set_value("Sales Analysis").run()
    assert not app.exception
    composition = next(table.value for table in app.dataframe if "UsableCreditValue" in table.value.columns)
    assert composition.UsableCreditValue.sum() == 20
    assert composition.Lines.sum() == 2


def test_zero_sales_bucket_keeps_a_path_back_to_the_chart(app):
    import pandas as pd

    app.selectbox(key="record_picker_revenue_chart").set_value(pd.Timestamp("2011-01-04")).run()
    app.button(key="inspect_picker_revenue_chart").click().run()
    assert not app.exception
    assert app.title[0].value == "Data Explorer"
    assert any("No transactions match this search" in message.value for message in app.info)
    app.button(key="drilldown_back").click().run()
    assert not app.exception
    assert app.title[0].value == "Sales Overview"
    assert app.metric[0].value == "£57.00"


def test_aggregation_is_initialized_after_quality_page_and_filter_reset(app):
    app.segmented_control(key="revenue_aggregation").set_value("Weekly").run()
    app.radio(key="navigation").set_value("Data Quality Center").run()
    app.radio(key="navigation").set_value("Sales Analysis").run()
    next(button for button in app.button if button.label == "Reset filters").click().run()
    assert not app.exception
    assert app.segmented_control(key="revenue_aggregation").value in {"Daily", "Weekly", "Monthly"}
    assert app.metric[0].value == "£57.00"
