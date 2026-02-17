# LLM SETUP

import os

# Choose LLM Backend: 'ollama' or 'groq'
LLM_BACKEND = os.getenv("LLM_BACKEND", "groq")  # Change this environment variable as needed

# Initialize LLM
if LLM_BACKEND == "groq":
    from groq import Groq

    class GroqLLM:
        def __init__(self, model="llama-3-70b", api_key="gsk_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"):
            self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
            self.model = model

        def invoke(self, prompt):
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
            )
            return completion.choices[0].message.content

    llm = GroqLLM(model="llama-3.3-70b-versatile")
else:
    llm = Ollama(model="llama3.1:8b", temperature=0.5)

# MY REPL!!

import sys
import io
import ast
import builtins
import contextlib
import importlib
import matplotlib.pyplot as plt
import re
import uuid

# Persistent environment
REPL_GLOBALS = {
    "__builtins__": {
        "abs": abs,
        "all": all,
        "any": any,
        "ascii": ascii,
        "bin": bin,
        "bool": bool,
        "breakpoint": breakpoint,
        "bytearray": bytearray,
        "bytes": bytes,
        "callable": callable,
        "chr": chr,
        "classmethod": classmethod,
        "compile": compile,
        "complex": complex,
        "delattr": delattr,
        "dict": dict,
        "dir": dir,
        "divmod": divmod,
        "enumerate": enumerate,
        "eval": eval,
        "exec": exec,
        "filter": filter,
        "float": float,
        "format": format,
        "frozenset": frozenset,
        "getattr": getattr,
        "globals": globals,
        "hasattr": hasattr,
        "hash": hash,
        "help": help,
        "hex": hex,
        "id": id,
        "input": input,
        "int": int,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "iter": iter,
        "len": len,
        "list": list,
        "locals": locals,
        "map": map,
        "max": max,
        "memoryview": memoryview,
        "min": min,
        "next": next,
        "object": object,
        "oct": oct,
        "open": open,
        "ord": ord,
        "pow": pow,
        "print": print,
        "property": property,
        "range": range,
        "repr": repr,
        "reversed": reversed,
        "round": round,
        "set": set,
        "setattr": setattr,
        "slice": slice,
        "sorted": sorted,
        "staticmethod": staticmethod,
        "str": str,
        "sum": sum,
        "super": super,
        "tuple": tuple,
        "type": type,
        "vars": vars,
        "zip": zip,
        "__import__": __import__,
        # Common exceptions
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "IndexError": IndexError,
        "KeyError": KeyError,
        "FileNotFoundError": FileNotFoundError,
        "ZeroDivisionError": ZeroDivisionError,
        "ImportError": ImportError,
        "NameError": NameError,
        "StopIteration": StopIteration,
        "RuntimeError": RuntimeError,
    },
    "__name__": "__main__",
}

# Known modules and their aliases
COMMON_MODULES = {
    "np": "numpy",
    "pd": "pandas",
    "plt": "matplotlib.pyplot",
    "sns": "seaborn",
    "sk": "sklearn",
    "sp": "scipy",
}

def detect_missing_imports(user_code):
    """Detect symbols used that may require auto-importing."""
    tree = ast.parse(user_code)
    used_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    already_imported = set(REPL_GLOBALS.keys())
    missing = used_names - already_imported - set(dir(builtins))
    return missing

def try_auto_import(name):
    """Try to auto-import common aliases."""
    module_name = COMMON_MODULES.get(name)
    if module_name:
        try:
            module = importlib.import_module(module_name)
            REPL_GLOBALS[name] = module
            return f"# Auto-imported {module_name} as {name}"
        except ImportError:
            return f"# Failed to auto-import {name}"
    return None

def fix_main_execution(user_code):
    """Detects and modifies `if __name__ == '__main__':` statements to work inside REPL."""
    modified_code = user_code
    main_match = re.search(r"if\s+__name__\s*==\s*[\"']__main__[\"']:\s*\n(\s+)(\w+)\(\)", user_code)

    if main_match:
        indent, main_func = main_match.groups()
        modified_code = re.sub(r"if\s+__name__\s*==\s*[\"']__main__[\"']:\s*\n" + indent + main_func + r"\(\)",
                               f"{main_func}()", user_code)
        return modified_code, f"# Modified main execution: Auto-ran `{main_func}()`"

    return modified_code, None

import os
import matplotlib.pyplot as plt

