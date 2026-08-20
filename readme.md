# 🛡️ Competitive Intelligence Dashboard & Strategy Engine

An end-to-end data product that automates competitor benchmarking in the retail brokerage and wealth management sector. This application ingests real-time web data, extracts legal fee matrices from regulatory PDFs, evaluates public market sentiment via financial NLP, and calculates a proprietary quantitative positioning index to recommend automated corporate tactics.

---

## 🚀 Executive Summary & Core Value Prop

Traditional market research is bottlenecked by manual tracking of competitor updates. This project replaces reactive analysis with automated data pipelines. By combining quantitative cost realities with qualitative consumer sentiment, the dashboard calculates a **Competitive Vulnerability Score (CVS)** for market incumbents, highlighting high-probability customer acquisition opportunities.

### Key Capabilities
* **Hybrid Data Ingestion:** Scrapes dynamic HTML landing pages and parses regulatory *Preis- und Leistungsverzeichnis* (PLV) PDFs.
* **Domain-Specific NLP:** Utilizes a specialized transformer model (**FinBERT**) to classify market mood across Reddit, RSS news feeds, and social media.
* **Quantitative Modeling:** Normalizes non-uniform financial metrics using Z-score standardization to generate an actionable strategic index.
* **Dual Frontend Architecture:** Features a rapid-prototype deployment in **Streamlit** alongside an enterprise-grade full-stack implementation in **Reflex** (React/FastAPI).

---

## 🛠️ System Architecture & Tech Stack

* **Ingestion:** `requests`, `BeautifulSoup4`, `pdfplumber` (visual layout table extraction).
* **NLP & Analytics:** Hugging Face `transformers` (`ProsusAI/finbert`), `praw` (Reddit API), `feedparser` (Google News RSS).
* **Data Processing:** `pandas`, `numpy` (Z-score standardization & vectorization).
* **Data Visualization:** `Plotly Express`.
* **Frontend UI:** `Streamlit` (top-down analytical prototyping) & `Reflex` (WebSocket-driven multi-page web app).

---

## 📊 The Strategic Core: The CVS Model

To prevent disparate data types (e.g., Euros vs. qualitative sentiment scale) from distorting analytics, the strategy engine standardizes features using market-relative **Z-scores**:

$$Z_{Price} = \frac{Price - \mu_{Price}}{\sigma_{Price}}$$

$$Z_{Sentiment} = \frac{Sentiment - \mu_{Sentiment}}{\sigma_{Sentiment}}$$

The final **Competitive Vulnerability Score (CVS)** balances these dimensions using user-defined weights ($w_p$ and $w_s$) representing macroeconomic shifts:

$$CVS = (w_p \cdot Z_{Price}) - (w_s \cdot Z_{Sentiment})$$

### Automated Tactical Matrix
Based on where an incumbent falls within the standardized quadrants, the engine flags actionable items:
* **CVS > 1.0 (High Vulnerability):** Incumbent is overcharging while suffering poor public sentiment. *Action: Trigger aggressive target acquisition campaigns.*
* **Low Price / Low Sentiment:** High-churn operational risk. *Action: Focus on brand rehabilitation and UX adjustments.*
* **High Price / High Sentiment:** Defensible premium position. *Action: Maintain margins; differentiate via high-touch custom services.*

---

## 📂 Project Structure

```text
├── Dashboard.py             # Streamlit application entry point
├──setup.py                  # uniform file importing resource file
├── strategy_n_CVS.py        # Core Z-score & CVS logic mathematical module
├── unified_ingestion.py     # Hybrid HTML scraper & PDF compliance parser
├── sentimental_analysis.py  # Reddit, RSS, and X text analysis using FinBERT
├── requirements.txt         # Managed project dependencies
└── README.md                # Repository documentation