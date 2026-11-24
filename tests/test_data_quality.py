import numpy as np
import pandas as pd
import pytest

from src.data_processing import clean_transactions
from src.data_quality import (
    filter_quality_evidence, quality_counts, quality_evidence, quality_impact, validate_metrics,
)


def test_findings_overlap_without_double_counting_affected_rows(raw_transactions, transactions):
    evidence = quality_evidence(raw_transactions, transactions)
    assert len(evidence) == 4
    counts = quality_counts(evidence, len(transactions)).set_index("Code")
    assert counts.loc["missing_customer", "Rows"] == 1
    assert counts.loc["missing_description", "Rows"] == 1
    assert counts.loc["exact_repeat", "Rows"] == 1
    assert counts.loc["missing_customer", "Percent"] == pytest.approx(100 / 7)
    assert counts.Rows.sum() > len(evidence)


def test_evidence_retains_original_cells_and_workbook_rows(raw_transactions, transactions):
    before = raw_transactions.copy(deep=True)
    evidence = quality_evidence(raw_transactions, transactions)
    row = evidence.loc[evidence.SourceRow.eq(5)].iloc[0]
    assert pd.isna(row.Description)
    assert pd.isna(row.CustomerID)
    assert row.Quantity == 3
    assert row.missing_customer and row.missing_description
    pd.testing.assert_frame_equal(raw_transactions, before)


def test_undated_and_nonfinite_source_evidence_is_not_lost(raw_transactions):
    raw_transactions = raw_transactions.astype(object)
    raw_transactions.loc[0, "InvoiceDate"] = "not-a-date"
    raw_transactions.loc[1, "Quantity"] = np.inf
    prepared = clean_transactions(raw_transactions)
    evidence = quality_evidence(raw_transactions, prepared).set_index("SourceRow")
    assert evidence.loc[2, "invalid_date"]
    assert evidence.loc[2, "InvoiceDate"] == "not-a-date"
    assert evidence.loc[3, "invalid_quantity"]


def test_impact_is_observed_value_not_automatic_revenue_loss(raw_transactions, transactions):
    impact = quality_impact(transactions, quality_evidence(raw_transactions, transactions))
    assert impact["source_rows"] == 7
    assert impact["affected_rows"] == 4
    assert impact["excluded_rows"] == 1
    assert impact["unattributed_sales_value"] == 12
    assert impact["repeated_sales_value"] == 20


def test_all_consistency_checks_pass_for_the_existing_pipeline(transactions):
    assert validate_metrics(transactions).Result.eq("PASS").all()


def test_validation_detects_admission_rule_violation(transactions):
    transactions.loc[0, "IsCancellation"] = True
    checks = validate_metrics(transactions).set_index("Validation")
    assert checks.loc["Positive-sales admission rules", "Result"] == "FAIL"


def test_selected_evidence_denominator_and_literal_search(raw_transactions, transactions):
    evidence = quality_evidence(raw_transactions, transactions)
    selected = evidence.loc[evidence.SourceRow.eq(5)]
    counts = quality_counts(selected, 1).set_index("Code")
    assert counts.loc["missing_customer", "Percent"] == 100
    assert counts.loc["missing_description", "Percent"] == 100
    assert len(filter_quality_evidence(evidence, "exact_repeat", "cup")) == 1
    assert filter_quality_evidence(evidence, query="[").empty
    with pytest.raises(ValueError, match="Unknown quality"):
        filter_quality_evidence(evidence, "invented")


def test_empty_source_has_zero_counts_without_division_errors(raw_transactions):
    raw = raw_transactions.iloc[:0]
    prepared = clean_transactions(raw)
    evidence = quality_evidence(raw, prepared)
    assert evidence.empty
    assert quality_counts(evidence, 0).Rows.sum() == 0
    assert quality_counts(evidence, 0).Percent.sum() == 0


def test_missing_country_and_cancel_conflict_keep_distinct_findings(raw_transactions):
    raw = raw_transactions.iloc[[0]].copy()
    raw.loc[raw.index[0], "Country"] = " "
    raw.loc[raw.index[0], "InvoiceNo"] = "C100"
    prepared = clean_transactions(raw)
    row = quality_evidence(raw, prepared).iloc[0]
    assert row.missing_country
    assert row.cancellation_conflict
    assert not row.unmarked_negative
    assert row.TransactionType == "Excluded / review"


def test_bad_row_alignment_is_rejected(raw_transactions, transactions):
    with pytest.raises(ValueError, match="same order and length"):
        quality_evidence(raw_transactions, transactions.iloc[::-1])
