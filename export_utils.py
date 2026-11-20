"""
Export utilities for AI Test Case Generator Agent.
Handles CSV export of test cases.
"""

import pandas as pd
import io
import re
from typing import Any, Dict, Hashable, Iterable, List, Mapping
from datetime import datetime


def export_to_csv(test_cases: List[Dict[str, Any]], requirement: str = "") -> bytes:
    """
    Export test cases to CSV format.

    Args:
        test_cases: List of test case dictionaries
        requirement: Original requirement text (optional)

    Returns:
        CSV content as bytes
    """
    if not test_cases:
        # Create empty dataframe with headers
        df = pd.DataFrame(columns=[
            "Test Case ID", "Scenario Type", "Title", "Preconditions",
            "Steps", "Test Data", "Expected Result", "Priority"
        ])
    else:
        # Prepare data for export
        export_data = []
        for tc in test_cases:
            export_data.append({
                "Test Case ID": tc.get("test_case_id", ""),
                "Scenario Type": tc.get("scenario_type", ""),
                "Title": tc.get("title", ""),
                "Preconditions": tc.get("preconditions", ""),
                "Steps": tc.get("steps", ""),
                "Test Data": tc.get("test_data", ""),
                "Expected Result": tc.get("expected_result", ""),
                "Priority": tc.get("priority", "Medium")
            })

        df = pd.DataFrame(export_data)

    # Add requirement as a comment row at the top if provided
    if requirement:
        # Create a buffer with requirement info
        output = io.StringIO()
        output.write(f"# Requirement: {requirement}\n")
        output.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write(f"# Total Test Cases: {len(test_cases)}\n\n")
        df.to_csv(output, index=False)
        return output.getvalue().encode('utf-8')

    # Standard CSV export
    output = io.StringIO()
    df.to_csv(output, index=False)
    return output.getvalue().encode('utf-8')


def export_to_dataframe(test_cases: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert test cases to a pandas DataFrame for display.

    Args:
        test_cases: List of test case dictionaries

    Returns:
        Formatted DataFrame
    """
    if not test_cases:
        return pd.DataFrame(columns=[
            "Test Case ID", "Scenario Type", "Title", "Preconditions",
            "Steps", "Test Data", "Expected Result", "Priority"
        ])

    display_data = []
    for tc in test_cases:
        display_data.append({
            "Test Case ID": tc.get("test_case_id", ""),
            "Scenario Type": tc.get("scenario_type", ""),
            "Title": tc.get("title", ""),
            "Preconditions": tc.get("preconditions", ""),
            "Steps": tc.get("steps", ""),
            "Test Data": tc.get("test_data", ""),
            "Expected Result": tc.get("expected_result", ""),
            "Priority": tc.get("priority", "Medium")
        })

    return pd.DataFrame(display_data)


def normalize_test_case_records(
    records: Iterable[Mapping[Hashable, Any]],
) -> List[Dict[str, Any]]:
    """Convert display/editor records back to internal test-case field names."""
    field_map = {
        "Test Case ID": "test_case_id",
        "Scenario Type": "scenario_type",
        "Title": "title",
        "Preconditions": "preconditions",
        "Steps": "steps",
        "Test Data": "test_data",
        "Expected Result": "expected_result",
        "Priority": "priority",
    }

    normalized = []
    for index, record in enumerate(records, 1):
        source = dict(record)
        tc = {}
        for display_name, internal_name in field_map.items():
            value = source.get(display_name, source.get(internal_name, ""))
            tc[internal_name] = "" if value is None else str(value)

        if not re.match(r"^TC-\d+$", tc["test_case_id"]):
            tc["test_case_id"] = f"TC-{index:02d}"

        tc["scenario_type"] = tc["scenario_type"].title()
        if tc["scenario_type"] not in ("Positive", "Negative", "Edge"):
            tc["scenario_type"] = "Positive"

        tc["priority"] = tc["priority"].title()
        if tc["priority"] not in ("High", "Medium", "Low"):
            tc["priority"] = "Medium"

        normalized.append(tc)

    return normalized


def format_test_case_for_display(test_case: Dict[str, Any]) -> Dict[str, str]:
    """Format a single test case for display in the UI."""
    return {
        "test_case_id": test_case.get("test_case_id", ""),
        "scenario_type": test_case.get("scenario_type", ""),
        "title": test_case.get("title", ""),
        "preconditions": test_case.get("preconditions", ""),
        "steps": test_case.get("steps", ""),
        "test_data": test_case.get("test_data", ""),
        "expected_result": test_case.get("expected_result", ""),
        "priority": test_case.get("priority", "Medium")
    }