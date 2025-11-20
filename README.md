# Dependency Explanation Assistant

An intelligent tool that provides natural language explanations for Python dependency conflicts, helping developers understand not just what conflicts exist, but why they occur and how to resolve them.

## Features

- 🔍 **Automatic Conflict Detection**: Identifies version conflicts and compatibility issues
- 🤖 **AI-Powered Explanations**: Uses LLM to generate clear, natural language explanations
- 📖 **Why It Happens**: Explains the technical reasons behind conflicts
- 🔧 **How to Fix**: Provides actionable solutions for resolving conflicts
- 📊 **Visual Interface**: Clean Streamlit-based UI for easy interaction

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd problem3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the App

1. **Upload a requirements.txt file** OR **paste requirements.txt content**
2. Click **"Analyze Dependencies"**
3. Review detailed explanations for any conflicts found
4. Each conflict includes:
   - Summary of the conflict
   - Natural language explanation
   - Why the conflict happens
   - How to fix it
   - Severity level

## Project Structure

```
problem3/
├── app.py                 # Main Streamlit application
├── dependency_parser.py   # Parses requirements.txt files
├── conflict_detector.py  # Detects conflicts and compatibility issues
├── explanation_engine.py # Generates LLM-powered explanations
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## How It Works

1. **Parsing**: Extracts packages and version constraints from requirements.txt
2. **Detection**: Identifies conflicts using rule-based compatibility checks
3. **Explanation**: Uses LLM (Hugging Face Inference API) to generate explanations
4. **Fallback**: If LLM is unavailable, uses rule-based explanations

## Example

**Input:**
```
torch==1.8.0
pytorch-lightning==2.2.0
pandas==2.0.3
```

**Output:**
- Detects conflict between torch and pytorch-lightning
- Explains: "PyTorch Lightning 2.0+ requires PyTorch 2.0 or higher..."
- Suggests: "Upgrade PyTorch to 2.0+ or downgrade PyTorch Lightning to 1.x"

## Technologies Used

- **Streamlit**: Web interface
- **Packaging**: Python package version parsing
- **Hugging Face Inference API**: Free LLM for explanations
- **Requests**: API calls

## License

MIT License

## Contributing

Feel free to submit issues or pull requests!

