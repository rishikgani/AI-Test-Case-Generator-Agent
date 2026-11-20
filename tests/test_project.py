import os
import tempfile
import unittest

import database
from export_utils import export_to_dataframe, normalize_test_case_records
from test_case_generator import TestCaseGenerator


class TestCaseValidationTests(unittest.TestCase):
    def setUp(self):
        self.generator = TestCaseGenerator.__new__(TestCaseGenerator)

    def test_valid_response_is_normalized(self):
        response = """{"test_cases":[{"test_case_id":"TC-01","scenario_type":"negative","title":"Invalid login","preconditions":"Login page open","steps":"Enter invalid password","test_data":"password=bad","expected_result":"Error is shown","priority":"high"}],"assumptions":["Invalid credentials are rejected"]}"""
        cases, assumptions = self.generator._parse_and_validate_response(response)

        self.assertEqual(cases[0]["scenario_type"], "Negative")
        self.assertEqual(cases[0]["priority"], "High")
        self.assertEqual(assumptions, ["Invalid credentials are rejected"])

    def test_missing_required_field_is_rejected(self):
        response = """{"test_cases":[{"test_case_id":"TC-01","scenario_type":"Positive","title":"Login","preconditions":"Login page open","steps":"Enter credentials","test_data":"valid credentials","expected_result":"","priority":"High"}],"assumptions":[]}"""

        with self.assertRaisesRegex(RuntimeError, "expected_result"):
            self.generator._parse_and_validate_response(response)

    def test_duplicate_id_is_replaced(self):
        response = """{"test_cases":[{"test_case_id":"TC-01","scenario_type":"Positive","title":"One","preconditions":"None","steps":"Run","test_data":"None","expected_result":"Pass","priority":"Low"},{"test_case_id":"TC-01","scenario_type":"Negative","title":"Two","preconditions":"None","steps":"Run","test_data":"Invalid","expected_result":"Fail","priority":"Medium"}],"assumptions":[]}"""
        cases, _ = self.generator._parse_and_validate_response(response)
        self.assertEqual([case["test_case_id"] for case in cases], ["TC-01", "TC-02"])


class ExportTests(unittest.TestCase):
    def test_editor_records_are_normalized_to_internal_keys(self):
        records = [{
            "Test Case ID": "TC-01",
            "Scenario Type": "Positive",
            "Title": "Valid login",
            "Preconditions": "Login page open",
            "Steps": "Enter valid credentials",
            "Test Data": "valid user",
            "Expected Result": "Login succeeds",
            "Priority": "High",
        }]

        normalized = normalize_test_case_records(records)
        self.assertIn("test_case_id", normalized[0])
        self.assertNotIn("Test Case ID", normalized[0])
        self.assertEqual(export_to_dataframe(normalized).iloc[0]["Title"], "Valid login")


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_db_path = database.DB_PATH
        database.DB_PATH = os.path.join(self.temp_directory.name, "test.db")
        database.init_database()

    def tearDown(self):
        database.DB_PATH = self.original_db_path
        self.temp_directory.cleanup()

    def test_save_load_and_delete_history(self):
        requirement_id = database.save_requirement("Login with email and password")
        database.save_test_cases(requirement_id, [{
            "test_case_id": "TC-01",
            "scenario_type": "Positive",
            "title": "Valid login",
            "preconditions": "User exists",
            "steps": "Enter valid credentials",
            "test_data": "valid user",
            "expected_result": "Login succeeds",
            "priority": "High",
        }])

        loaded = database.get_requirement_with_test_cases(requirement_id)
        self.assertEqual(loaded["requirement_text"], "Login with email and password")
        self.assertEqual(len(loaded["test_cases"]), 1)

        database.delete_test_cases_for_requirement(requirement_id)
        loaded = database.get_requirement_with_test_cases(requirement_id)
        self.assertEqual(loaded["test_cases"], [])

        self.assertTrue(database.delete_requirement(requirement_id))
        self.assertIsNone(database.get_requirement_with_test_cases(requirement_id))


if __name__ == "__main__":
    unittest.main()
