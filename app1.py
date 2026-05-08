import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

from langchain_groq import ChatGroq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI SQL Data Analyst",
    page_icon="🤖",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}

/* Main Title */
.main-title {
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    color: white;
    margin-top: 10px;
}

.sub-title {
    text-align: center;
    color: #cbd5e1;
    font-size: 20px;
    margin-bottom: 30px;
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 15px;
    border-radius: 18px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(to right, #3b82f6, #8b5cf6);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 25px;
    font-size: 16px;
    font-weight: bold;
}

/* Input Boxes */
.stTextInput > div > div > input {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    '<div class="main-title">🤖 AI SQL Data Analyst Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Upload CSV → AI SQL Queries → Insights → Visualizations</div>',
    unsafe_allow_html=True
)

# ---------------- SIDEBAR ----------------
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
    ],
    key="model_select"
)

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📂 Upload CSV File",
    type=["csv"]
)

# ---------------- MAIN APP ----------------
if uploaded_file:

    # ---------------- LOAD DATA ----------------
    try:
        df = pd.read_csv(uploaded_file)

    except Exception:
        st.error("❌ Could not read CSV file")
        st.stop()

    # ---------------- SQLITE ----------------
    conn = sqlite3.connect("data.db")

    df.to_sql(
        "data_table",
        conn,
        if_exists="replace",
        index=False
    )

    # ---------------- DATASET INSIGHTS ----------------
    st.markdown("## 📌 Dataset Insights")

    total_rows = df.shape[0]
    total_columns = df.shape[1]
    missing_values = int(df.isnull().sum().sum())
    duplicate_rows = int(df.duplicated().sum())

    m1, m2, m3, m4 = st.columns(4)

    with m1:
        st.metric("📄 Rows", total_rows)

    with m2:
        st.metric("📊 Columns", total_columns)

    with m3:
        st.metric("❌ Missing Values", missing_values)

    with m4:
        st.metric("🔁 Duplicate Rows", duplicate_rows)

    # ---------------- DATA PREVIEW ----------------
    left, right = st.columns(2)

    with left:

        st.markdown("## 📊 Data Preview")

        st.dataframe(
            df.head(20),
            use_container_width=True
        )

    with right:

        st.markdown("## 🧠 Schema")

        schema_df = pd.DataFrame({
            "Column": df.columns,
            "Data Type": df.dtypes.astype(str)
        })

        st.dataframe(
            schema_df,
            use_container_width=True
        )

    # ---------------- DATA QUALITY ----------------
    st.markdown("## 🔍 Data Quality Analysis")

    q1, q2 = st.columns(2)

    with q1:

        missing_df = pd.DataFrame({
            "Column": df.columns,
            "Missing Values": df.isnull().sum().values
        })

        st.markdown("### ⚠️ Missing Values")

        st.dataframe(
            missing_df,
            use_container_width=True
        )

    with q2:

        unique_df = pd.DataFrame({
            "Column": df.columns,
            "Unique Values": [
                df[col].nunique() for col in df.columns
            ]
        })

        st.markdown("### 📌 Unique Values")

        st.dataframe(
            unique_df,
            use_container_width=True
        )

    # ---------------- STATISTICS ----------------
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:

        st.markdown("## 📈 Statistical Summary")

        st.dataframe(
            df.describe(),
            use_container_width=True
        )

    # ---------------- CORRELATION HEATMAP ----------------
    if len(numeric_cols) >= 2:

        st.markdown("## 🔥 Correlation Heatmap")

        try:

            corr_matrix = df[numeric_cols].corr()

            # Fill NaN values
            corr_matrix = corr_matrix.fillna(0)

            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception:

            st.warning(
                "⚠️ Could not generate heatmap"
            )

    # ---------------- AI INSIGHTS ----------------
    st.markdown("## 🤖 AI Generated Insights")

    if len(numeric_cols) > 0:

        for col in numeric_cols:

            avg_val = round(df[col].mean(), 2)
            max_val = df[col].max()
            min_val = df[col].min()

            st.info(
                f"📌 {col} → Average: {avg_val} | Maximum: {max_val} | Minimum: {min_val}"
            )

    # ---------------- AI QUESTION SECTION ----------------
    st.markdown("## 💬 Ask Questions About Your Data")

    question = st.text_input(
        "Ask using natural language",
        key="question_box"
    )

    if question and groq_api_key:

        try:

            # ---------------- LLM ----------------
            llm = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=model_option
            )

            # ---------------- PROMPT ----------------
            prompt = f"""
You are an expert SQL analyst.

Database: SQLite
Table Name: data_table

Columns:
{', '.join(df.columns)}

User Question:
{question}

Instructions:
1. Generate valid SQLite query
2. Then give answer

STRICT FORMAT:

SQL:
<query>

Answer:
<answer>
"""

            # ---------------- AI RESPONSE ----------------
            response = llm.invoke(prompt).content

            sql_query = ""
            final_answer = ""

            if "SQL:" in response and "Answer:" in response:

                sql_query = response.split(
                    "SQL:"
                )[1].split(
                    "Answer:"
                )[0].strip()

                final_answer = response.split(
                    "Answer:"
                )[1].strip()

            else:
                final_answer = response

            # ---------------- SQL DISPLAY ----------------
            st.markdown("## 🧠 Generated SQL Query")

            st.code(
                sql_query,
                language="sql"
            )

            # ---------------- ANSWER ----------------
            st.markdown("## ✅ AI Answer")

            st.success(final_answer)

            # ---------------- EXECUTE QUERY ----------------
            try:

                if sql_query.lower().startswith("select"):

                    result_df = pd.read_sql_query(
                        sql_query,
                        conn
                    )

                    st.markdown("## 📄 Query Result")

                    st.dataframe(
                        result_df,
                        use_container_width=True
                    )

                    # ---------------- AUTO VISUALIZATION ----------------
                    if not result_df.empty:

                        result_numeric = result_df.select_dtypes(
                            include=['number']
                        ).columns

                        result_object = result_df.select_dtypes(
                            include=['object']
                        ).columns

                        st.markdown("## 📊 Auto Visualization")

                        # BAR CHART
                        if len(result_numeric) == 1 and len(result_object) == 1:

                            fig = px.bar(
                                result_df,
                                x=result_object[0],
                                y=result_numeric[0],
                                title=f"{result_object[0]} vs {result_numeric[0]}"
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True
                            )

                        # SCATTER CHART
                        elif len(result_numeric) >= 2:

                            fig = px.scatter(
                                result_df,
                                x=result_numeric[0],
                                y=result_numeric[1],
                                title=f"{result_numeric[0]} vs {result_numeric[1]}"
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True
                            )

            except Exception:

                st.warning(
                    "⚠️ SQL query execution failed"
                )

        except Exception as e:

            st.error(
                f"❌ Error: {str(e)}"
            )

    elif question and not groq_api_key:

        st.warning(
            "⚠️ Please enter Groq API Key"
        )

    # ---------------- CUSTOM VISUALIZATION ----------------
    st.markdown("## 📈 Custom Visualization")

    if len(numeric_cols) > 0:

        v1, v2, v3 = st.columns(3)

        with v1:

            x_axis = st.selectbox(
                "Select X-axis",
                df.columns,
                key="x_axis"
            )

        with v2:

            y_axis = st.selectbox(
                "Select Y-axis",
                numeric_cols,
                key="y_axis"
            )

        with v3:

            chart_type = st.selectbox(
                "Chart Type",
                ["Line", "Bar", "Scatter", "Histogram"],
                key="chart_type"
            )

        if st.button(
            "Generate Visualization",
            key="generate_chart"
        ):

            if chart_type == "Line":

                fig = px.line(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            elif chart_type == "Bar":

                fig = px.bar(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            elif chart_type == "Scatter":

                fig = px.scatter(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            else:

                fig = px.histogram(
                    df,
                    x=y_axis
                )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

else:

    st.info("👆 Upload a CSV file to start AI analysis")