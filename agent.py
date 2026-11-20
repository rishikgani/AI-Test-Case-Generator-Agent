"""
Agent module for AI Test Case Generator Agent.
Orchestrates the test case generation workflow.
"""

from typing import List, Dict, Any, Optional, Tuple
from test_case_generator import TestCaseGenerator, create_generator
from database import (
    save_requirement, save_test_cases, get_all_requirements,
    get_requirement_with_test_cases, update_test_case, delete_test_case,
    delete_requirement, delete_test_cases_for_requirement, update_requirement
)
from export_utils import export_to_csv


class TestCaseAgent:
    """Main agent orchestrating the test case generation workflow."""

    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize the agent.

        Args:
            model_name: Ollama model to use for generation
        """
        self.generator = create_generator(model_name)
        self.current_requirement_id: Optional[int] = None
        self.current_test_cases: List[Dict[str, Any]] = []
        self.current_assumptions: List[str] = []

    def generate_test_cases(self, requirement: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Generate test cases for a requirement.

        Args:
            requirement: Software requirement description

        Returns:
            Tuple of (test_cases, assumptions)
        """
        test_cases, assumptions = self.generator.generate_test_cases(requirement)

        # Store in memory for current session
        self.current_test_cases = test_cases
        self.current_assumptions = assumptions

        return test_cases, assumptions

    def save_current_session(self, requirement: str) -> int:
        """
        Save the current requirement and test cases to database.

        Args            requirement: Original requirement text

        Returns:
            Requirement ID
        """
        if not self.current_test_cases:
            raise ValueError("No test cases to save")

        # Save requirement, updating the loaded history item when applicable.
        if self.current_requirement_id is not None:
            req_id = self.current_requirement_id
            update_requirement(req_id, requirement)
            delete_test_cases_for_requirement(req_id)
        else:
            req_id = save_requirement(requirement)
        self.current_requirement_id = req_id

        # Save test cases
        save_test_cases(req_id, self.current_test_cases)

        return req_id

    def load_requirement(self, requirement_id: int) -> Optional[Dict[str, Any]]:
        """
        Load a requirement and its test cases from database.

        Args:
            requirement_id: ID of the requirement to load

        Returns:
            Requirement data with test cases, or None if not found
        """
        data = get_requirement_with_test_cases(requirement_id)
        if data:
            self.current_requirement_id = requirement_id
            self.current_test_cases = data.get('test_cases', [])
        return data

    def get_history(self) -> List[Dict[str, Any]]:
        """Get all saved requirements with test case counts."""
        return get_all_requirements()

    def update_test_case(self, test_case_db_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update a test case in database and memory.

        Args:
            test_case_db_id: Database ID of the test case
            updates: Dictionary of fields to update

        Returns:
            True if successful
        """
        # Update in database
        success = update_test_case(test_case_db_id, updates)

        if success:
            # Update in memory
            for tc in self.current_test_cases:
                if tc.get('id') == test_case_db_id:
                    tc.update(updates)
                    break

        return success

    def delete_test_case(self, test_case_db_id: int) -> bool:
        """
        Delete a test case from database and memory.

        Args:
            test_case_db_id: Database ID of the test case

        Returns:
            True if successful
        """
        success = delete_test_case(test_case_db_id)

        if success:
            self.current_test_cases = [
                tc for tc in self.current_test_cases
                if tc.get('id') != test_case_db_id
            ]

        return success

    def delete_requirement(self, requirement_id: int) -> bool:
        """Delete a requirement and all its test cases."""
        success = delete_requirement(requirement_id)

        if success and self.current_requirement_id == requirement_id:
            self.current_requirement_id = None
            self.current_test_cases = []

        return success

    def export_current_to_csv(self, requirement: str = "") -> bytes:
        """Export current test cases to CSV."""
        return export_to_csv(self.current_test_cases, requirement)

    def get_current_test_cases(self) -> List[Dict[str, Any]]:
        """Get current test cases in memory."""
        return self.current_test_cases

    def set_current_test_cases(self, test_cases: List[Dict[str, Any]]) -> None:
        """Set test cases after UI edits or deletions."""
        self.current_test_cases = test_cases

    def get_current_assumptions(self) -> List[str]:
        """Get current assumptions."""
        return self.current_assumptions

    def clear_current_session(self):
        """Clear current session data."""
        self.current_requirement_id = None
        self.current_test_cases = []
        self.current_assumptions = []

    def check_model_availability(self) -> bool:
        """Check if the LLM model is available."""
        return self.generator.check_model_availability()


def create_agent(model_name: str = "llama3.2") -> TestCaseAgent:
    """Factory function to create a TestCaseAgent instance."""
    return TestCaseAgent(model_name=model_name)