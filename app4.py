import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from fpdf import FPDF
from langchain_groq import ChatGroq

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="SQLMIND — Data Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_history" not in st.session_state:
    st.session_state.query_history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# =========================================================
# THEME TOGGLE
# =========================================================
if st.sidebar.button("🌙 Toggle Theme"):

    st.session_state.dark_mode = (
        not st.session_state.dark_mode
    )

    st.rerun()

# =========================================================
# THEME COLORS
# =========================================================
if st.session_state.dark_mode:

    bg_color = "#0e1117"
    card_color = "#161b22"
    text_color = "#ffffff"
    border_color = "#30363d"
    sidebar_color = "#161b22"
    secondary_text = "#c9d1d9"

else:

    bg_color = "#f5f7fb"
    card_color = "#ffffff"
    text_color = "#111111"
    border_color = "#d0d7de"
    sidebar_color = "#ffffff"
    secondary_text = "#555555"

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown(f"""
<style>

/* =====================================================
MAIN APP
===================================================== */
.stApp {{
    background: {bg_color};
    color: {text_color};
    font-family: 'Segoe UI', sans-serif;
}}

/* =====================================================
HIDE STREAMLIT DEFAULTS
===================================================== */
#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

/* =====================================================
SIDEBAR
===================================================== */
section[data-testid="stSidebar"] {{
    background: {sidebar_color};
    border-right: 1px solid {border_color};
}}

/* =====================================================
TITLE
===================================================== */
.main-title {{
    font-size: 62px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(
        90deg,
        #4f46e5,
        #9333ea
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.sub-title {{
    text-align: center;
    font-size: 18px;
    color: {secondary_text};
    margin-top: 10px;
}}

/* =====================================================
GLASS CARD
===================================================== */
.glass {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0px 4px 18px rgba(0,0,0,0.08);
}}

/* =====================================================
METRICS
===================================================== */
[data-testid="metric-container"] {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
}}

/* =====================================================
BUTTONS
===================================================== */
.stButton > button {{
    width: 100%;
    background: linear-gradient(
        90deg,
        #4f46e5,
        #9333ea
    );
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
}}

.stButton > button:hover {{
    opacity: 0.92;
}}

/* =====================================================
DOWNLOAD BUTTON
===================================================== */
.stDownloadButton > button {{
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(
        90deg,
        #0ea5e9,
        #14b8a6
    );
    color: white;
    padding: 12px;
    font-weight: 600;
}}

/* =====================================================
INPUTS
===================================================== */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {{
    border-radius: 12px !important;
}}

/* =====================================================
DATAFRAME
===================================================== */
[data-testid="stDataFrame"] {{
    border-radius: 18px;
    overflow: hidden;
}}

/* =====================================================
CHAT
===================================================== */
.stChatMessage {{
    background: {card_color};
    border: 1px solid {border_color};
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 12px;
}}

/* =====================================================
TABS
===================================================== */
.stTabs [data-baseweb="tab"] {{
    background: {card_color};
    border-radius: 12px;
    padding: 12px 20px;
    margin-right: 8px;
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(
        90deg,
        #4f46e5,
        #9333ea
    ) !important;

    color: white !important;
}}

/* =====================================================
HEADINGS
===================================================== */
h1, h2, h3, h4 {{
    color: {text_color} !important;
}}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HERO SECTION
# =========================================================
st.markdown("""
<div class="glass">
<div class="main-title">SQLMIND</div>
<div class="sub-title">AI Powered SQL Intelligence Platform</div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.markdown("## ⚙️ Configuration")

groq_api_key = st.sidebar.text_input(
    "Groq API Key",
    type="password"
)

model_option = st.sidebar.selectbox(
    "Select AI Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("""
### 🚀 Features

✅ Multi CSV Upload  
✅ AI SQL Queries  
✅ Smart Charts  
✅ Query History  
✅ PDF Reports  
""")

# =========================================================
# FILE UPLOAD
# =========================================================
uploaded_files = st.file_uploader(
    "📂 Upload CSV Files",
    type=["csv"],
    accept_multiple_files=True
)

# =========================================================
# PDF FUNCTION
# =========================================================
def generate_pdf(summary_text):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Arial", size=12)

    pdf.cell(
        200,
        10,
        txt="SQLMIND Report",
        ln=True
    )

    pdf.multi_cell(
        0,
        10,
        summary_text
    )

    pdf.output("report.pdf")

# =========================================================
# MAIN APP
# =========================================================
if uploaded_files:

    conn = sqlite3.connect("data.db")

    all_tables = {}

    # =====================================================
    # LOAD CSV FILES
    # =====================================================
    for uploaded_file in uploaded_files:

        try:

            df_temp = pd.read_csv(uploaded_file)

            table_name = (
                uploaded_file.name
                .replace(".csv", "")
                .replace(" ", "_")
                .replace("-", "_")
                .lower()
            )

            all_tables[table_name] = df_temp

            df_temp.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False
            )

        except Exception:

            st.error(
                f"❌ Could not read {uploaded_file.name}"
            )

    combined_df = pd.concat(
        all_tables.values(),
        ignore_index=True,
        sort=False
    )

    numeric_cols = combined_df.select_dtypes(
        include=["number"]
    ).columns

    # =====================================================
    # TABS
    # =====================================================
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "💬 AI Chat",
        "📈 Visualizations",
        "📄 Reports"
    ])

    # =====================================================
    # DASHBOARD
    # =====================================================
    with tab1:

        st.markdown("## 📊 Dataset Overview")

        total_rows = combined_df.shape[0]
        total_columns = combined_df.shape[1]
        missing_values = int(
            combined_df.isnull().sum().sum()
        )
        duplicate_rows = int(
            combined_df.duplicated().sum()
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Rows", total_rows)

        with m2:
            st.metric("Columns", total_columns)

        with m3:
            st.metric("Missing", missing_values)

        with m4:
            st.metric("Duplicates", duplicate_rows)

        st.markdown("## 📂 Uploaded Tables")

        for table_name, table_df in all_tables.items():

            st.markdown(f"""
<div class="glass"><h3>📌 {table_name}</h3><b>Columns:</b><br>{', '.join(table_df.columns)}<br><br><b>Total Rows:</b> {table_df.shape[0]}</div>
""", unsafe_allow_html=True)

        st.markdown("## 📋 Dataset Preview")

        st.dataframe(
            combined_df.head(20),
            use_container_width=True
        )

    # =====================================================
    # AI CHAT
    # =====================================================
    with tab2:

        st.markdown("## 💬 AI SQL Assistant")

        suggestions = [
            "Show total revenue",
            "Find duplicate rows",
            "Display highest sales",
            "Join tables",
            "Compare datasets",
            "Find missing values"
        ]

        cols = st.columns(3)

        for i, suggestion in enumerate(suggestions):

            with cols[i % 3]:

                if st.button(
                    suggestion,
                    key=f"suggestion_{i}"
                ):

                    st.session_state[
                        "auto_question"
                    ] = suggestion

        # =================================================
        # CHAT HISTORY
        # =================================================
        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):

                st.markdown(msg["content"])

        question = st.chat_input(
            "Ask questions about your data..."
        )

        if st.session_state.get("auto_question"):

            question = st.session_state[
                "auto_question"
            ]

            st.session_state[
                "auto_question"
            ] = None

        # =================================================
        # AI QUERY
        # =================================================
        if question and groq_api_key:

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            with st.chat_message("user"):

                st.markdown(question)

            try:

                with st.spinner(
                    "🤖 AI is analyzing..."
                ):

                    llm = ChatGroq(
                        groq_api_key=groq_api_key,
                        model_name=model_option
                    )

                    table_info = "\n\n".join([

                        f"""
Table Name: {table}

Columns:
{', '.join(all_tables[table].columns)}
"""

                        for table in all_tables

                    ])

                    prompt = f"""
You are an expert SQL analyst.

Database Type: SQLite

Available Tables:

{table_info}

User Question:
{question}

Instructions:
1. Generate valid SQLite query
2. Use JOIN when needed
3. Return executable SQL
4. Then provide answer

STRICT FORMAT:

SQL:
SELECT ...

Answer:
<answer>
"""

                    response = llm.invoke(
                        prompt
                    ).content

                sql_query = ""
                final_answer = response

                if (
                    "SQL:" in response
                    and
                    "Answer:" in response
                ):

                    sql_query = response.split(
                        "SQL:"
                    )[1].split(
                        "Answer:"
                    )[0].strip()

                    final_answer = response.split(
                        "Answer:"
                    )[1].strip()

                sql_query = (
                    sql_query
                    .replace("```sql", "")
                    .replace("```", "")
                    .strip()
                )

                ai_response = (
                    f"### 🧠 Generated SQL Query\n\n"
                    f"```sql\n{sql_query}\n```\n\n"
                    f"### ✅ AI Answer\n\n"
                    f"{final_answer}"
                )

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })

                with st.chat_message("assistant"):

                    st.markdown(ai_response)

                    try:

                        result_df = pd.read_sql_query(
                            sql_query,
                            conn
                        )

                        st.success(
                            "✅ Query Executed Successfully"
                        )

                        st.dataframe(
                            result_df,
                            use_container_width=True
                        )

                        csv_result = result_df.to_csv(
                            index=False
                        ).encode("utf-8")

                        st.download_button(
                            label="⬇ Download Results",
                            data=csv_result,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )

                    except Exception as e:

                        st.error(
                            f"❌ SQL Error: {e}"
                        )

            except Exception as e:

                st.error(str(e))

        elif question and not groq_api_key:

            st.warning(
                "⚠️ Please enter Groq API Key"
            )

    # =====================================================
    # VISUALIZATION
    # =====================================================
    with tab3:

        st.markdown("## 📈 Smart Visualizations")

        if len(numeric_cols) > 0:

            x_axis = st.selectbox(
                "Select X-axis",
                combined_df.columns
            )

            y_axis = st.selectbox(
                "Select Y-axis",
                numeric_cols
            )

            chart_type = st.selectbox(
                "Chart Type",
                [
                    "Bar",
                    "Line",
                    "Scatter",
                    "Histogram",
                    "Pie"
                ]
            )

            if st.button(
                "🚀 Generate Visualization"
            ):

                if chart_type == "Line":

                    fig = px.line(
                        combined_df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Bar":

                    fig = px.bar(
                        combined_df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Scatter":

                    fig = px.scatter(
                        combined_df,
                        x=x_axis,
                        y=y_axis
                    )

                elif chart_type == "Pie":

                    fig = px.pie(
                        combined_df,
                        names=x_axis,
                        values=y_axis
                    )

                else:

                    fig = px.histogram(
                        combined_df,
                        x=y_axis
                    )

                fig.update_layout(
                    template="plotly_dark"
                    if st.session_state.dark_mode
                    else "plotly_white"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

    # =====================================================
    # REPORTS
    # =====================================================
    with tab4:

        st.markdown("## 📄 Generate Reports")

        if st.button(
            "📄 Generate PDF Report"
        ):

            report_text = f"""
SQLMIND Report

Total Tables:
{len(all_tables)}

Tables:
{', '.join(all_tables.keys())}

Total Rows:
{combined_df.shape[0]}

Total Columns:
{combined_df.shape[1]}
"""

            generate_pdf(report_text)

            with open(
                "report.pdf",
                "rb"
            ) as f:

                st.download_button(
                    label="⬇ Download PDF",
                    data=f,
                    file_name="SQLMIND_Report.pdf",
                    mime="application/pdf"
                )

        csv = combined_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇ Download Combined CSV",
            csv,
            "combined_data.csv",
            "text/csv"
        )

# =========================================================
# EMPTY STATE
# =========================================================
else:

    st.markdown("""
<div class="glass" style="text-align:center;">

<h1>📂 Upload CSV Files</h1>

<p style="font-size:18px;">
Start analyzing datasets with AI-powered SQL queries,
interactive dashboards, smart charts, and reports.
</p>

</div>
""", unsafe_allow_html=True)