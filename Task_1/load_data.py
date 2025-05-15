# --- Load Data ---
import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "data.csv"))
    
    # Change "Amount Spent in INR" to "Amount Spent" since we're displaying it as a generic currency
    df = df.rename(columns={"Amount Spent in INR": "Amount Spent"})
    
    # Clean up currency and convert to numeric
    df['Amount Spent'] = df['Amount Spent'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Cost Per Click (CPC)'] = df['Cost Per Click (CPC)'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Cost per Result (CPR)'] = df['Cost per Result (CPR)'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # Calculate additional metrics
    df['Conversion Rate'] = df['Unique Link Clicks (ULC)'] / df['Impressions'] * 100
    df['ROI Score'] = df['Unique Link Clicks (ULC)'] / df['Amount Spent']
    df['Efficiency Score'] = df['Click-Through Rate (CTR in %)'] / df['Cost per Result (CPR)']
    df['CPM'] = df['Amount Spent'] / df['Impressions'] * 1000  # Renamed to simpler CPM
    
    return df