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
    page_title="AI SQL Data Analyst",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "query_history" not in st.session_state:
    st.session_state.query_history = []

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(
        135deg,
        #667eea 0%,
        #764ba2 25%,
        #6B8DD6 50%,
        #8E37D7 75%,
        #4A00E0 100%
    );
    background-attachment: fixed;
    color: white;
}

/* Title */
.main-title {
    font-size: 52px;
    font-weight: 800;
    text-align: center;
    color: white;
    margin-top: 10px;
    text-shadow: 2px 2px 15px rgba(0,0,0,0.4);
}

/* Subtitle */
.sub-title {
    text-align: center;
    color: #f1f5f9;
    font-size: 20px;
    margin-bottom: 30px;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.15);
    padding: 20px;
    border-radius: 24px;
    backdrop-filter: blur(14px);
    box-shadow: 0px 8px 25px rgba(0,0,0,0.25);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        to right,
        #ff6a00,
        #ee0979
    );
    color: white;
    border-radius: 14px;
    border: none;
    padding: 12px 28px;
    font-size: 15px;
    font-weight: bold;
}

/* Headers */
h1, h2, h3 {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.markdown(
    '<div class="main-title">🤖 AI SQL Data Analyst Platform</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Multi CSV Upload • AI SQL Queries • JOIN Operations • Smart Visualizations</div>',
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("⚙️ Settings")

groq_api_key = st.sidebar.text_input(
    "Enter Groq API Key",
    type="password"
)

model_option = st.sidebar.selectbox(
    "Select AI Model",
    [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]
)

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
        txt="AI SQL Data Analyst Report",
        ln=True
    )

    pdf.multi_cell(
        0,
        10,
        summary_text
    )

    pdf.output("report.pdf")

# =========================================================
# MAIN APPLICATION
# =========================================================
if uploaded_files:

    # =====================================================
    # DATABASE CONNECTION
    # =====================================================
    conn = sqlite3.connect("data.db")

    all_tables = {}

    # =====================================================
    # LOAD CSV FILES
    # =====================================================
    for uploaded_file in uploaded_files:

        try:

            df_temp = pd.read_csv(uploaded_file)

            # Clean table name
            table_name = (
                uploaded_file.name
                .replace(".csv", "")
                .replace(" ", "_")
                .replace("-", "_")
                .lower()
            )

            all_tables[table_name] = df_temp

            # Store in SQLite
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

    # =====================================================
    # COMBINED DATAFRAME
    # =====================================================
    combined_df = pd.concat(
        all_tables.values(),
        ignore_index=True,
        sort=False
    )

    numeric_cols = combined_df.select_dtypes(
        include=['number']
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
    # DASHBOARD TAB
    # =====================================================
    with tab1:

        st.markdown("## 📌 Multi Dataset Insights")

        total_rows = combined_df.shape[0]
        total_columns = combined_df.shape[1]
        missing_values = int(combined_df.isnull().sum().sum())
        duplicate_rows = int(combined_df.duplicated().sum())

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("📄 Total Rows", total_rows)

        with m2:
            st.metric("📊 Total Columns", total_columns)

        with m3:
            st.metric("❌ Missing", missing_values)

        with m4:
            st.metric("🔁 Duplicates", duplicate_rows)

        # =================================================
        # TABLE DETAILS
        # =================================================
        st.markdown("## 📂 Uploaded SQL Tables")

        for table_name, table_df in all_tables.items():

            st.success(
                f"""
📌 Table Name: {table_name}

Columns:
{', '.join(table_df.columns)}

Rows:
{table_df.shape[0]}
"""
            )

        # =================================================
        # PREVIEW
        # =================================================
        st.markdown("## 📊 Combined Dataset Preview")

        st.dataframe(
            combined_df.head(20),
            use_container_width=True
        )

        # =================================================
        # SCHEMA
        # =================================================
        st.markdown("## 🧠 Database Schema")

        schema_data = []

        for table_name, table_df in all_tables.items():

            for col in table_df.columns:

                schema_data.append({
                    "Table": table_name,
                    "Column": col,
                    "Data Type": str(table_df[col].dtype)
                })

        schema_df = pd.DataFrame(schema_data)

        st.dataframe(
            schema_df,
            use_container_width=True
        )

    # =====================================================
    # AI CHAT TAB
    # =====================================================
    with tab2:

        st.markdown("## 💬 AI SQL Chat")

        # =================================================
        # TABLE INFO
        # =================================================
        st.markdown("### 📂 Available Tables")

        for table_name, table_df in all_tables.items():

            st.info(
                f"""
📌 {table_name}

Columns:
{', '.join(table_df.columns)}
"""
            )

        # =================================================
        # SUGGESTIONS
        # =================================================
        st.markdown("### 🤖 Suggested Questions")

        suggestions = [
            "Join customers and orders tables",
            "Find matching IDs",
            "Compare sales between datasets",
            "Show total revenue",
            "Find duplicate values",
            "Display highest sales"
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
            "Ask SQL questions across multiple datasets..."
        )

        # =================================================
        # AUTO QUESTION
        # =================================================
        if st.session_state.get("auto_question"):

            question = st.session_state[
                "auto_question"
            ]

            st.session_state[
                "auto_question"
            ] = None

        # =================================================
        # AI PROCESSING
        # =================================================
        if question and groq_api_key:

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            with st.chat_message("user"):
                st.markdown(question)

            try:

                llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name=model_option
                )

                # =============================================
                # TABLE INFO
                # =============================================
                table_info = "\n\n".join([

                    f"""
Table Name: {table}

Columns:
{', '.join(all_tables[table].columns)}
"""

                    for table in all_tables

                ])

                # =============================================
                # PROMPT
                # =============================================
                prompt = f"""
You are an expert SQL analyst.

Database Type: SQLite

Available Tables:

{table_info}

User Question:
{question}

Instructions:
1. Understand all uploaded tables
2. Use JOIN when needed
3. Generate valid SQLite query
4. Use only available table names
5. Do not use markdown code blocks
6. Return only executable SQL
7. Then provide final answer

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

                # =============================================
                # SPLIT RESPONSE
                # =============================================
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

                # =============================================
                # CLEAN SQL QUERY
                # =============================================
                sql_query = (
                    sql_query
                    .replace("```sql", "")
                    .replace("```", "")
                    .strip()
                )

                # =============================================
                # AI RESPONSE
                # =============================================
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

                st.session_state.query_history.append({
                    "question": question,
                    "sql": sql_query
                })

                # =============================================
                # DISPLAY RESPONSE
                # =============================================
                with st.chat_message("assistant"):

                    st.markdown(ai_response)

                    try:

                        # =====================================
                        # CLEAN AGAIN BEFORE EXECUTION
                        # =====================================
                        sql_query = (
                            sql_query
                            .replace("```sql", "")
                            .replace("```", "")
                            .strip()
                        )

                        # =====================================
                        # EXECUTE SELECT QUERY
                        # =====================================
                        if sql_query.lower().startswith("select"):

                            result_df = pd.read_sql_query(
                                sql_query,
                                conn
                            )

                            st.success(
                                "✅ Query Executed Successfully"
                            )

                            st.info(
                                f"""
📊 Total Rows Returned:
{result_df.shape[0]}
"""
                            )

                            # =================================
                            # DISPLAY RESULTS
                            # =================================
                            st.markdown(
                                "## 📋 Query Results"
                            )

                            st.dataframe(
                                result_df,
                                use_container_width=True
                            )

                            # =================================
                            # DOWNLOAD RESULTS
                            # =================================
                            csv_result = result_df.to_csv(
                                index=False
                            ).encode("utf-8")

                            st.download_button(
                                label="⬇ Download Query Results",
                                data=csv_result,
                                file_name="query_results.csv",
                                mime="text/csv"
                            )

                            # =================================
                            # AUTO VISUALIZATION
                            # =================================
                            numeric_result_cols = result_df.select_dtypes(
                                include=["number"]
                            ).columns

                            if len(numeric_result_cols) > 0:

                                st.markdown(
                                    "## 📈 Result Visualization"
                                )

                                chart_type = st.selectbox(
                                    "Select Chart Type",
                                    [
                                        "Bar",
                                        "Line",
                                        "Scatter",
                                        "Pie",
                                        "Histogram"
                                    ],
                                    key=f"chart_{len(st.session_state.query_history)}"
                                )

                                x_col = st.selectbox(
                                    "Select X-axis",
                                    result_df.columns,
                                    key=f"x_{len(st.session_state.query_history)}"
                                )

                                y_col = st.selectbox(
                                    "Select Y-axis",
                                    numeric_result_cols,
                                    key=f"y_{len(st.session_state.query_history)}"
                                )

                                # =============================
                                # CHARTS
                                # =============================
                                if chart_type == "Bar":

                                    fig = px.bar(
                                        result_df,
                                        x=x_col,
                                        y=y_col
                                    )

                                elif chart_type == "Line":

                                    fig = px.line(
                                        result_df,
                                        x=x_col,
                                        y=y_col
                                    )

                                elif chart_type == "Scatter":

                                    fig = px.scatter(
                                        result_df,
                                        x=x_col,
                                        y=y_col
                                    )

                                elif chart_type == "Pie":

                                    fig = px.pie(
                                        result_df,
                                        names=x_col,
                                        values=y_col
                                    )

                                else:

                                    fig = px.histogram(
                                        result_df,
                                        x=y_col
                                    )

                                st.plotly_chart(
                                    fig,
                                    use_container_width=True
                                )

                        # =====================================
                        # NON SELECT QUERY
                        # =====================================
                        else:

                            cursor = conn.cursor()

                            cursor.execute(sql_query)

                            conn.commit()

                            st.success(
                                "✅ Query Executed Successfully"
                            )

                    except Exception as e:

                        st.error(
                            f"❌ SQL Execution Error: {e}"
                        )

            except Exception as e:

                st.error(str(e))

        elif question and not groq_api_key:

            st.warning(
                "⚠️ Please enter Groq API Key"
            )

        # =================================================
        # QUERY HISTORY
        # =================================================
        st.markdown("## 🕘 Query History")

        for item in st.session_state.query_history:

            st.markdown(
                f"### ❓ {item['question']}"
            )

            st.code(
                item['sql'],
                language='sql'
            )

    # =====================================================
    # VISUALIZATION TAB
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
                    "Line",
                    "Bar",
                    "Scatter",
                    "Histogram",
                    "Pie"
                ]
            )

            if st.button(
                "Generate Visualization"
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

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

    # =====================================================
    # REPORT TAB
    # =====================================================
    with tab4:

        st.markdown("## 📄 Download Reports")

        if st.button(
            "Generate PDF Report"
        ):

            report_text = f"""
AI SQL Data Analyst Report

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
                    file_name="AI_SQL_Report.pdf",
                    mime="application/pdf"
                )

        # =================================================
        # DOWNLOAD CSV
        # =================================================
        csv = combined_df.to_csv(
            index=False
        ).encode('utf-8')

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

    st.info(
        "👆 Upload multiple CSV files to start AI SQL analysis"
    )