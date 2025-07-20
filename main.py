import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import io


# ======= Ollama LLM Call Function =======
def ask_llm(prompt, model="llama3"):
    """Call Ollama local LLM API"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    return response.json()["response"]


# ======= Streamlit UI =======
st.title("📊 Local LLM (Ollama) Smart Sales Data Analyzer")
st.write(
    "Upload a **CSV or Excel file**. The local LLM will auto-detect column meanings → generate charts → provide business insights.")

uploaded_file = st.file_uploader("📂 Upload CSV or Excel", type=["csv", "xlsx", "xls"])

if uploaded_file:
    # Detect file type and read accordingly
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type == "csv":
        df = pd.read_csv(uploaded_file)
    else:  # Default Excel
        df = pd.read_excel(uploaded_file)

    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # ===== 1. Ask LLM to understand column meanings =====
    sample_data = df.head(5).to_dict(orient="records")
    column_prompt = (
        f"Here are the first 5 rows of a sales record:\n{sample_data}\n\n"
        f"Please infer the meaning of each column "
        f"(e.g. Date, Product Name, Quantity Sold, Sales Amount, Region...) "
        f"and return as JSON like {{'column_name': 'meaning'}}."
    )
    column_meanings = ask_llm(column_prompt)
    st.subheader("🧠 LLM-Inferred Column Meanings")
    st.code(column_meanings, language="json")

    # ===== 2. Auto-generate statistical charts =====
    st.subheader("📊 Auto-generated Charts")

    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        for col in numeric_cols:
            fig = px.histogram(df, x=col, nbins=20, title=f"{col} Distribution")
            st.plotly_chart(fig)

    # Try to detect potential date columns
    date_cols = [c for c in df.columns if "date" in c.lower() or "day" in c.lower()]
    if date_cols:
        date_col = date_cols[0]
        try:
            df[date_col] = pd.to_datetime(df[date_col])
            if numeric_cols:
                sales_col = numeric_cols[0]  # assume first numeric col is sales
                df_trend = df.groupby(date_col)[sales_col].sum().reset_index()
                fig = px.line(df_trend, x=date_col, y=sales_col, title=f"{sales_col} Over Time")
                st.plotly_chart(fig)
        except:
            st.warning("⚠️ Could not parse date column. Skipping time-series chart.")

    # ===== 3. AI Business Analysis =====
    st.subheader("💡 AI Business Insights & Suggestions")
    summary_stats = df.describe().to_dict()
    analysis_prompt = f"""
    Here is the statistical summary of the sales data:
    {summary_stats}

    Based on this data, please answer:
    1. Which products or months performed poorly?
    2. Are there any potential operational issues (inventory, regional sales gaps, seasonality)?
    3. Give 3 actionable improvement suggestions.

    Please respond in **clear bullet points**.
    """
    business_analysis = ask_llm(analysis_prompt)
    st.write(business_analysis)
