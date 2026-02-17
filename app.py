import streamlit as st
import pandas as pd
import os
import math
from ai_core import graph, handle_followup, data_description, custom_repl

# --- Session State Initialization ---
if "dfs" not in st.session_state:
    st.session_state.dfs = []
if "state" not in st.session_state:
    st.session_state.state = None
if "history" not in st.session_state:
    st.session_state.history = []
if "followup_counter" not in st.session_state:
    st.session_state.followup_counter = 0
if "figure_paths_history" not in st.session_state:
    st.session_state.figure_paths_history = []

st.set_page_config(page_title="AI Data Analyst", layout="wide")

st.title("AI-Powered Data Analyst")

#st.markdown("Upload CSV/XLSX files and ask a question. The system will analyze your data, run code, and give recommendations!")

# --- File Uploader ---
uploaded_files = st.file_uploader("Upload CSV/XLSX files and ask a question. The system will analyze your data, run code, and give recommendations!", type=["csv", "xlsx", "xls"], accept_multiple_files=True, key="main_uploader")

if uploaded_files:
    for i, file in enumerate(uploaded_files, start=1):
        ext = file.name.split(".")[-1].lower()
        try:
            if ext == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            description_initial = st.text_input(f"Enter description for {file.name}", f"User uploaded file: {file.name}", key= f"initial_file{i}")

            temp_file_name = file.name.split(".")[0]

            if temp_file_name not in [x['name'] for x in st.session_state.dfs]:

                st.session_state.dfs.append({
                    "name": temp_file_name,
                    "data": df,
                    "description": description_initial
                })

            st.success(f"✅ Loaded: {file.name} as {temp_file_name}")
        except Exception as e:
            st.error(f"❌ Failed to read {file.name}: {e}")

# --- User Query ---
st.markdown("### 💬 Enter your analysis query:")
user_query = st.text_area("Example: 'Find high-risk suppliers who had highest spend'", height=100)

# --- Submit Query Button ---
if st.button("🚀 Run Analysis", type="primary") and st.session_state.dfs and user_query.strip():

    initial_state = {
        "dfs": st.session_state.dfs,
        "user_query": user_query.strip()
    }
    with st.spinner("Processing your query with LangGraph..."):
        try:
            result = graph.invoke(initial_state)

            st.session_state.state = result
            st.session_state.history = [result]
            st.session_state.followup_counter = 0
            st.session_state.figure_paths_history = []  # Reset figure history

            for figure_path in result.get("figure_paths", []):
                st.session_state.figure_paths_history.append(figure_path)
        except Exception as e:
            st.error(f"❌ Error while processing: {e}")

