# AI Test Case Generator Agent

An AI-powered web application that helps software testers create comprehensive test cases from plain-language software requirements. Built with Streamlit, LangChain, and local LLMs via Ollama.

## 🚀 Features

- **Requirement Analysis**: Enter software requirements in plain English
- **Intelligent Test Generation**: AI generates positive, negative, and edge-case test scenarios
- **Structured Test Cases**: Each case includes ID, scenario type, title, preconditions, steps, test data, expected results, and priority
- **Interactive Editing**: Review and modify generated test cases inline
- **Persistence**: Save requirements and test cases to SQLite database
- **History**: View and reload previously saved test cases
- **Export**: Download test cases as CSV files
- **Local LLM**: Runs entirely offline using Ollama (no API keys needed)

## 📋 Requirements

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- At least one LLM model pulled (default: `llama3.2`)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-test-case-generator-agent
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install and start Ollama**
   ```bash
   # Install Ollama from https://ollama.ai/
   
   # Pull the default model
   ollama pull llama3.2
   
   # Start Ollama service (run in separate terminal)
   ollama serve
   ```

## ▶️ Usage

1. **Start the application**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Enter a requirement** in the text area, for example:
   > "A user should be able to register using name, email, and password. The email must be unique and the password must be at least 8 characters long."

4. **Click "Generate Test Cases"** - The AI will analyze the requirement and create structured test cases

5. **Review and edit** the generated test cases in the interactive table

6. **Save to database** or **Export as CSV** for use in your testing workflow

## 🧪 Running Tests

```bash
python -m unittest discover -s tests -v
```

## 📁 Project Structure

```
ai-test-case-generator-agent/
├── app.py                 # Main Streamlit application
├── agent.py               # Agent orchestration logic
├── test_case_generator.py # LLM interaction and response validation
├── prompts.py             # Prompt templates for the LLM
├── database.py            # SQLite database operations
├── export_utils.py        # CSV export utilities
├── requirements.txt       # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## 🔧 Configuration

### Changing the LLM Model

Edit `agent.py` or use the sidebar in the UI to select a different model:
- `llama3.2` (default, balanced)
- `llama3.1` (previous version)
- `mistral` (faster, good for code)
- `codellama` (specialized for code)

```bash
# Pull additional models
ollama pull mistral
ollama pull codellama
```

### Database

The application uses SQLite (`test_cases.db`) which is created automatically. No configuration needed.

## 🎯 Test Case Structure

Each generated test case includes:

| Field | Description |
|-------|-------------|
| Test Case ID | Unique identifier (TC-01, TC-02, etc.) |
| Scenario Type | Positive / Negative / Edge |
| Title | Descriptive test case name |
| Preconditions | Setup required before test execution |
| Steps | Numbered test execution steps |
| Test Data | Specific input values to test |
| Expected Result | Expected outcome |
| Priority | High / Medium / Low |

## 🧪 Example Output

**Input Requirement:**
> "A user should be able to register using name, email, and password."

**Generated Test Cases:**

| ID | Scenario | Title | Priority |
|----|----------|-------|----------|
| TC-01 | Positive | Valid registration with all fields | High |
| TC-02 | Negative | Empty email field | High |
| TC-03 | Negative | Invalid email format | Medium |
| TC-04 | Edge | Password below minimum length | Medium |
| TC-05 | Edge | Duplicate email registration | High |

## ⚠️ Important Notes

1. **Human Review Required**: AI-generated test cases must be reviewed by a human before use in actual testing
2. **Assumptions**: The AI marks assumptions clearly - verify these match your application
3. **Local Model**: Quality depends on the Ollama model used; larger models generally produce better results
4. **No Internet Required**: Everything runs locally after initial model download

## 🐛 Troubleshooting

### "Ollama model not available"
- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Pull the model: `ollama pull llama3.2`

### "Connection refused" errors
- Ollama service may not be running
- Check firewall settings
- Default Ollama port is 11434

### Poor quality test cases
- Try a larger model: `ollama pull llama3.2:70b` (requires more RAM)
- Provide more detailed requirements
- Check the assumptions listed by the AI

## 📝 License

This project is created for the Xpert Champs AI Engineering Internship.

## 🤝 Contributing

This is an internship project. For suggestions or issues, please contact the project maintainers.

## 📚 References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [SQLite Documentation](https://www.sqlite.org/docs.html)