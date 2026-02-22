# AI Data Analyst

An intelligent desktop application for data analysis powered by AI. Upload datasets, ask questions, and get AI-generated analysis code with automatic execution, all with a beautiful Tkinter GUI.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [File Structure](#file-structure)
- [Features Deep Dive](#features-deep-dive)
- [API Configuration](#api-configuration)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Core Capabilities

- **Natural Language Queries**: Ask questions about your data in plain English
- **AI-Generated Code**: Automatically generates Python code for data analysis
- **Auto-Execution**: Generated code is executed in a sandboxed REPL environment
- **Inline Visualizations**: See matplotlib charts directly in the chat interface
- **Multi-Dataset Support**: Work with multiple CSV/Excel files simultaneously
- **Context Tracking**: Intelligent context management across sessions

### UI/UX Features

- **Dual Mode Interface**:
  - **Chat Mode**: Interactive Q&A with your data
  - **Data & Transformations Mode**: Manual data manipulation

- **Smart Settings**:
  - **Theme Support**: Dark/Light themes with persistent preferences
  - **Multi-LLM Support**: Switch between Groq, OpenAI, and Ollama
  - **API Key Management**: Securely store and manage LLM credentials

- **Data Management**:
  - Upload multiple files (CSV, XLSX, XLS)
  - DataFrame preview with scrolling
  - Remove datasets from context
  - Track DataFrames in sidebar

- **Code Transformation**:
  - **Python Mode**: Write custom Python transformations
  - **LLM Mode**: Describe transformations in English

### Analysis Features

- **Automatic Imports**: Detects and auto-imports common libraries (numpy, pandas, matplotlib, etc.)
- **Code Generation**: Produces clean, executable Python code
- **Data Descriptions**: Auto-generated summaries of created DataFrames
- **Recommended Analysis**: AI suggests follow-up questions based on current analysis
- **Bottom Panels**: View analysis summary and generated code side-by-side

---

## 🖥️ System Requirements

### Minimum Requirements

- **Python**: 3.8+
- **RAM**: 4GB
- **Display**: 1400x850 minimum resolution
- **OS**: Windows, macOS, or Linux

### For Full Functionality

- **Internet**: Required for cloud LLM backends (Groq, OpenAI)
- **Ollama** (optional): For local LLM inference

---

## 📦 Installation

### Step 1: Clone or Download

```bash
cd "c:\Ashad\ML Project\ExperimentAI\AIDataAnalyst"
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Core Dependencies:**
```
pandas>=1.3.0
tkinter  (usually comes with Python)
matplotlib>=3.4.0
langgraph>=0.0.1
langchain>=0.1.0
langchain-core>=0.1.0
groq>=0.9.0  # For Groq backend
openai>=1.0.0  # For OpenAI backend
```

### Step 3: Run the Application

```bash
python app.py
```

---

## ⚙️ Configuration

### config.json Structure

The app uses `config.json` to store persistent settings:

```json
{
  "theme": "dark",
  "llm_backend": "groq",
  "groq_api_key": "your_groq_api_key_here",
  "openai_api_key": "your_openai_api_key_here",
  "ollama_model": "llama3.1:8b"
}
```

### Initial Setup

1. **Launch the app**: `python app.py`
2. **Open Settings**: Click the ⚙ Settings button (bottom right)
3. **Choose Theme**: Select Dark or Light
4. **Select LLM Backend**: Choose Groq, OpenAI, or Ollama
5. **Add API Keys**: Enter credentials for your chosen backend
6. **Save**: Click Save to persist settings

---

## 🚀 Usage

### Basic Workflow

#### 1. Upload Data
```
1. Click "Upload Files" in the sidebar
2. Select CSV, XLSX, or XLS files
3. DataFrames appear in the "IN CONTEXT" list
```

#### 2. Ask Questions (Chat Mode)
```
1. Switch to "Chat Mode" (top bar)
2. Enter your question: "What is the correlation between price and quantity?"
3. Click "Run"
4. AI analyzes data and generates code
5. View results in chat + visualizations inline
6. Check "Summary" tab for analysis details
7. Check "Generated Code" tab to see the code
```

#### 3. Transform Data (Data & Transformations Mode)
```
1. Switch to "Data & Transformations" (top bar)
2. Select DataFrame from dropdown
3. Choose mode:
   - Python Mode: Write Python pandas code manually
   - LLM Mode: Describe transformation in English
4. Click "Apply Data Transformation"
5. Preview updated data with "Preview" button
```

#### 4. Configure Settings
```
1. Click ⚙ Settings (bottom right)
2. Modify theme, LLM backend, or API keys
3. Click "Save"
4. Restart app for full theme changes
```

---

## 🏗️ Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────┐
│         UI Layer (app.py)           │
│   Tkinter GUI, Settings, Chat       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Configuration Layer (config.json) │
│  Theme, LLM Backend, API Keys       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Core Layer (ai_core.py)        │
│  LLM, REPL, Workflow, Tools         │
└─────────────────────────────────────┘
```

### Data Flow

```
User Query
    ↓
[Chat Mode Interface]
    ↓
[LangGraph Workflow]
    ├─ Analyze Data (LLM)
    ├─ Generate Code (LLM)
    └─ Execute Code (REPL)
    ↓
[Results + Visualizations]
    ├─ Chat Display
    ├─ Analysis Summary
    ├─ Generated Code
    └─ Figures
```

---

## 📁 File Structure

```
AIDataAnalyst/
├── app.py                    # Main GUI application
├── ai_core.py               # LLM and workflow engine
├── config.json              # Settings (auto-created)
├── README.md                # This file
└── requirements.txt         # Python dependencies
```

### app.py (559 lines)

**Components:**
- `SettingsDialog`: Settings UI with theme and LLM configuration
- `DataAnalystApp`: Main application class
  - `build_layout()`: UI structure
  - `build_chat_view()`: Chat interface
  - `build_data_view()`: Data transformation interface
  - `run_analysis()`: Execute analysis workflow
  - `apply_transformation()`: Apply data transforms

**Key Functions:**
- `load_config()`: Load settings from config.json
- `save_config()`: Persist settings
- Configuration management

### ai_core.py (527 lines)

**Sections:**

1. **LLM Configuration** (lines 22-90)
   - `get_llm()`: Factory function for LLM instances
   - `_load_config()`: Load config.json
   - LLM initialization

2. **REPL Environment** (lines 93-193)
   - `REPL_GLOBALS`: Execution namespace
   - `COMMON_MODULES`: Auto-import mappings
   - Helper functions for imports

3. **REPL Helper Functions** (lines 196-233)
   - `detect_missing_imports()`: Find required imports
   - `try_auto_import()`: Auto-import common aliases
   - `fix_main_execution()`: Handle `__name__ == "__main__"`
   - `custom_repl()`: Execute user code safely

4. **Tools & Utilities** (lines 238-264)
   - `repl_tool`: LangChain tool wrapper
   - `data_description()`: Generate DataFrame summaries

5. **Data Analysis Workflow** (lines 267-455)
   - `analyze_data()`: Analyze datasets (LLM)
   - `generate_code()`: Generate analysis code (LLM)
   - `execute_code()`: Execute generated code (REPL)
   - `handle_followup()`: Process follow-up queries

6. **LangGraph Compilation** (lines 458-528)
   - `workflow`: StateGraph definition
   - `graph`: Compiled workflow

---

## 🔧 Features Deep Dive

### Chat Mode Analysis

**Step 1: Data Analysis**
- LLM receives DataFrame schemas and summary
- Understands user intent from query
- Generates comprehensive analysis prompt

**Step 2: Code Generation**
- LLM creates Python code for analysis
- Code includes:
  - Data filtering/aggregation
  - Visualization (matplotlib/seaborn)
  - DataFrame descriptions (for new DataFrames)
  - Recommended follow-up questions

**Step 3: Code Execution**
- Code runs in isolated REPL environment
- Auto-imports: numpy, pandas, matplotlib, seaborn, sklearn, scipy
- File I/O restricted (security)
- Matplotlib figures saved inline
- Execution output captured

**Step 4: Results Display**
- Chat interface shows user query + AI response
- Figures embedded in chat panel
- Summary tab: LLM's analysis of data
- Code tab: Generated Python code

### Data Transformation

**Python Mode:**
```python
# You write Python code directly
import pandas as pd
df['new_column'] = df['col1'] * df['col2']
df = df[df['price'] > 100]
```

**LLM Mode:**
```
Input: "Remove rows where price is less than 100 and create a discount column"
Output: Generated Python code that does exactly that
```

### Theme System

**Dark Theme (Default):**
- Background: #1e1e1e
- Panel: #252526
- Input: #2d2d2d
- Text: #d4d4d4
- Accent: #0e639c

**Light Theme:**
- Background: #ffffff
- Panel: #f3f3f3
- Input: #eeeeee
- Text: #333333
- Accent: #0078d4

---

## 🔑 API Configuration

### Groq API

**Get API Key:**
1. Visit https://console.groq.com/keys
2. Sign up/Log in
3. Create new API key
4. Copy to Settings

**Model:** `llama-3.3-70b-versatile` (included)

### OpenAI API

**Get API Key:**
1. Visit https://platform.openai.com/api-keys
2. Sign up/Log in
3. Create new secret key
4. Copy to Settings

**Model:** `gpt-3.5-turbo` (configurable in code)

### Ollama (Local)

**Setup:**
1. Download: https://ollama.ai
2. Run: `ollama serve`
3. Pull model: `ollama pull llama2` (or llama3.1:8b)
4. In Settings, enter model name and base URL

**Models:**
- `llama2` - 7B parameters
- `llama3.1:8b` - 8B parameters
- `mistral` - 7B parameters
- `neural-chat` - 7B parameters

---

## 📊 Demo Screenshots

### Chat Mode
```
- User query at top
- AI response in middle
- Inline visualization
- Summary and Code tabs at bottom
```
![Chat Screen](https://github.com/Ashad-Ahmed/AIDataAnalyst/blob/main/DemoScreenShots_AIDataAnalyst/Query%20And%20Response.png?raw=true)

### Settings Dialog
```
- Theme selection (Dark/Light)
- LLM Backend selection (Groq/OpenAI/Ollama)
- API Key input fields
- Save/Cancel buttons
```
![Setting](https://github.com/Ashad-Ahmed/AIDataAnalyst/blob/main/DemoScreenShots_AIDataAnalyst/Settings.png?raw=true)

### Data Transformations Mode
```
- DataFrame selector
- Python/LLM mode toggle
- Code editor
- Preview panel
- Apply button
```
![Data Transformation](https://github.com/Ashad-Ahmed/AIDataAnalyst/blob/main/DemoScreenShots_AIDataAnalyst/Data%20Transformation%20Mode.png?raw=true)

### Sidebar with Datasets
```
- "IN CONTEXT" label
- Loaded DataFrames list
- Upload Files button
- Remove Selected button
```
![Side Bar](https://github.com/Ashad-Ahmed/AIDataAnalyst/blob/main/DemoScreenShots_AIDataAnalyst/SideBar.png?raw=true)

---

## 🔍 Workflow Example

### Query: "What is the average price by category?"

**Step 1: Data Analysis**
```
LLM receives:
- sales_data: 1000 rows, columns: category, price, quantity, date
- User query: "What is the average price by category?"
```

**Step 2: Code Generation**
```python
import pandas as pd
import matplotlib.pyplot as plt

# Analyze average price by category
avg_price_by_category = sales_data.groupby('category')['price'].mean().sort_values(ascending=False)

# Create visualization
plt.figure(figsize=(10, 5))
avg_price_by_category.plot(kind='bar')
plt.title('Average Price by Category')
plt.xlabel('Category')
plt.ylabel('Average Price')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('price_by_category.png')

# Data description for new dataframes
data_description_dict = {
    'avg_price_by_category': 'Average price for each product category'
}

# Recommendations for follow-up
recommended_analysis = [
    'What is the total quantity sold by category?',
    'Which category has the highest variance in price?',
    'How does category performance trend over time?'
]
```

**Step 3: Execution**
- Code executes in REPL
- DataFrame created
- Figure generated (PNG)
- Output captured

**Step 4: Display**
```
USER: What is the average price by category?

AI: Based on the analysis of your sales_data, here's the average
    price by category. The most expensive category is Electronics
    with an average price of $450, followed by Home & Garden...

[Bar Chart Visualization]

Summary: Electronics has the highest average price at $450...

Generated Code: [Full Python code shown]

Recommended Analysis:
1. What is the total quantity sold by category?
2. Which category has the highest variance in price?
3. How does category performance trend over time?
```

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'groq'"

**Solution:**
```bash
pip install groq
```

### Issue: "API Key Error" when saving settings

**Cause:** Invalid or empty API key

**Solution:**
1. Get valid API key from provider (see [API Configuration](#api-configuration))
2. Enter complete key (no spaces at start/end)
3. Save again

### Issue: Ollama connection refused

**Solutions:**
1. Ensure Ollama is running: `ollama serve`
2. Check base URL: Default is `http://localhost:11434`
3. Verify model exists: `ollama list`
4. Pull model if missing: `ollama pull llama3.1:8b`

### Issue: GUI appears frozen during analysis

**Cause:** Long-running analysis

**Solution:**
- Wait for analysis to complete (check console for progress)
- Large datasets may take longer
- Consider filtering data first

### Issue: Matplotlib figures not displaying

**Cause:** matplotlib backend issue

**Solution:**
- Already configured to use "Agg" backend (non-interactive)
- Ensures figures save correctly
- Try restarting app

### Issue: "Not enough context" error from LLM

**Cause:** Dataset too large or query too complex

**Solution:**
1. Remove unnecessary columns
2. Filter data to smaller subset
3. Ask more specific questions
4. Try different LLM backend

---

## 🔐 Security Considerations

### Code Execution

- **Sandboxed REPL**: Code runs in isolated namespace
- **No File I/O**: Cannot read/write arbitrary files
- **Limited Imports**: Only safe modules available
- **Timeout Protection**: Long-running code can be interrupted

### API Keys

- **Local Storage**: Keys stored in local config.json
- **Environment Variables**: Can use `.env` instead
- **Secure**: Never transmitted unless to LLM API
- **User Responsibility**: Manage key access carefully

---

## 📝 Configuration Examples

### Using Environment Variables

Instead of storing API keys in config.json:

```bash
# Windows
set GROQ_API_KEY=your_key_here
set OPENAI_API_KEY=your_key_here

# macOS/Linux
export GROQ_API_KEY=your_key_here
export OPENAI_API_KEY=your_key_here
```

### Custom Ollama Model

Edit `config.json`:
```json
{
  "ollama_model": "neural-chat:latest"
}
```

---

## 🤝 Contributing

### Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Document complex functions

### Areas for Enhancement

- [ ] Export analysis reports (PDF, HTML)
- [ ] Multi-language support
- [ ] Advanced analytics (statistical tests)
- [ ] Real-time collaboration
- [ ] Custom prompt templates

---

## 📄 License

This project is for educational and research purposes.

---

## 📞 Support

### Common Resources

- **Groq Docs**: https://console.groq.com/docs
- **OpenAI Docs**: https://platform.openai.com/docs
- **Ollama Docs**: https://ollama.ai
- **Pandas Docs**: https://pandas.pydata.org/docs
- **LangGraph**: https://langchain-ai.github.io/langgraph

### Debug Mode

To see detailed logs:

```python
# In app.py or ai_core.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 🎯 Future Roadmap

- [ ] Database integration (SQLite, PostgreSQL)
- [ ] Real-time data streaming
- [ ] Advanced visualization gallery
- [ ] Model fine-tuning support
- [ ] Collaborative notebooks
- [ ] CLI version
- [ ] Web version (FastAPI + React)

---

**Last Updated:** February 2026
**Version:** 1.0
