import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import re

# ==========================================
# 1. Utility Functions & LLM Configuration
# ==========================================

def clean_llm_json(response_text):
    """
    Extracts JSON from LLM response even if it includes conversational text.
    """
    try:
        # Try finding a code block first
        match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try finding first { and last }
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(response_text)
    except:
        return None

def ask_llm(prompt, model="llama3", json_mode=False):
    """Call Ollama local LLM API with improved error handling"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json" if json_mode else None
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()["response"]
        if json_mode:
            return clean_llm_json(result)
        return result
    except Exception as e:
        st.error(f"Error communicating with Ollama: {e}")
        return None

# ==========================================
# 2. Main Streamlit App
# ==========================================

st.set_page_config(page_title="AI Sales Analyst Pro", layout="wide")

st.title("🚀 Enterprise Sales AI Analyst")
st.markdown("### Powered by Local LLM (Ollama) & Python")

# Sidebar for controls
with st.sidebar:
    st.header("⚙️ Configuration")
    model_name = st.selectbox("Select Model", ["llama3", "mistral", "gemma"], index=0)
    st.info("Ensure Ollama is running locally: `ollama run llama3`")

uploaded_file = st.file_uploader("📂 Upload Sales Data (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    st.write("---")
    
    # ==========================================
    # 3. Intelligent Column Mapping (The "Brain")
    # ==========================================
    # Instead of just "inferring meaning", we map columns to specific roles for plotting.
    
    if "col_map" not in st.session_state:
        with st.spinner("🤖 Analyzing dataset structure..."):
            columns = df.columns.tolist()
            sample_data = df.head(3).to_dict(orient="records")
            
            mapping_prompt = f"""
            Here are the columns: {columns}
            Here is sample data: {sample_data}
            
            Identify the column names that best fit these roles:
            - 'date_col': The main date/time column.
            - 'sales_col': The numeric column representing revenue or sales amount.
            - 'category_col': The main categorical column (product, region, or segment).
            - 'quantity_col': The column representing quantity sold (optional).
            
            Return ONLY a valid JSON object with keys: date_col, sales_col, category_col, quantity_col.
            If a role is not found, set value to null.
            """
            st.session_state.col_map = ask_llm(mapping_prompt, model=model_name, json_mode=True)

    col_map = st.session_state.col_map
    
    # Allow user to override AI mapping if needed
    with st.expander("🛠️ Data Mapping Settings (AI Detected)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        date_col = c1.selectbox("Date Column", df.columns, index=df.columns.get_loc(col_map.get('date_col')) if col_map.get('date_col') in df.columns else 0)
        sales_col = c2.selectbox("Sales/Revenue Column", df.columns, index=df.columns.get_loc(col_map.get('sales_col')) if col_map.get('sales_col') in df.columns else 0)
        cat_col = c3.selectbox("Category Column", df.columns, index=df.columns.get_loc(col_map.get('category_col')) if col_map.get('category_col') in df.columns else 0)
        qty_col = c4.selectbox("Quantity Column", [None] + list(df.columns), index=df.columns.get_loc(col_map.get('quantity_col')) + 1 if col_map.get('quantity_col') in df.columns else 0)

    # Data Type Conversion based on mapping
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
        if qty_col:
            df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
        df = df.dropna(subset=[date_col, sales_col]) # Drop invalid rows
    except Exception as e:
        st.error(f"Data conversion failed: {e}. Please check your column mapping.")
        st.stop()

    # ==========================================
    # 4. KPI Dashboard (Atlassian Style)
    # ==========================================
    st.subheader("📈 Executive Dashboard")
    
    total_revenue = df[sales_col].sum()
    total_orders = len(df)
    avg_order_value = total_revenue / total_orders
    
    # Calculate MoM (Month over Month) Growth
    current_month_sales = df[df[date_col] >= df[date_col].max() - pd.DateOffset(months=1)][sales_col].sum()
    prev_month_sales = df[(df[date_col] >= df[date_col].max() - pd.DateOffset(months=2)) & 
                          (df[date_col] < df[date_col].max() - pd.DateOffset(months=1))][sales_col].sum()
    
    mom_growth = ((current_month_sales - prev_month_sales) / prev_month_sales) * 100 if prev_month_sales != 0 else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Revenue", f"${total_revenue:,.2f}", delta=None)
    kpi2.metric("Total Orders", f"{total_orders}", delta=None)
    kpi3.metric("Avg Order Value (AOV)", f"${avg_order_value:.2f}", delta=None)
    kpi4.metric("MoM Growth (Last 30 days)", f"{mom_growth:.2f}%", delta=f"{mom_growth:.2f}%")

    st.write("---")

    # ==========================================
    # 5. Advanced Visualization Tabs
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📊 Trends & Forecast", "📦 Product & Category", "🧠 AI Insights"])

    with tab1:
        st.subheader("Sales Trends Over Time")
        # Time Series Aggregation
        time_frame = st.radio("Group By:", ["D", "W", "M"], index=2, horizontal=True)
        df_trend = df.set_index(date_col).resample(time_frame)[sales_col].sum().reset_index()
        
        fig_trend = px.line(df_trend, x=date_col, y=sales_col, markers=True, 
                            title="Revenue Trend", template="plotly_dark")
        fig_trend.update_traces(line_color='#0052CC') # Atlassian Blue style
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab2:
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Top Performing Categories")
            df_cat = df.groupby(cat_col)[sales_col].sum().sort_values(ascending=False).reset_index()
            fig_bar = px.bar(df_cat.head(10), x=sales_col, y=cat_col, orientation='h', 
                             color=sales_col, title="Top Categories by Revenue")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            st.subheader("Pareto Analysis (80/20 Rule)")
            if qty_col: # Scatter plot: Price vs Quantity if available
                # Calculate Price per Unit approximation
                df['calculated_price'] = df[sales_col] / df[qty_col]
                fig_scatter = px.scatter(df, x='calculated_price', y=qty_col, color=cat_col,
                                         size=sales_col, hover_data=[cat_col], 
                                         title="Price Elasticity: Price vs Quantity")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Select a Quantity column to see Price/Quantity analysis.")

    with tab3:
        st.subheader("💡 Strategic AI Analysis")
        
        # Prepare context for AI
        top_product = df_cat.iloc[0][cat_col]
        top_val = df_cat.iloc[0][sales_col]
        trend_direction = "UP" if mom_growth > 0 else "DOWN"
        
        analysis_context = f"""
        Total Revenue: {total_revenue}, Trend: {trend_direction} ({mom_growth}%), 
        Top Category: {top_product} (${top_val}), 
        AOV: {avg_order_value}.
        Data spans from {df[date_col].min()} to {df[date_col].max()}.
        """
        
        if st.button("Generate Executive Report"):
            with st.spinner("Writing report..."):
                report_prompt = f"""
                You are a Senior Data Analyst at a top tech company. Analyze this sales data context:
                {analysis_context}
                
                Please provide a report with:
                1. **Executive Summary**: What is the main story of this data?
                2. **Root Cause Analysis**: Why might the trend be {trend_direction}? (Speculate based on standard business logic).
                3. **Actionable Recommendations**: Give 3 specific strategies to improve revenue based on the AOV and top category.
                
                Format as valid Markdown.
                """
                report = ask_llm(report_prompt, model=model_name)
                st.markdown(report)

    # ==========================================
    # 6. Chat with Data (Feature for Resume)
    # ==========================================
    st.write("---")
    st.subheader("💬 Chat with your Data")
    
    # Simple session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about your data (e.g., 'Why is Q4 sales low?')"):
        # Display user message
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.spinner("Analyzing..."):
            # Provide simplified dataframe context (first 10 rows + description) to save context window
            data_context = df.head(10).to_string()
            stats_context = df.describe().to_string()
            
            full_prompt = f"""
            Context:
            User Data Sample: {data_context}
            User Data Stats: {stats_context}
            
            User Question: {prompt}
            
            Answer strictly based on the provided data context. Keep it concise and professional.
            """
            
            response = ask_llm(full_prompt, model=model_name)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
