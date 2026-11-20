"""
Test Case Generator module.
Handles LLM interaction, response validation, and test case processing.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from langchain_ollama import OllamaLLM as Ollama

from prompts import SYSTEM_PROMPT, build_user_prompt


class TestCaseGenerator:
    """Generates test cases using a local LLM via Ollama."""

    def __init__(self, model_name: str = "llama3.2", temperature: float = 0.3):
        """
        Initialize the test case generator.

        Args:
            model_name: Name of the Ollama model to use
            temperature: Temperature for generation (lower = more deterministic)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self._initialize_llm()

    def _initialize_llm(self):
        """Initialize the Ollama LLM."""
        try:
            self.llm = Ollama(
                model=self.model_name,
                temperature=self.temperature,
                num_predict=1024,  # Limit output tokens for faster response
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Ollama with model '{self.model_name}': {e}")

    def generate_test_cases(self, requirement: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Generate test cases from a requirement.

        Args:
            requirement: Software requirement description

        Returns:
            Tuple of (test_cases_list, assumptions_list)

        Raises:
            ValueError: If requirement is empty or invalid
            RuntimeError: If LLM generation or parsing fails
        """
        if not requirement or not requirement.strip():
            raise ValueError("Requirement cannot be empty")

        # Build prompt
        user_prompt = build_user_prompt(requirement.strip())

        # Generate response
        try:
            full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
            response = self.llm.invoke(full_prompt)
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

        # Parse and validate response
        test_cases, assumptions = self._parse_and_validate_response(response)

        if not test_cases:
            raise RuntimeError("No valid test cases generated. Please try again or rephrase the requirement.")

        return test_cases, assumptions

    def _parse_and_validate_response(self, response: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse and validate the LLM response.

        Args:
            response: Raw LLM response

        Returns:
            Tuple of (validated_test_cases, assumptions)
        """
        # Try to extract JSON from response
        json_str = self._extract_json(response)

        if not json_str:
            raise RuntimeError("Could not extract valid JSON from LLM response")

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in LLM response: {e}")

        # Validate structure
        if not isinstance(data, dict):
            raise RuntimeError("Response must be a JSON object")

        test_cases = data.get("test_cases", [])
        assumptions = data.get("assumptions", [])

        if not isinstance(test_cases, list):
            raise RuntimeError("'test_cases' must be a list")

        if not isinstance(assumptions, list):
            assumptions = []

        # Validate each test case
        validated_cases = []
        seen_ids = set()

        for i, tc in enumerate(test_cases):
            validated = self._validate_test_case(tc, i + 1)
            if validated:
                # Check for duplicate IDs
                tc_id = validated["test_case_id"]
                if tc_id in seen_ids:
                    # Generate new unique ID
                    validated["test_case_id"] = self._generate_unique_id(seen_ids)
                seen_ids.add(validated["test_case_id"])
                validated_cases.append(validated)

        return validated_cases, assumptions

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract JSON from text, handling markdown code blocks."""
        # Try to find JSON in markdown code blocks
        json_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_block_pattern, text, re.DOTALL)
        if matches:
            return matches[0].strip()

        # Try to find JSON object directly
        json_pattern = r'(\{.*\})'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            # Return the largest match (most likely to be complete)
            return max(matches, key=len).strip()

        return None

    def _validate_test_case(self, tc: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """Validate a single test case and return normalized version."""
        if not isinstance(tc, dict):
            raise RuntimeError(f"Test case {index} must be a JSON object")

        # Required fields
        required_fields = [
            "test_case_id", "scenario_type", "title",
            "preconditions", "steps", "test_data",
            "expected_result", "priority"
        ]

        for field in required_fields:
            if field not in tc or tc[field] is None or str(tc[field]).strip() == "":
                raise RuntimeError(
                    f"Invalid LLM response: test case {index} is missing required field '{field}'"
                )

        # Validate scenario_type
        valid_scenarios = ["Positive", "Negative", "Edge"]
        scenario = str(tc["scenario_type"]).strip().title()
        if scenario not in valid_scenarios:
            raise RuntimeError(
                f"Invalid LLM response: test case {index} has unsupported scenario type '{tc['scenario_type']}'"
            )
        tc["scenario_type"] = scenario

        # Validate priority
        valid_priorities = ["High", "Medium", "Low"]
        priority = str(tc["priority"]).strip().title()
        if priority not in valid_priorities:
            raise RuntimeError(
                f"Invalid LLM response: test case {index} has unsupported priority '{tc['priority']}'"
            )
        tc["priority"] = priority

        # Ensure test_case_id format
        if not re.match(r'^TC-\d+$', tc["test_case_id"]):
            tc["test_case_id"] = f"TC-{index:02d}"

        # Ensure all fields are strings
        for key in tc:
            if tc[key] is None:
                tc[key] = ""
            elif not isinstance(tc[key], str):
                tc[key] = str(tc[key])

        return tc

    def _generate_unique_id(self, seen_ids: set) -> str:
        """Generate a unique test case ID."""
        counter = 1
        while True:
            new_id = f"TC-{counter:02d}"
            if new_id not in seen_ids:
                return new_id
            counter += 1

    def check_model_availability(self) -> bool:
        """Check if the Ollama model is available."""
        try:
            # Try a simple invocation
            self.llm.invoke("Hello")
            return True
        except Exception:
            return False


def create_generator(model_name: str = "llama3.2") -> TestCaseGenerator:
    """Factory function to create a TestCaseGenerator instance."""
    return TestCaseGenerator(model_name=model_name)