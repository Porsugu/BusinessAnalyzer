# 🚀 Enterprise Sales AI Analyst (Local LLM)

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Local-black?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

An intelligent, privacy-first analytics platform that transforms raw sales data into actionable business strategies. Powered by **Local LLMs (Ollama/Llama3)**, this tool simulates the role of a Chief Revenue Officer (CRO), offering deep customer segmentation (RFM), retention metrics, and conversational insights without sending data to the cloud.

---

## 🌟 Key Features

### 1. 🧠 Intelligent Data Mapping (Auto-Schema)
- Uses LLM to **automatically infer** complex column roles (e.g., distinguishing between `Transaction Date`, `Customer ID`, and `Revenue`).
- Robust error handling with JSON cleaning logic ensures stability even with verbose LLM outputs.

### 2. 📈 Executive KPI Dashboard
- Real-time calculation of critical metrics:
  - **AOV (Average Order Value)**
  - **UPT (Units Per Transaction / Basket Size)**
  - **MoM Growth (Month-over-Month)**
  - **Repeat Purchase Rate** (Loyalty metric)

### 3. 👥 RFM Customer Segmentation (Advanced)
- Implements the **Recency, Frequency, Monetary (RFM)** model to classify customers into actionable cohorts:
  - 🏆 **Champions (VIPs)**: High value, recent buyers.
  - 💎 **Loyal Customers**: Frequent buyers.
  - 💤 **Lost/Churned**: High value but inactive.
- **Strategic Visualization**: Scatter plots and distribution charts to identify revenue concentration.

### 4. 💬 Chat with Your Data
- A built-in **Conversational Interface** allows non-technical users to query data naturally.
- *Example: "Why did sales drop in Q4?"* or *"Who is our most valuable customer?"*

### 5. 🔒 100% Local & Private
- Runs entirely on your machine using **Ollama**.
- Zero data leakage—perfect for sensitive financial datasets.

---

## 🛠 Tech Stack

- **Frontend/UI**: Streamlit
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly Express (Interactive Charts)
- **AI/Inference**: Ollama (Llama 3 / Mistral) via `requests`
- **Architecture**: Python modular design with Session State management for scalability.

---

## 🚀 Quick Start

### Prerequisites
1. **Python 3.10+** installed.
2. **[Ollama](https://ollama.com/)** installed and running.

### Installation

1️⃣ **Clone the repository**
```bash
git clone [https://github.com/yourusername/sales-ai-analyst.git](https://github.com/yourusername/sales-ai-analyst.git)
cd sales-ai-analyst