# Modify custom_repl function to save plots
def custom_repl(user_code: str, context_vars: dict = None, return_globals: bool = False):
    import io
    import contextlib
    import uuid

    stdout = io.StringIO()
    stderr = io.StringIO()

    # Step 1: Detect and auto-import
    missing = detect_missing_imports(user_code)
    import_logs = [try_auto_import(name) for name in missing]

    # Step 2: Fix `if __name__ == "__main__"` issue
    user_code, main_log = fix_main_execution(user_code)
    if main_log:
        import_logs.append(main_log)

    # Step 3: Use a shared REPL global environment
    global REPL_GLOBALS
    if context_vars:
        REPL_GLOBALS.update(context_vars)

    # Step 4: Execute the code
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            exec(user_code, REPL_GLOBALS)
        except Exception as e:
            print(f"⚠️ Execution Error: {e}")

    # Step 5: Capture outputs and visualizations
    out = stdout.getvalue() + stderr.getvalue()
    logs = "\n".join(filter(None, import_logs))
    result_value = REPL_GLOBALS.get("agent_result", None)

    # Collect all active matplotlib figures
    figures = [plt.figure(i) for i in plt.get_fignums()]

    # Save all the figures with unique names
    figure_paths = []
    for fig in figures:
        fig_name = f"figure_{str(uuid.uuid4())}.png"
        fig_path = os.path.join(os.getcwd(), fig_name)  # Save in the current directory
        fig.savefig(fig_path, format="png", bbox_inches="tight")
        figure_paths.append(fig_path)

    if return_globals:
        return {
            "stdout": f"{logs}\n{out}" if logs else out,
            "agent_result": result_value,
            "globals": REPL_GLOBALS.copy(),
            "figure_paths": figure_paths  # Save the paths
        }

    return {
        "stdout": f"{logs}\n{out}" if logs else out,
        "agent_result": result_value,
        "figure_paths": figure_paths  # Save the paths
    }

import pandas as pd
from langgraph.graph import StateGraph
from langchain.llms import Ollama
from langchain_core.tools import Tool
from langchain_core.runnables import RunnableLambda

repl_tool = Tool(
    name="custom_repl",
    description="A dynamic Python shell that automatically handles imports and executes code.",
    func=custom_repl
)

def data_description(df, name="df"):
    column_info = []
    for col in df.columns:
        col_data = {
            "column_name": col,
            "dtype": str(df[col].dtype)
        }
        column_info.append(col_data)

    summary = {
        "dataframe_name": name,
        "schema": column_info,
        "sample_rows": df.head(1).to_dict(orient="records")
    }

    return summary

# 🔍 Step 1: Analyze dataframes and user query
def analyze_data(state):
    dfs = state.get("dfs", [])
    user_query = state.get("user_query", "")

    try:
        all_summaries = []
        for entry in dfs:

            df = entry["data"]
            name = entry["name"]

            description = entry.get("description", "No description provided.")
            summary = data_description(df, name=name)

            all_summaries.append({
                "name": name,
                "description": description,
                "summary": summary
            })
    except Exception as e:
        return {"analysis": f"⚠️ Execution Error: {str(e)}", "dfs": dfs, "user_query": user_query}

    prompt = "You are analyzing **multiple datasets**. Each dataset has a description and a summarized view. Use these to understand the context and help generate insights or code.\n\n"
    for item in all_summaries:
        prompt += f"📄 Dataset: {item['name']}\n📝 Description: {item['description']}\n📊 Summary: {item['summary']}\n\n"

    prompt += f"💬 User Request:\n{user_query}"

    response = llm.invoke(prompt)
    return {
        "analysis": response if isinstance(response, str) else response.content,
        "dfs": dfs,
        "user_query": user_query
    }

# 🧠 Step 2: Generate Python code
import re

def generate_code(state):

    analysis = state.get("analysis", "")
    user_query = state.get("user_query", "")

    prompt = f"""
    You are a creative and intelligent Python data analysis assistant. Your goal is to help users extract insights, perform analysis, and create meaningful visualizations from pandas DataFrames they provide.

    Context:
    - You are provided with multiple pandas DataFrames already loaded into memory.
    - Each DataFrame has a variable name along with a short description. You can directly use them with their variable names in your Python code.
    - You will receive a summary of each DataFrame (including column names, data types, sample values, statistics, and missing data info) along with a user request.

    Instructions:
    1. DO NOT include any code for reading files (e.g., pd.read_csv or pd.read_excel).
    2. DO NOT hardcode any DataFrames in your code — use only those passed as variables.
    3. DO NOT ASSUME ANY COLUMN NAMES.
    4. Write clean, executable Python code using best practices.
    5. Include relevant visualizations (matplotlib or seaborn) if they enhance understanding.
    
    IMPORTANT:
    - At the end of your code, define a dictionary called `data_description_dict` and add short, human-readable descriptions for any **important** DataFrames your code created or transformed.
    - Also create a list named `recommended_analysis` where you suggest 3 other **simple, text-based data analysis questions** that a user may want to explore based on the current dataset and their original question.
    - These questions should be:
        - Exploratory in nature (e.g. comparisons, aggregations, filtering, visualizations)
        - Answerable via basic Python and pandas
        - NOT involve predictive modeling, ML, or external tools like dashboards
        - Realistically answerable by a text-based LLM in code form

    Begin by analyzing the following datasets and user request:

    📊 Dataset Analysis:
    {analysis}

    💬 User Request:
    {user_query}
    """

    # Get LLM response
    response = llm.invoke(prompt)
    code = response if isinstance(response, str) else response.content

    # 1. Match all Python code blocks (both with and without language specifier)
    python_code_blocks = re.findall(r'```python(.*?)```', code, re.DOTALL)

    # 2. If no Python code blocks with "python" found, look for generic code blocks (```...``` without language)
    if not python_code_blocks:
        python_code_blocks = re.findall(r'```(.*?)```', code, re.DOTALL)

    # 3. Clean up and concatenate all found code blocks
    cleaned_code = "\n".join([block.strip() for block in python_code_blocks])

    return {
        "generated_code": cleaned_code,
        "dfs": state.get("dfs"),
        "user_query": user_query
    }


