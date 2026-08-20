# Competitive Intelligence Dashboard & Strategy Engine

A prototype toolkit for benchmarking retail brokers against each other. It pulls competitor fee data from web pages and regulatory PDFs, scores public sentiment about each broker with a finance-tuned language model, and combines the two into a single **Competitive Vulnerability Score (CVS)** that maps onto a recommended tactic. Results are explored in a Streamlit dashboard.

The project targets the German retail brokerage market: the PDF parser looks for fee terms from a *Preis- und Leistungsverzeichnis* (PLV), and the Reddit scraper reads r/Finanzen and r/investing.

---

## How it fits together

```
Unified_Ingestion.py       sentimental_analysis.py
  HTML + PDF fee scraping    Reddit / Google News / X sentiment (FinBERT)
              \                        /
               \                      /
                v                    v
              strategy_n_CVS.py
              Z-score normalisation -> CVS -> tactic
                        |
                        v
                   Dashboard.py
                Streamlit UI (Plotly scatter + tactics table)
```

The three data modules run independently today. `Dashboard.py` calls the strategy engine on a small hardcoded DataFrame rather than on live ingestion output, so wiring the pipelines into the dashboard is the obvious next step (see [Known gaps](#known-gaps)).

---

## The CVS model

Fees are in euros and sentiment is on a −1.0 to 1.0 scale, so the two are standardised as Z-scores across the set of brokers being compared before they are combined:

```
z_price     = (fee - mean(fee)) / std(fee)
z_sentiment = (sentiment - mean(sentiment)) / std(sentiment)

CVS = w_price * z_price - w_sentiment * z_sentiment
```

A high CVS means a broker charges more than its peers *and* is talked about worse than its peers — an opening to compete for its customers. The weights default to `0.6 / 0.4` and are adjustable from the dashboard sidebar (they are renormalised to sum to 1).

`calculate_cvs_and_strategy` then assigns a tactic:

| Condition | Recommended tactic |
| --- | --- |
| `CVS > 1.0` | Aggressive acquisition — target with cost-leadership marketing |
| `CVS < -1.0` | Avoid direct competition — differentiate via niche features |
| `z_price < 0` and `z_sentiment < 0` | Brand rehabilitation — invest in UX/UI and customer service |
| `z_price > 0` and `z_sentiment > 0` | Premium justification — keep high-touch service to defend margins |
| otherwise | Monitor — position is at equilibrium |

Because the scores are relative to the input set, adding or removing a broker changes everyone's CVS. Use at least three or four competitors for the numbers to mean anything.

---

## Getting started

Requires Python 3.9+.

```bash
git clone https://github.com/yogesharma249/Competitive-Intelligence-Dashboard.git
cd Competitive-Intelligence-Dashboard

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirement.txt
```

The dependency file is named `requirement.txt` (singular). Installing it pulls in `torch` and `transformers`, which is a large download; skip them if you only want the dashboard and strategy engine.

Run the dashboard:

```bash
streamlit run Dashboard.py
```

It opens on <http://localhost:8501> with the built-in sample brokers.

---

## Running the modules

### Fee ingestion

```bash
python Unified_Ingestion.py
```

Prints a markdown table of the compiled fee data. Which brokers get scraped, and how, is set in `BROKER_CONFIG` at the top of the file:

```python
BROKER_CONFIG = {
    "Trade Republic": {
        "type": "html",
        "url": "https://traderepublic.com/en-de/about",
        "selectors": {"standard_order_fee": "div[data-testid='pricing-order'] span", ...},
    },
    "Legacy Bank (Mock)": {
        "type": "pdf",
        "url": "https://example.com/legal/preis-und-leistungsverzeichnis.pdf",
        "keywords": {"standard_order_fee": ["Orderprovision", "Grundentgelt pro Order"], ...},
    },
}
```

* `type: "html"` fetches the page and pulls each fee with a CSS selector via BeautifulSoup.
* `type: "pdf"` downloads the document, scans tables on the first five pages with `pdfplumber`, and takes the first number from any row matching one of the German fee keywords.

Both routes run their result through `clean_fee_string`, which treats "free"/"kostenlos"/"gratis" as `0.0` and converts German decimal commas. Call `run_ingestion_pipeline()` to get the DataFrame directly instead of printing it.

The two entries shipped in `BROKER_CONFIG` are illustrative. The Trade Republic selectors are guesses at that site's markup and the PDF URL is a placeholder, so expect to replace both with real targets before the numbers are usable.

### Sentiment

```bash
python sentimental_analysis.py
```

`MarketSentimentPipeline` loads `ProsusAI/finbert` (downloaded from Hugging Face on first run) and gathers headlines from three sources:

| Method | Source | Auth |
| --- | --- | --- |
| `fetch_reddit` | r/Finanzen + r/investing search | Reddit API credentials |
| `fetch_news` | Google News RSS | none |
| `fetch_x` | placeholder, returns mock posts | n/a |

Each headline is classified positive/neutral/negative and turned into a net score in `[-1.0, 1.0]` by multiplying the label by the model's confidence. `aggregate_sentiment(broker_name)` returns every signal as a DataFrame; the mean of `sentiment_score` is the broker's aggregate sentiment.

Reddit access needs a script-type app from <https://www.reddit.com/prefs/apps>. The `__main__` block currently has placeholder strings:

```python
pipeline = MarketSentimentPipeline("YOUR_ID", "YOUR_SECRET")
```

Replace them with your own client ID and secret — preferably read from environment variables rather than committed to the file. `fetch_x` returns fabricated posts and exists only to keep the interface complete; X data needs paid API access.

### Strategy engine

`strategy_n_CVS.py` has no CLI. Import it:

```python
import pandas as pd
from strategy_n_CVS import calculate_cvs_and_strategy

df = pd.DataFrame({
    "broker_name": ["Legacy Incumbent", "NeoBroker A", "NeoBroker B"],
    "standard_order_fee": [15.00, 1.00, 0.00],
    "sentiment_score": [-0.2, 0.6, -0.5],
})

result = calculate_cvs_and_strategy(df, weight_price=0.6, weight_sentiment=0.4)
print(result[["broker_name", "cvs", "recommended_tactic"]])
```

It needs `broker_name`, `standard_order_fee`, and `sentiment_score` columns, and returns the frame with `z_price`, `z_sentiment`, `cvs`, and `recommended_tactic` added, sorted by CVS descending. It mutates the DataFrame you pass in, so hand it a copy if that matters.

---

## Project structure

```text
├── Dashboard.py             # Streamlit UI: weight sliders, Plotly quadrant chart, tactics table
├── Unified_Ingestion.py     # HTML scraper + regulatory PDF fee parser
├── sentimental_analysis.py  # Reddit / Google News / X sentiment via FinBERT
├── strategy_n_CVS.py        # Z-score normalisation, CVS, tactic assignment
├── setup.py                 # setuptools stub for local installs
├── requirement.txt          # dependencies
└── LICENSE                  # MIT
```

## Tech stack

`streamlit` and `plotly` for the frontend, `requests` + `beautifulsoup4` + `pdfplumber` for ingestion, `transformers` (FinBERT) + `praw` + `feedparser` for sentiment, `pandas` and `numpy` for the analytics.

## License

MIT — see [LICENSE](LICENSE).
