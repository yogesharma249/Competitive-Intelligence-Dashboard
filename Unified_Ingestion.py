# -*- coding: utf-8 -*-
"""
Created on Sat May 30 20:33:24 2026

@author: DELL
"""

import re
import requests
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
from io import BytesIO

# --- Configuration & Headers ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9,de;q=0.8"
}

# Master config dictates which strategy to use per broker
BROKER_CONFIG = {
    "Trade Republic": {
        "type": "html",
        "url": "https://traderepublic.com/en-de/about",
        "selectors": {
            "custody_fee_annual": "div[data-testid='pricing-custody'] span",
            "standard_order_fee": "div[data-testid='pricing-order'] span",
            "savings_plan_fee": "div[data-testid='pricing-savings'] span"
        }
    },
    "Legacy Bank (Mock)": {
        "type": "pdf",
        "url": "https://example.com/legal/preis-und-leistungsverzeichnis.pdf",
        # Mapping keywords to our standard database schema
        "keywords": {
            "custody_fee_annual": ["Depotführung", "Verwahrgebühr"],
            "standard_order_fee": ["Orderprovision", "Grundentgelt pro Order"],
            "savings_plan_fee": ["Sparplanausführung", "Sparplan"]
        }
    }
}

# --- Normalization Engine ---
def clean_fee_string(raw_text: str) -> float:
    """Normalizes currency text into clean floating point values."""
    if not raw_text: return None
    cleaned = str(raw_text).lower().strip()
    
    if any(word in cleaned for word in ["free", "kostenlos", "gratis", "0 €", "0,00"]):
        return 0.0
        
    cleaned = cleaned.replace(",", ".")
    match = re.search(r"[-+]?\d*\.\d+|\d+", cleaned)
    return float(match.group()) if match else None

# --- Extraction Engines ---
def extract_html(broker_name: str, config: dict) -> dict:
    """Parses targeted CSS selectors from HTML landing pages."""
    result = {"broker_name": broker_name, "source": "HTML"}
    try:
        response = requests.get(config["url"], headers=HEADERS, timeout=10)
        if response.status_code != 200: return result
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        for fee_type, selector in config["selectors"].items():
            element = soup.select_one(selector)
            # If element is found, clean it; otherwise default to a mock string for this example
            raw_text = element.text if element else ("0.0" if "savings" in fee_type else "1.00") 
            result[fee_type] = clean_fee_string(raw_text)
            
    except Exception as e:
        print(f"[Error] HTML extraction failed for {broker_name}: {e}")
    return result

def extract_pdf(broker_name: str, config: dict) -> dict:
    """Parses regulatory PDFs and searches tables for keyword mappings."""
    result = {"broker_name": broker_name, "source": "PDF"}
    try:
        response = requests.get(config["url"], timeout=10)
        if response.status_code != 200: return result
            
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            for page in pdf.pages[:5]: # Scan first 5 pages for efficiency
                for table in page.extract_tables():
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ').strip() for cell in row if cell]
                        
                        # Match row content against our targeted keywords
                        for fee_type, keywords in config["keywords"].items():
                            if any(any(kw.lower() in cell.lower() for kw in keywords) for cell in clean_row):
                                # If keyword found, grab the first identifiable number in that row
                                for cell in clean_row:
                                    val = clean_fee_string(cell)
                                    if val is not None and fee_type not in result:
                                        result[fee_type] = val
                                        break
    except Exception as e:
        print(f"[Error] PDF extraction failed for {broker_name}: {e}")
    return result

# --- Orchestrator ---
def run_ingestion_pipeline() -> pd.DataFrame:
    """Routes each broker to the correct extraction engine and compiles the data."""
    compiled_data = []
    
    for broker, config in BROKER_CONFIG.items():
        print(f"Processing {broker} via {config['type'].upper()}...")
        if config["type"] == "html":
            compiled_data.append(extract_html(broker, config))
        elif config["type"] == "pdf":
            compiled_data.append(extract_pdf(broker, config))
            
    # Convert to DataFrame and ensure consistent columns
    df = pd.DataFrame(compiled_data)
    cols = ["broker_name", "source", "custody_fee_annual", "standard_order_fee", "savings_plan_fee"]
    return df.reindex(columns=cols)

if __name__ == "__main__":
    df_competitors = run_ingestion_pipeline()
    print("\n--- Consolidated Competitive Pricing Data ---")
    print(df_competitors.to_markdown(index=False))