# 📊 Intelligent Business Data Analytics Platform (Ollama)

This project is a **Streamlit web app** that lets you upload **CSV or Excel sales data**, then uses a **local LLM (via Ollama)** to:

✅ **Auto-detect column meanings** (e.g. Date, Product, Sales Amount)  
✅ **Auto-generate meaningful charts** (distributions, time-series trends)  
✅ **Provide AI-driven business insights & improvement suggestions**  

It runs **entirely locally**, so your data stays private. No cloud API required.

---

## 🚀 Features

- 🖱 **Upload CSV or Excel** files for analysis  
- 🧠 **LLM auto-interprets columns** (e.g. detects which is date, sales amount, etc.)  
- 📊 **Auto-generated visualizations**:
  - Numeric column distributions
  - Sales trends over time (if date column detected)
- 💡 **Business insights**: LLM highlights weak-performing products/months and gives suggestions  
- 🏠 **Runs locally with Ollama** → No data leaves your machine  

---

## 🛠 Requirements

- **Python 3.10+**
- **[Ollama](https://ollama.com/) installed** and a local model (e.g. `llama3` or `mistral`)

Python dependencies:
```txt
streamlit
pandas
plotly
matplotlib
requests
openpyxl   # for Excel support
```

---

## 🔧 Setup

1️⃣ **Clone the repo**
```bash
git clone https://github.com/yourusername/sales-data-analyzer.git
cd sales-data-analyzer
```

2️⃣ **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3️⃣ **Install & run Ollama**
- [Download Ollama](https://ollama.com/download)
- Pull a model:
  ```bash
  ollama pull llama3
  ```
- Start the Ollama server:
  ```bash
  ollama serve
  ```
  It will run at `http://localhost:11434`.

4️⃣ **Run the Streamlit app**
```bash
streamlit run sales_analysis_app.py
```

5️⃣ **Open browser**
- Visit `http://localhost:8501`
- Upload a CSV/Excel file and start exploring your sales data!

---

## 📂 Project Structure

```
sales-data-analyzer/
│
├── sales_analysis_app.py   # Main Streamlit app
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

---

## 🖼 Example Workflow

1. **Upload a file (CSV/Excel)**  
2. The LLM infers column meanings:  
   ```json
   {
     "Date": "Transaction date",
     "Product": "Product name",
     "Amount": "Total sales amount"
   }
   ```
3. Charts are generated:
   - Sales distribution
   - Time series trends
4. AI provides business insights:
   - Which products/regions/months are underperforming
   - Suggestions for improvements

*(You can later add screenshots here)*

---

## ⚡ Future Improvements

- 🗺 **Regional sales heatmap** (if region column exists)  
- 📈 **LLM-driven dynamic chart selection**  
- 📄 **Export AI report as PDF**  
- 🐳 **Docker support for easy deployment**  
- 🔗 **Optional cloud LLM (OpenAI) for higher accuracy**

---

## 💻 Tech Stack

- **[Streamlit](https://streamlit.io/)** → interactive UI  
- **[Pandas](https://pandas.pydata.org/)** → CSV/Excel processing  
- **[Plotly](https://plotly.com/python/)** → interactive charts  
- **[Ollama](https://ollama.com/)** → local LLM for reasoning & insights  

---

## 📝 License

MIT License © 2025 Your Name

---

## 🤝 Contributing

Pull requests and suggestions are welcome!  
You can also open an **Issue** if you have feature requests or bug reports.

---

## 🙌 Acknowledgements

- Thanks to [Ollama](https://ollama.com/) for making local LLMs easy to run  
- Inspired by business analytics workflows for SMBs
