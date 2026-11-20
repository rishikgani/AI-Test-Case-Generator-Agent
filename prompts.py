"""
Prompt templates for AI Test Case Generator Agent.
Contains system prompts and user prompt templates for LLM interaction.
"""

# Concise system prompt for faster generation
SYSTEM_PROMPT = """You are a QA expert. First understand the feature and its stated constraints.
Generate concise, non-duplicate test cases from the actual requirement.
Do not invent application rules. Put any unstated assumption in "assumptions".
Use only scenario_type values Positive, Negative, Edge and only priority values High, Medium, Low.
Output ONLY valid JSON, no markdown, no extra text.

Format:
{"test_cases":[{"test_case_id":"TC-01","scenario_type":"Positive","title":"Valid registration","preconditions":"None","steps":"1. Enter valid name, email, password","test_data":"name=John, email=j@j.com, pass=pass1234","expected_result":"Account created","priority":"High"},{"test_case_id":"TC-02","scenario_type":"Negative","title":"Empty email","preconditions":"None","steps":"1. Leave email blank","test_data":"email=","expected_result":"Error message shown","priority":"High"}],"assumptions":["Password min 8 chars"]}"""


# User prompt template
USER_PROMPT_TEMPLATE = """Requirement: {requirement}

Generate 4-6 test cases (positive, negative, edge). Output ONLY the JSON object."""


def build_user_prompt(requirement: str) -> str:
    """Build the user prompt with the given requirement."""
    return USER_PROMPT_TEMPLATE.format(requirement=requirement)