# --- Show Results ---
if st.session_state.state:
    st.divider()
    st.markdown(f'## User Query: {st.session_state.state.get("user_query", "No analysis found.")}')

    st.subheader("Analysis Summary")

    # --- Show Figures for Current Query Only ---
    figure_paths = st.session_state.state.get("figure_paths", [])
    if figure_paths:
        st.subheader("📊 Visualizations")
        max_per_row = 2
        num_rows = math.ceil(len(figure_paths) / max_per_row)

        for row in range(num_rows):
            cols = st.columns(max_per_row)
            for i in range(max_per_row):
                idx = row * max_per_row + i
                if idx < len(figure_paths):
                    fig_path = figure_paths[idx]
                    if os.path.exists(fig_path):
                        with cols[i]:
                            st.image(fig_path, use_container_width=True, caption=f"Figure {idx + 1}")
                    else:
                        with cols[i]:
                            st.warning(f"⚠️ Image missing: {fig_path}")

    with st.expander("📜 Generated Python Code"):
        st.code(st.session_state.state.get("generated_code", ""), language="python")

    with st.expander("🚀 Execution Output"):
        st.code(st.session_state.state.get("execution_output", ""), language="text")

    st.subheader("📚 Context Ledger")
    ledger = st.session_state.state.get("context_ledger", {})
    for df_name, info in ledger.items():
        with st.expander(f"📊 {df_name} - {info['description']}"):
            st.json(info["summary"])

    # --- Recommended Follow-ups ---
    st.subheader("🤔 Recommended Follow-up Queries")
    followups = st.session_state.state.get("recommended_analysis", [])
    for i, question in enumerate(followups):
        if st.button(f"🔁 {question}", key=f"followup_{st.session_state.followup_counter}_{i}"):

            with st.spinner("Generating follow-up..."):
                try:
                    followup_state = handle_followup(question, st.session_state.state)
                    st.session_state.state = followup_state
                    st.session_state.history.append(followup_state)
                    st.session_state.followup_counter += 1

                    # Persist new figures if available
                    for figure_path in followup_state.get("figure_paths", []):
                        st.session_state.figure_paths_history.append(figure_path)

                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error during follow-up: {e}")

    # --- Custom Follow-up ---
    st.markdown("### ✏️ Or ask your own follow-up question:")
    custom_followup = st.text_input("Custom follow-up query", key="custom_followup")

    if st.button("📌 Submit Follow-up Query", key="submit_custom_followup") and custom_followup.strip():
        with st.spinner("Processing custom follow-up..."):
            try:
                followup_state = handle_followup(custom_followup.strip(), st.session_state.state)
                st.session_state.state = followup_state
                st.session_state.history.append(followup_state)
                st.session_state.followup_counter += 1

                # Persist new figures if available
                for figure_path in followup_state.get("figure_paths", []):
                    st.session_state.figure_paths_history.append(figure_path)

                st.rerun()
            except Exception as e:
                st.error(f"❌ Error during follow-up: {e}")
    
    st.sidebar.subheader("Manage DataFrames")
    # Temp storage for file and metadata
    if "pending_sidebar_upload" not in st.session_state:
        st.session_state.pending_sidebar_upload = {}

    uploaded_files_sidebar = st.sidebar.file_uploader(
        "Upload CSV/XLSX files", type=["csv", "xlsx", "xls"],
        accept_multiple_files=False, key="sidebar_uploader"
    )

    # When a file is uploaded, store in pending state
    if uploaded_files_sidebar:
        file = uploaded_files_sidebar
        ext = file.name.split(".")[-1].lower()
        try:
            if ext == "csv":
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)

            st.session_state.pending_sidebar_upload = {
                "file": file,
                "data": df
            }

        except Exception as e:
            st.sidebar.error(f"❌ Failed to read {file.name}: {e}")
            st.session_state.pending_sidebar_upload = {}

    # If a file is pending, ask for metadata and confirm
    if st.session_state.get("pending_sidebar_upload"):
        file = st.session_state.pending_sidebar_upload["file"]
        df = st.session_state.pending_sidebar_upload["data"]

        new_df_name = st.sidebar.text_input("📛 DataFrame Name", value=file.name.split(".")[0])
        description = st.sidebar.text_input("📝 Description", f"User uploaded file: {file.name}")

        if st.sidebar.button("✅ Confirm Upload"):
            # Prevent duplicate DataFrame names
            if new_df_name in [x['name'] for x in st.session_state.dfs]:
                st.sidebar.warning("⚠️ DataFrame name already exists!")
            else:
                st.session_state.dfs.append({
                    "name": new_df_name,
                    "data": df,
                    "description": description
                })

                # Also update the context ledger if available
                if st.session_state.state:
                    st.session_state.state.setdefault("context_ledger", {})[new_df_name] = {
                        "description": description,
                        "summary": data_description(df)
                    }

                st.sidebar.success(f"✅ Loaded: {file.name} as {new_df_name}")
                st.session_state.pending_sidebar_upload = {}  # Clear pending state
                st.rerun()


    # Remove DataFrame
    remove_df_name = st.sidebar.selectbox("Remove DataFrame", [x['name'] for x in st.session_state.dfs])
    if st.sidebar.button("Remove"):

        for item in st.session_state.dfs:
            if item["name"] == remove_df_name:
                st.session_state.dfs.remove(item)
                break

        if remove_df_name in ledger:
            del ledger[remove_df_name]

        st.rerun()
        st.sidebar.warning(f"'{remove_df_name}' removed.")

    st.subheader("🔍 Preview a DataFrame")

    if st.session_state.dfs:
        df_names = [df["name"] for df in st.session_state.dfs]
        selected_df_name = st.selectbox("Select a DataFrame to preview", df_names)

        num_rows = st.number_input("Number of rows to show", min_value=1, max_value=1000, value=10, step=1)

        # Get the actual DataFrame
        selected_df_data = next((df["data"] for df in st.session_state.dfs if df["name"] == selected_df_name), None)

        if selected_df_data is not None:
            st.dataframe(selected_df_data.head(num_rows), use_container_width=True)
        else:
            st.warning("⚠️ Could not find the selected DataFrame.")
    else:
        st.info("Upload a file to start previewing data.")



    # --- DataFrame Manipulation ---
    st.subheader("✍️ Manipulate DataFrames")

    if st.session_state.state and "context_ledger" in st.session_state.state:
        df_names = list(st.session_state.state["context_ledger"].keys())
        
        selected_df_name = st.selectbox("📊 Select a DataFrame to manipulate", df_names)
        mode = st.radio("Choose manipulation mode", ["Python Mode", "LLM Mode"], horizontal=True)

        if selected_df_name:
            # Find the actual DataFrame object
            target_df_obj = next((x for x in st.session_state.dfs if x["name"] == selected_df_name), None)

            if target_df_obj:
                if mode == "Python Mode":
                    code = st.text_area("✍️ Write Python code to manipulate the DataFrame", height=150,
                                        placeholder=f"Example: {selected_df_name} = {selected_df_name}[{selected_df_name}[\"spend_amount\"] >= 500]")

                    if st.button("▶️ Execute Python Code"):
                        try:
                            local_vars = {selected_df_name: target_df_obj["data"]}
                            exec(code, {}, local_vars)
                            modified_df = local_vars[selected_df_name]

                            # Update DataFrame
                            target_df_obj["data"] = modified_df

                            # Update context ledger summary
                            st.session_state.state["context_ledger"][selected_df_name]["summary"] = data_description(modified_df)

                            st.success("✅ DataFrame updated successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error executing code: {e}")

                elif mode == "LLM Mode":
                    llm_instruction = st.text_input("🧠 Describe what you want to do",
                                                    placeholder="Example: Keep only spend amount greater than 500")

                    if st.button("✨ Generate and Execute Code"):
                        try:
                            from ai_core import textgen_agent  # Assuming you already have this function
                            
                            # Generate code
                            prompt = f"Write Python code to modify a pandas DataFrame named '{selected_df_name}' as per the instruction: {llm_instruction}"
                            generated_code = textgen_agent(prompt)

                            st.code(generated_code.strip(), language="python")

                            local_vars = {selected_df_name: target_df_obj["data"]}
                            exec(generated_code, {}, local_vars)
                            modified_df = local_vars[selected_df_name]

                            # Update DataFrame
                            target_df_obj["data"] = modified_df

                            # Update context ledger summary
                            st.session_state.state["context_ledger"][selected_df_name]["summary"] = data_description(modified_df)

                            st.success("✅ LLM-generated code executed successfully.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error in LLM Mode: {e}")

    st.markdown("### 🔄 Re-run Last Generated Code on Updated Data")

    if st.button("🔁 Rerun Code on Latest Data"):
        with st.spinner("Re-running code on current data..."):
            try:
                code = st.session_state.state.get("generated_code", "")
                if not code:
                    st.warning("No code available to re-run.")
                else:
                    # Prepare context for repl
                    repl_context = {
                        df["name"]: df["data"] for df in st.session_state.dfs
                    }

                    result = custom_repl(code, repl_context)

                    # Update state
                    st.session_state.state["execution_output"] = result["stdout"]
                    st.session_state.state["figure_paths"] =  result.get("figure_paths", ["Dummy.png"])
                    #st.session_state.state["figure_paths_history"].extend(result.get("figure_paths", ["Dummy.png"]))

                    # Rerender
                    st.success("Code re-executed with latest data.")
                    st.rerun()

            except Exception as e:
                st.error(f"❌ Error while re-running: {e}")