# 🧪 Step 3: Execute code with REPL
def execute_code(state):

    code = state.get("generated_code", "").strip()
    dfs = state.get("dfs", [])
    ledger = state.get("context_ledger", {})
    user_query = state.get("user_query")

    print("\n📝 Generated Python Code:\n")

    # Inject existing DataFrames
    context_vars = {entry["name"]: entry["data"] for entry in dfs}
    injected_names = set(context_vars.keys())

    # Add injected DataFrames to the ledger if missing
    for entry in dfs:

        name = entry["name"]
        df = entry["data"]
        description = entry.get("description", "No description provided.")
        
        if name not in ledger:
            try:
                summary = data_description(df, name=name)
                ledger[name] = {
                    "description": description,
                    "summary": summary
                }
            except Exception as e:
                print(f"⚠️ Error summarizing injected DataFrame '{name}': {e}")


    # Execute the code in REPL
    result = repl_tool.func(code, context_vars=context_vars, return_globals=True)
    output = result["stdout"]
    exec_globals = result["globals"]
    df_descriptions = exec_globals.get("data_description_dict", {})
    recommended_analysis = exec_globals.get("recommended_analysis", [])
    figure_paths = result.get("figure_paths", ["Dummy.png"])

    # Detect and register only important DataFrames as per data_description_dict
    for var_name, val in exec_globals.items():

        if (
            isinstance(val, pd.DataFrame)
            and var_name in df_descriptions  # ✅ Only track if LLM provided a description
            and var_name not in injected_names
            and var_name not in ledger
        ):
            try:
                summary = data_description(val, name=var_name)
                description = df_descriptions[var_name]
                ledger[var_name] = {
                    "description": description,
                    "summary": summary
                }
                dfs.append({"name": var_name, "data": val, "description": description})
            except Exception as e:
                print(f"⚠️ Error summarizing new DataFrame '{var_name}': {e}")


    print("\n🚀 Execution Output:\n")

    return {
        "execution_output": output,
        "generated_code": code,
        "dfs": dfs,
        "user_query": user_query,
        "context_ledger": ledger,
        "recommended_analysis": recommended_analysis,
        "figure_paths": figure_paths
    }

"""
def handle_followup(followup_query, previous_state):
    new_state = {
        "dfs": previous_state["dfs"],
        "context_ledger": previous_state["context_ledger"],
        "user_query": followup_query,
    }

    updated_state = graph.invoke(new_state)
    # Re-analyze to get fresh analysis for follow-up UI display
    analysis_state = analyze_data(updated_state)
    updated_state["analysis"] = analysis_state.get("analysis", "")

    return updated_state  # ← Return the updated state to caller
"""

def handle_followup(followup_query, previous_state):
    new_state = {
        "dfs": previous_state["dfs"],
        "context_ledger": previous_state["context_ledger"],
        "user_query": followup_query,
    }

    # Step 1: Fresh analysis for follow-up
    analysis_state = analyze_data(new_state)
    new_state["analysis"] = analysis_state.get("analysis", "")

    # Step 2: Generate code from new analysis
    code_state = generate_code(new_state)
    new_state["generated_code"] = code_state.get("generated_code", "")

    # Step 3: Execute new code and update everything
    final_state = execute_code(new_state)

    return final_state





# 🧠 LangGraph Workflow Definition
workflow = StateGraph(dict)
workflow.add_node("analyze_data", RunnableLambda(analyze_data))
workflow.add_node("generate_code", RunnableLambda(generate_code))
workflow.add_node("execute_code", RunnableLambda(execute_code))

workflow.set_entry_point("analyze_data")
workflow.add_edge("analyze_data", "generate_code")
workflow.add_edge("generate_code", "execute_code")

graph = workflow.compile()

"""
# 🧪 Sample Usage
if __name__ == "__main__":

    df1 = pd.read_csv("df1.csv")
    df2 = pd.read_csv("df2.csv")

    dfs = [
        {"name": "supplier_spend_df", "data": df1, "description": "Q1 Supplier Spend Data"},
        {"name": "supplier_risk_scores_df", "data": df2, "description": "Supplier Risk Assessment Scores"}
    ]

    #user_query = "Find high-risk suppliers who also had the highest spends."
    #user_query = "Create a pie chart showing total spend amount per supplier, highlighting suppliers with high risk levels."
    user_query =  "What kind of different analysis can be done using these dataframes."
    initial_state = {"dfs": dfs, "user_query": user_query}
    final_state = graph.invoke(initial_state)
"""