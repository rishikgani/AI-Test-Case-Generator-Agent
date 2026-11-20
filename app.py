"""
AI Test Case Generator Agent - Streamlit Web Application.
Main entry point for the web UI.
"""

import streamlit as st
from datetime import datetime

from agent import create_agent
from database import init_database
from export_utils import (
    export_to_dataframe,
    normalize_test_case_records,
)


# Page configuration
st.set_page_config(
    page_title="AI Test Case Generator Agent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .priority-high { background-color: #ffebee; color: #c62828; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; }
    .priority-medium { background-color: #fff3e0; color: #ef6c00; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; }
    .priority-low { background-color: #e8f5e9; color: #2e7d32; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: bold; }
    .assumption-box {
        background-color: #f5f5f5;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 4px 4px 0;
    }
    .stButton > button {
        width: 100%;
    }
    .test-case-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #fafafa;
    }
    .scenario-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .scenario-positive { background-color: #e8f5e9; color: #2e7d32; }
    .scenario-negative { background-color: #ffebee; color: #c62828; }
    .scenario-edge { background-color: #e3f2fd; color: #1565c0; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize Streamlit session state variables."""
    if 'agent' not in st.session_state:
        st.session_state.agent = create_agent()
    if 'generated_test_cases' not in st.session_state:
        st.session_state.generated_test_cases = []
    if 'current_assumptions' not in st.session_state:
        st.session_state.current_assumptions = []
    if 'current_requirement' not in st.session_state:
        st.session_state.current_requirement = ""
    if 'show_history' not in st.session_state:
        st.session_state.show_history = False
    if 'editing_test_case' not in st.session_state:
        st.session_state.editing_test_case = None
    if 'model_available' not in st.session_state:
        st.session_state.model_available = None


def check_model_availability():
    """Check if Ollama model is available."""
    if st.session_state.model_available is None:
        with st.spinner("Checking model availability..."):
            st.session_state.model_available = st.session_state.agent.check_model_availability()
    return st.session_state.model_available


def render_header():
    """Render the application header."""
    st.markdown('<h1 class="main-header">🧪 AI Test Case Generator Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Generate comprehensive test cases from software requirements using local LLMs</p>', unsafe_allow_html=True)


def render_requirement_input():
    """Render the requirement input section."""
    st.markdown('<h2 class="section-header">📝 Enter Software Requirement</h2>', unsafe_allow_html=True)

    requirement = st.text_area(
        "Describe the software feature you want to test:",
        value=st.session_state.current_requirement,
        height=120,
        placeholder="Example: A user should be able to register using name, email, and password. The email must be unique and the password must be at least 8 characters long.",
        help="Enter a clear description of the feature. Include any specific validation rules or constraints."
    ) or ""

    col1, col2, _ = st.columns([1, 1, 2])

    with col1:
        generate_clicked = st.button(
            "🚀 Generate Test Cases",
            type="primary",
            disabled=not requirement.strip() or not check_model_availability()
        )

    with col2:
        if st.button("🗑️ Clear"):
            st.session_state.current_requirement = ""
            st.session_state.generated_test_cases = []
            st.session_state.current_assumptions = []
            st.session_state.agent.clear_current_session()
            st.rerun()

    if not check_model_availability():
        st.error("⚠️ Ollama model not available. Please ensure Ollama is running and the model (llama3.2) is installed. Run: `ollama pull llama3.2`")

    return requirement, generate_clicked


def render_generation_result(requirement: str, generate_clicked: bool):
    """Handle test case generation and display results."""
    if generate_clicked and requirement.strip():
        with st.spinner("🤖 Analyzing requirement and generating test cases..."):
            try:
                test_cases, assumptions = st.session_state.agent.generate_test_cases(requirement)
                st.session_state.generated_test_cases = test_cases
                st.session_state.current_assumptions = assumptions
                st.session_state.current_requirement = requirement
                st.success(f"✅ Generated {len(test_cases)} test cases!")
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {str(e)}")
            except RuntimeError as e:
                st.error(f"❌ Generation failed: {str(e)}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


def render_assumptions():
    """Display assumptions made during generation."""
    if st.session_state.current_assumptions:
        with st.expander("📋 Assumptions Made", expanded=True):
            st.markdown('<div class="assumption-box">', unsafe_allow_html=True)
            for i, assumption in enumerate(st.session_state.current_assumptions, 1):
                st.markdown(f"{i}. {assumption}")
            st.markdown('</div>', unsafe_allow_html=True)


def get_priority_class(priority: str) -> str:
    """Get CSS class for priority badge."""
    priority_lower = priority.lower()
    if priority_lower == "high":
        return "priority-high"
    elif priority_lower == "medium":
        return "priority-medium"
    else:
        return "priority-low"


def get_scenario_class(scenario_type: str) -> str:
    """Get CSS class for scenario badge."""
    scenario_lower = scenario_type.lower()
    if scenario_lower == "positive":
        return "scenario-positive"
    elif scenario_lower == "negative":
        return "scenario-negative"
    else:
        return "scenario-edge"


def render_test_cases_table():
    """Render test cases in an editable table format."""
    if not st.session_state.generated_test_cases:
        return

    st.markdown('<h2 class="section-header">📊 Generated Test Cases</h2>', unsafe_allow_html=True)

    # Render assumptions first
    render_assumptions()

    # Convert to DataFrame for display
    df = export_to_dataframe(st.session_state.generated_test_cases)

    # Display as interactive table with editing
    st.markdown("### Test Cases Overview")

    # Use st.data_editor for editable table
    edited_df = st.data_editor(
        df,
        column_config={
            "Test Case ID": st.column_config.TextColumn("ID", width="small", disabled=True),
            "Scenario Type": st.column_config.SelectboxColumn(
                "Scenario",
                options=["Positive", "Negative", "Edge"],
                width="small"
            ),
            "Title": st.column_config.TextColumn("Title", width="medium"),
            "Preconditions": st.column_config.TextColumn("Preconditions", width="medium"),
            "Steps": st.column_config.TextColumn("Steps", width="large"),
            "Test Data": st.column_config.TextColumn("Test Data", width="medium"),
            "Expected Result": st.column_config.TextColumn("Expected Result", width="large"),
            "Priority": st.column_config.SelectboxColumn(
                "Priority",
                options=["High", "Medium", "Low"],
                width="small"
            ),
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic",
        key="test_cases_editor"
    )

    # Convert display columns back to the internal database field names.
    normalized_cases = normalize_test_case_records(edited_df.to_dict("records"))
    st.session_state.generated_test_cases = normalized_cases
    st.session_state.agent.set_current_test_cases(normalized_cases)

    # Action buttons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💾 Save to Database", type="primary"):
            save_to_database()

    with col2:
        csv_data = export_to_dataframe(st.session_state.generated_test_cases).to_csv(index=False)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with col3:
        if st.button("🗑️ Clear All"):
            st.session_state.generated_test_cases = []
            st.session_state.current_assumptions = []
            st.session_state.agent.clear_current_session()
            st.rerun()

    with col4:
        if st.button("🔄 Regenerate"):
            if st.session_state.current_requirement:
                with st.spinner("Regenerating test cases..."):
                    try:
                        test_cases, assumptions = st.session_state.agent.generate_test_cases(
                            st.session_state.current_requirement
                        )
                        st.session_state.generated_test_cases = test_cases
                        st.session_state.current_assumptions = assumptions
                        st.success("✅ Regenerated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Regeneration failed: {str(e)}")


def save_to_database():
    """Save current requirement and test cases to database."""
    if not st.session_state.current_requirement:
        st.error("No requirement to save")
        return

    if not st.session_state.generated_test_cases:
        st.error("No test cases to save")
        return

    try:
        req_id = st.session_state.agent.save_current_session(st.session_state.current_requirement)
        st.success(f"✅ Saved to database (Requirement ID: {req_id})")
    except Exception as e:
        st.error(f"❌ Save failed: {str(e)}")


def render_history():
    """Render the history section with saved requirements."""
    st.markdown('<h2 class="section-header">📚 History</h2>', unsafe_allow_html=True)

    history = st.session_state.agent.get_history()

    if not history:
        st.info("No saved requirements yet. Generate and save test cases to see them here.")
        return

    for req in history:
        with st.expander(f"📄 {req['requirement_text'][:80]}... ({req['test_case_count']} test cases) - {req['created_at']}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Requirement:** {req['requirement_text']}")
                st.write(f"**Created:** {req['created_at']}")
                st.write(f"**Test Cases:** {req['test_case_count']}")

            with col2:
                if st.button("📂 Load", key=f"load_{req['id']}"):
                    load_requirement(req['id'])

                if st.button("📥 Export CSV", key=f"export_{req['id']}"):
                    export_requirement_csv(req['id'])

                if st.button("🗑️ Delete", key=f"delete_{req['id']}", type="secondary"):
                    delete_requirement(req['id'])


def load_requirement(requirement_id: int):
    """Load a requirement and its test cases from database."""
    data = st.session_state.agent.load_requirement(requirement_id)
    if data:
        st.session_state.current_requirement = data['requirement_text']
        st.session_state.generated_test_cases = data.get('test_cases', [])
        st.session_state.current_assumptions = []
        st.success(f"✅ Loaded requirement with {len(st.session_state.generated_test_cases)} test cases")
        st.rerun()
    else:
        st.error("Failed to load requirement")


def export_requirement_csv(requirement_id: int):
    """Export a saved requirement's test cases to CSV."""
    data = st.session_state.agent.load_requirement(requirement_id)
    if data and data.get('test_cases'):
        csv_bytes = export_to_dataframe(data['test_cases']).to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=f"test_cases_req_{requirement_id}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            key=f"download_{requirement_id}"
        )
    else:
        st.error("No test cases to export")


def delete_requirement(requirement_id: int):
    """Delete a requirement from database."""
    if st.session_state.agent.delete_requirement(requirement_id):
        st.success("✅ Requirement deleted")
        st.rerun()
    else:
        st.error("Failed to delete requirement")


def render_sidebar():
    """Render the sidebar with info and settings."""
    with st.sidebar:
        st.markdown("## 🧪 AI Test Case Generator")
        st.markdown("---")

        st.markdown("### 📖 How to Use")
        st.markdown("""
        1. **Enter Requirement** - Describe the feature in plain English
        2. **Generate** - Click "Generate Test Cases"
        3. **Review** - Check the generated test cases
        4. **Edit** - Modify any test case inline
        5. **Save** - Store in database for later
        6. **Export** - Download as CSV
        """)

        st.markdown("---")
        st.markdown("### ⚙️ Settings")

        # Model selection
        model_options = ["llama3.2", "llama3.1", "mistral", "codellama"]
        selected_model = st.selectbox(
            "LLM Model",
            model_options,
            index=0,
            help="Select the Ollama model to use"
        )

        if st.button("🔄 Reload Model"):
            st.session_state.agent = create_agent(selected_model)
            st.session_state.model_available = None
            st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Test Case Types")
        st.markdown("""
        - **Positive** ✅ Valid inputs, happy paths
        - **Negative** ❌ Invalid inputs, errors
        - **Edge** 🔍 Boundaries, limits
        """)

        st.markdown("### 🎯 Priority Levels")
        st.markdown("""
        - **High** 🔴 Critical functionality
        - **Medium** 🟠 Standard features
        - **Low** 🟢 Nice-to-have
        """)

        st.markdown("---")
        st.markdown("### 🔧 Requirements")
        st.markdown("""
        - Python 3.8+
        - Streamlit
        - Ollama (local LLM)
        - LangChain
        - SQLite (built-in)
        """)

        st.markdown("---")
        st.caption("Built for Xpert Champs AI Engineering Internship")


def main():
    """Main application entry point."""
    # Initialize database
    init_database()

    # Initialize session state
    init_session_state()

    # Render sidebar
    render_sidebar()

    # Render header
    render_header()

    # Render requirement input
    requirement, generate_clicked = render_requirement_input()

    # Handle generation
    render_generation_result(requirement, generate_clicked)

    # Render test cases if available
    if st.session_state.generated_test_cases:
        render_test_cases_table()

    # Render history section
    st.markdown("---")
    render_history()


if __name__ == "__main__":
    main()