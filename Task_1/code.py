import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv("dataset/data.csv")  # replace with your file
    df = df.loc[:, ~df.columns.str.contains('@|^Unnamed')]
    df['Amount Spent in INR'] = df['Amount Spent in INR'].replace('[\$,]', '', regex=True).astype(float)
    df['Cost Per Click (CPC)'] = df['Cost Per Click (CPC)'].replace('[\$,]', '', regex=True).astype(float)
    df['Cost per Result (CPR)'] = df['Cost per Result (CPR)'].replace('[\$,]', '', regex=True).astype(float)
    df['Click-Through Rate (CTR in %)'] = df['Click-Through Rate (CTR in %)'].astype(float)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter")
campaigns = st.sidebar.multiselect("Campaign ID", df['Campaign ID'].unique(), default=df['Campaign ID'].unique())
geos = st.sidebar.multiselect("Geography", df['Geography'].unique(), default=df['Geography'].unique())
ages = st.sidebar.multiselect("Age Group", df['Age'].unique(), default=df['Age'].unique())

filtered = df[
    df['Campaign ID'].isin(campaigns) &
    df['Geography'].isin(geos) &
    df['Age'].isin(ages)
]

st.title("📊 Campaign Dashboard (Interactive)")

# --- KPIs ---
total_spent = filtered["Amount Spent in INR"].sum()
avg_ctr = filtered["Click-Through Rate (CTR in %)"].mean()
avg_cpc = filtered["Cost Per Click (CPC)"].mean()

col1, col2, col3 = st.columns(3)
col1.metric("💰 Total Spent", f"₹{total_spent:,.0f}")
col2.metric("📈 Avg CTR", f"{avg_ctr:.2f}%")
col3.metric("🪙 Avg CPC", f"₹{avg_cpc:.2f}")

# --- CTR by Age Group (Interactive Plotly) ---
st.subheader("CTR by Age Group")
ctr_data = filtered.groupby('Age')["Click-Through Rate (CTR in %)"].mean().reset_index()
fig1 = px.bar(ctr_data, x='Age', y='Click-Through Rate (CTR in %)', color='Age',
              title="CTR by Age Group", labels={'Click-Through Rate (CTR in %)': 'CTR (%)'})
st.plotly_chart(fig1, use_container_width=True)

# --- CPC vs CPR Scatter ---
st.subheader("CPC vs CPR")
fig2 = px.scatter(filtered, x="Cost Per Click (CPC)", y="Cost per Result (CPR)",
                  color="Age", hover_data=["Campaign Name"], title="CPC vs CPR")
st.plotly_chart(fig2, use_container_width=True)

# --- Spend by Geography ---
st.subheader("Amount Spent by Geography")
geo_spent = filtered.groupby("Geography")["Amount Spent in INR"].sum().reset_index()
fig3 = px.bar(geo_spent, x="Geography", y="Amount Spent in INR", title="Total Spend by Geography")
st.plotly_chart(fig3, use_container_width=True)

# --- Clicks vs Impressions ---
st.subheader("Clicks vs Impressions")
clicks_imps = filtered.groupby("Campaign Name")[["Clicks", "Impressions"]].sum().reset_index()
fig4 = px.bar(clicks_imps, x="Campaign Name", y=["Clicks", "Impressions"],
              title="Clicks and Impressions", barmode='group')
st.plotly_chart(fig4, use_container_width=True)

# --- CTR vs Frequency ---
st.subheader("CTR vs Frequency")
fig5 = px.scatter(filtered, x="Frequency", y="Click-Through Rate (CTR in %)", 
                  color="Age", hover_data=["Campaign Name"], 
                  title="CTR vs Frequency")
st.plotly_chart(fig5, use_container_width=True)

# --- Spend per Click by Campaign ---
st.subheader("Spend per Click by Campaign")
spc_df = filtered.copy()
spc_df['Spend per Click'] = spc_df['Amount Spent in INR'] / spc_df['Clicks'].replace(0, pd.NA)
spc_df = spc_df.dropna(subset=['Spend per Click'])
fig6 = px.bar(spc_df, x="Campaign Name", y="Spend per Click", 
              color="Campaign Name", title="Spend per Click (INR) by Campaign")
st.plotly_chart(fig6, use_container_width=True)

# --- Map: Spend by Geography (Choropleth) ---
st.subheader("🗺️ Spend by Geography Map")

import pycountry

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

geo_map_df = geo_spent.copy()
geo_map_df["iso_alpha"] = geo_map_df["Geography"].apply(get_country_code)
geo_map_df = geo_map_df.dropna(subset=["iso_alpha"])

fig7 = px.choropleth(geo_map_df, 
                     locations="iso_alpha",
                     color="Amount Spent in INR",
                     hover_name="Geography",
                     color_continuous_scale=px.colors.sequential.Plasma,
                     title="Amount Spent by Geography (Map)")
st.plotly_chart(fig7, use_container_width=True)


# --- Save plots as PNG ---
def fig_to_download(fig, filename="plot.png"):
    buffer = BytesIO()
    fig.write_image(buffer, format='png')
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:file/png;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

st.markdown("---")
st.subheader("📥 Download Plots")
col1, col2 = st.columns(2)
with col1:
    st.markdown(fig_to_download(fig1, "ctr_by_age.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig3, "spend_by_geo.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig5, "ctr_vs_frequency.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig7, "spend_map.png"), unsafe_allow_html=True)

with col2:
    st.markdown(fig_to_download(fig2, "cpc_vs_cpr.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig4, "clicks_impressions.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig6, "spend_per_click.png"), unsafe_allow_html=True)

