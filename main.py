import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import re
import datetime

# ==========================================
# 1. Utility Functions
# ==========================================

def clean_llm_json(response_text):
    try:
        match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
        if match: return json.loads(match.group(1))
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match: return json.loads(match.group(0))
        return json.loads(response_text)
    except:
        return None

def ask_llm(prompt, model="llama3", json_mode=False):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model, "prompt": prompt, "stream": False,
        "format": "json" if json_mode else None
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()["response"]
        return clean_llm_json(result) if json_mode else result
    except Exception as e:
        # st.error(f"Error: {e}") # Suppress temporary errors
        return None

# ==========================================
# 2. Main Streamlit App
# ==========================================

st.set_page_config(page_title="AI Sales Analyst", layout="wide")
st.title("Enterprise Sales AI Analyst")
st.markdown("### Featuring: RFM Analysis, Cohort Metrics & Local LLM Insights")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    model_name = st.selectbox("LLM Model", ["llama3", "mistral"], index=0)
    st.info("Ensure Ollama is running: `ollama run llama3`")

uploaded_file = st.file_uploader("📂 Upload Sales Data (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load Data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Read Error: {e}")
        st.stop()

    st.write("---")
    
    # ==========================================
    # 3. Intelligent Column Mapping (Upgraded)
    # ==========================================
    if "col_map" not in st.session_state:
        with st.spinner("🤖 AI is analyzing dataset structure..."):
            columns = df.columns.tolist()
            sample_data = df.head(3).to_dict(orient="records")
            
            mapping_prompt = f"""
            Analyze these columns: {columns}
            Sample data: {sample_data}
            
            Map columns to these roles (return null if not found):
            - 'date_col': Transaction date.
            - 'sales_col': Revenue/Sales amount.
            - 'category_col': Product category or Name.
            - 'quantity_col': Quantity sold.
            - 'customer_col': Customer ID, Name, or Email (Critical for RFM).
            - 'order_id_col': Order ID or Invoice Number.
            
            Return ONLY valid JSON. Keys: date_col, sales_col, category_col, quantity_col, customer_col, order_id_col.
            """
            st.session_state.col_map = ask_llm(mapping_prompt, model=model_name, json_mode=True)

    col_map = st.session_state.col_map or {}

    # Manual Override
    with st.expander("🛠️ Column Mapping (Verify AI Detection)", expanded=False):
        c1, c2, c3 = st.columns(3)
        date_col = c1.selectbox("Date", df.columns, index=df.columns.get_loc(col_map.get('date_col')) if col_map.get('date_col') in df.columns else 0)
        sales_col = c2.selectbox("Revenue", df.columns, index=df.columns.get_loc(col_map.get('sales_col')) if col_map.get('sales_col') in df.columns else 0)
        cat_col = c3.selectbox("Category", df.columns, index=df.columns.get_loc(col_map.get('category_col')) if col_map.get('category_col') in df.columns else 0)
        
        c4, c5, c6 = st.columns(3)
        qty_col = c4.selectbox("Quantity (Optional)", [None] + list(df.columns), index=df.columns.get_loc(col_map.get('quantity_col')) + 1 if col_map.get('quantity_col') in df.columns else 0)
        cust_col = c5.selectbox("Customer ID (Optional)", [None] + list(df.columns), index=df.columns.get_loc(col_map.get('customer_col')) + 1 if col_map.get('customer_col') in df.columns else 0)
        order_col = c6.selectbox("Order ID (Optional)", [None] + list(df.columns), index=df.columns.get_loc(col_map.get('order_id_col')) + 1 if col_map.get('order_id_col') in df.columns else 0)

    # Data Processing
    try:
        df[date_col] = pd.to_datetime(df[date_col])
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
        if qty_col: df[qty_col] = pd.to_numeric(df[qty_col], errors='coerce')
        df = df.dropna(subset=[date_col, sales_col])
    except:
        st.error("Data conversion failed. Check mapping.")
        st.stop()

    # ==========================================
    # 4. Enterprise KPI Dashboard
    # ==========================================
    st.subheader("📈 Executive Dashboard")
    
    # Basic calculations
    total_revenue = df[sales_col].sum()
    unique_orders = df[order_col].nunique() if order_col else len(df)
    aov = total_revenue / unique_orders
    
    # Advanced: Basket Size (UPT)
    avg_basket_size = (df[qty_col].sum() / unique_orders) if qty_col and unique_orders else 0
    
    # Advanced: Repeat Purchase Rate (Requires Customer ID)
    repeat_rate_str = "N/A"
    if cust_col:
        cust_counts = df.groupby(cust_col).size()
        repeat_customers = cust_counts[cust_counts > 1].count()
        total_customers = cust_counts.count()
        repeat_rate = (repeat_customers / total_customers * 100) if total_customers else 0
        repeat_rate_str = f"{repeat_rate:.1f}%"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Revenue", f"${total_revenue:,.0f}")
    k2.metric("Orders", f"{unique_orders:,}")
    k3.metric("AOV (Avg Order Value)", f"${aov:.2f}")
    k4.metric("Basket Size (UPT)", f"{avg_basket_size:.1f} units")
    k5.metric("Repeat Cust. Rate", repeat_rate_str)
    
    st.write("---")

    # ==========================================
    # 5. Advanced Analysis Tabs
    # ==========================================
    tab1, tab2, tab3 = st.tabs(["📊 Market Trends", "👥 RFM Customer Segments", "🧠 AI Strategy"])

    with tab1:
        # Time Series
        df_trend = df.set_index(date_col).resample('M')[sales_col].sum().reset_index()
        fig_trend = px.line(df_trend, x=date_col, y=sales_col, markers=True, title="Monthly Revenue Trend", template="plotly_dark")
        fig_trend.update_traces(line_color='#0052CC')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Category Breakdown
        top_cats = df.groupby(cat_col)[sales_col].sum().nlargest(10).reset_index()
        fig_bar = px.bar(top_cats, x=sales_col, y=cat_col, orientation='h', title="Top Revenue Generators", color=sales_col)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        if cust_col:
            st.markdown("### RFM Analysis (Recency, Frequency, Monetary)")
            st.info("RFM segments customers based on purchasing behavior. Industry standard for retention.")
            
            # Prepare RFM Data
            snapshot_date = df[date_col].max() + datetime.timedelta(days=1)
            rfm = df.groupby(cust_col).agg({
                date_col: lambda x: (snapshot_date - x.max()).days, # Recency
                order_col if order_col else date_col: 'count',        # Frequency
                sales_col: 'sum'                                      # Monetary
            }).rename(columns={date_col: 'Recency', order_col if order_col else date_col: 'Frequency', sales_col: 'Monetary'})
            
            # Simple Scoring (Quantiles)
            rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1]) # Lower recency is better
            rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
            rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
            rfm['RFM_Segment'] = rfm.apply(lambda x: str(x['R_Score']) + str(x['F_Score']) + str(x['M_Score']), axis=1)
            
            # Define Segments
            def segment_customer(df):
                if df['RFM_Segment'] == '444': return 'Champions (VIP)'
                elif df['F_Score'] == 4: return 'Loyal Customers'
                elif df['M_Score'] == 4: return 'Big Spenders'
                elif df['R_Score'] == 1: return 'Lost/Churned'
                else: return 'Others'
            
            rfm['Segment'] = rfm.apply(segment_customer, axis=1)
            
            # Visualization
            c1, c2 = st.columns(2)
            with c1:
                seg_counts = rfm['Segment'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                fig_pie = px.pie(seg_counts, names='Segment', values='Count', title="Customer Segmentation Distribution", hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with c2:
                fig_scatter = px.scatter(rfm, x='Recency', y='Monetary', color='Segment', size='Frequency', 
                                         hover_data=['Recency', 'Frequency', 'Monetary'], log_y=True,
                                         title="Customer Value Matrix (Recency vs Monetary)")
                st.plotly_chart(fig_scatter, use_container_width=True)
                
            st.dataframe(rfm.head())
        else:
            st.warning("⚠️ Please map a 'Customer ID' column to enable RFM Analysis.")

    with tab3:
        st.subheader("💡 Chief Revenue Officer (CRO) Insights")
        if st.button("Generate Strategic Report"):
            with st.spinner("Consulting AI Model..."):
                # Prepare Context
                summary_stats = f"""
                Total Rev: ${total_revenue}, Orders: {unique_orders}, AOV: ${aov:.2f}, 
                Repeat Rate: {repeat_rate_str}, Basket Size: {avg_basket_size:.1f}.
                Top Category: {top_cats.iloc[0][cat_col]} (${top_cats.iloc[0][sales_col]}).
                """
                
                rfm_context = ""
                if cust_col:
                    rfm_counts = rfm['Segment'].value_counts().to_dict()
                    rfm_context = f"Customer Segments: {rfm_counts}"

                prompt = f"""
                Act as a Chief Revenue Officer. Analyze this data:
                {summary_stats}
                {rfm_context}
                
                Provide a strategic memo in Markdown:
                1. **Health Check**: Is the business healthy based on Repeat Rate and AOV?
                2. **RFM Action Plan**: How to treat 'Champions' vs 'Lost' customers? (If RFM data exists)
                3. **Growth Strategy**: 3 specific tactics to increase Revenue.
                """
                
                response = ask_llm(prompt, model=model_name)
                st.markdown(response)