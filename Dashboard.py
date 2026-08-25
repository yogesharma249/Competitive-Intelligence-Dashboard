# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 19:09:35 2026

@author: DELL
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from strategy_n_CVS import calculate_cvs_and_strategy


st.set_page_config(page_title="CompIntel Dashboard", layout="wide")

st.title("🛡️ Competitive Intelligence Dashboard")

# --- MOCK DATA ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        'broker_name': ['Legacy Incumbent', 'NeoBroker A', 'NeoBroker B'],
        'standard_order_fee': [15.00, 1.00, 0.00],
        'sentiment_score': [-0.2, 0.6, -0.5]
    })

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("Strategy Weights")
    w_price = st.slider("Price Sensitivity ($w_p$)", 0.0, 1.0, 0.6)
    w_sent = st.slider("Sentiment Impact ($w_s$)", 0.0, 1.0, 0.4)
    
    # Normalize weights so they equal 1.0
    total = w_price + w_sent
    w_price, w_sent = w_price/total, w_sent/total

# --- CALCULATE STRATEGY ---
df_strategy = calculate_cvs_and_strategy(st.session_state.data, w_price, w_sent)

# --- UI LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Market Vulnerability Matrix")
    # Using Plotly for a clean interactive scatter plot
    fig = px.scatter(
        df_strategy, x="z_price", y="z_sentiment", 
        color="cvs", text="broker_name", size_max=60,
        color_continuous_scale="RdYlGn_r" # Red is high vulnerability
    )
    fig.add_hline(y=0, line_dash="dash")
    fig.add_vline(x=0, line_dash="dash")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Recommended Tactics")
    # Streamlit's updated dataframe with programmatic styling
    st.dataframe(
        df_strategy[['broker_name', 'cvs', 'recommended_tactic']],
        hide_index=True,
        use_container_width=True
    )