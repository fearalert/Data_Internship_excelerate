import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
import pycountry

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
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

# --- CTR by Age Group ---
st.subheader("CTR by Age Group")
ctr_data = filtered.groupby('Age')["Click-Through Rate (CTR in %)"].mean().reset_index()
fig_ctr_age = px.bar(ctr_data, x='Age', y='Click-Through Rate (CTR in %)', color='Age',
                     title="CTR by Age Group", labels={'Click-Through Rate (CTR in %)': 'CTR (%)'})
st.plotly_chart(fig_ctr_age, use_container_width=True)

# --- CPC vs CPR Scatter ---
st.subheader("CPC vs CPR")
fig_cpc_cpr = px.scatter(filtered, x="Cost Per Click (CPC)", y="Cost per Result (CPR)",
                         color="Age", hover_data=["Campaign Name"], title="CPC vs CPR")
st.plotly_chart(fig_cpc_cpr, use_container_width=True)

# --- Spend by Geography ---
st.subheader("Amount Spent by Geography")
geo_spent = filtered.groupby("Geography")["Amount Spent in INR"].sum().reset_index()
fig_geo_spend = px.bar(geo_spent, x="Geography", y="Amount Spent in INR", title="Total Spend by Geography")
st.plotly_chart(fig_geo_spend, use_container_width=True)

# --- Clicks vs Impressions ---
st.subheader("Clicks vs Impressions")
clicks_imps = filtered.groupby("Campaign Name")[["Clicks", "Impressions"]].sum().reset_index()
fig_clicks_imps = px.bar(clicks_imps, x="Campaign Name", y=["Clicks", "Impressions"],
                         title="Clicks and Impressions", barmode='group')
st.plotly_chart(fig_clicks_imps, use_container_width=True)

# --- CTR vs Frequency ---
st.subheader("CTR vs Frequency")
fig_ctr_freq = px.scatter(filtered, x="Frequency", y="Click-Through Rate (CTR in %)",
                          color="Age", hover_data=["Campaign Name"],
                          title="CTR vs Frequency")
st.plotly_chart(fig_ctr_freq, use_container_width=True)

# --- Spend per Click by Campaign ---
st.subheader("Spend per Click by Campaign")
spc_df = filtered.copy()
spc_df['Spend per Click'] = spc_df['Amount Spent in INR'] / spc_df['Clicks'].replace(0, pd.NA)
spc_df = spc_df.dropna(subset=['Spend per Click'])
fig_spend_click = px.bar(spc_df, x="Campaign Name", y="Spend per Click",
                         color="Campaign Name", title="Spend per Click (INR) by Campaign")
st.plotly_chart(fig_spend_click, use_container_width=True)

# --- Map: Spend by Geography (Choropleth) ---
st.subheader("🗺️ Spend by Geography Map")

def get_country_code(name):
    try:
        return pycountry.countries.lookup(name).alpha_3
    except:
        return None

geo_map_df = geo_spent.copy()
geo_map_df["iso_alpha"] = geo_map_df["Geography"].apply(get_country_code)
geo_map_df = geo_map_df.dropna(subset=["iso_alpha"])

fig_geo_map = px.choropleth(geo_map_df,
                        locations="iso_alpha",
                        color="Amount Spent in INR",
                        hover_name="Geography",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Amount Spent by Geography (Map)")
st.plotly_chart(fig_geo_map, use_container_width=True)

# --- Time Series: Amount Spent Over Time by Campaign ---
st.subheader("📅 Amount Spent Over Time by Campaign")
if 'Date' in filtered.columns:
    filtered['Date'] = pd.to_datetime(filtered['Date'])
    time_data = filtered.groupby(['Date', 'Campaign Name'])['Amount Spent in INR'].sum().reset_index()
    fig_time_series = px.line(time_data, x='Date', y='Amount Spent in INR', color='Campaign Name',
                              title="Daily Spend by Campaign")
    st.plotly_chart(fig_time_series, use_container_width=True)

# --- Top 10 Campaigns by CTR ---
st.subheader("🏆 Top 10 Campaigns by CTR")
top_ctr = filtered.groupby('Campaign Name')['Click-Through Rate (CTR in %)'].mean().nlargest(10).reset_index()
fig_top10_ctr = px.bar(top_ctr, x='Click-Through Rate (CTR in %)', y='Campaign Name', orientation='h',
                       title='Top 10 Campaigns by Average CTR', color='Click-Through Rate (CTR in %)')
st.plotly_chart(fig_top10_ctr, use_container_width=True)

# --- Impressions by Age Group ---
st.subheader("📊 Impressions by Age Group")
imp_age = filtered.groupby('Age')['Impressions'].sum().reset_index()
fig_imp_age = px.pie(imp_age, names='Age', values='Impressions', title='Impressions Distribution by Age Group')
st.plotly_chart(fig_imp_age, use_container_width=True)

# --- Bubble Chart: CPR vs CTR with Spend as Size ---
st.subheader("📌 CPR vs CTR Bubble Chart")
fig_bubble = px.scatter(filtered, x='Click-Through Rate (CTR in %)', y='Cost per Result (CPR)',
                        size='Amount Spent in INR', color='Geography', hover_name='Campaign Name',
                        title="CTR vs CPR (Bubble Size = Spend)")
st.plotly_chart(fig_bubble, use_container_width=True)

# --- Cost per Result (CPR) by Age and Geography ---
st.subheader("📊 Cost per Result (CPR) by Age and Geography")
cpr_geo_age = filtered.groupby(['Geography', 'Age'])['Cost per Result (CPR)'].mean().reset_index()
fig_cpr_geo_age = px.bar(cpr_geo_age, x='Geography', y='Cost per Result (CPR)', color='Age',
                         barmode='group', title='CPR by Age and Geography')
st.plotly_chart(fig_cpr_geo_age, use_container_width=True)

# --- Clicks vs Frequency ---
st.subheader("📍 Clicks vs Frequency")
fig_clicks_freq = px.scatter(filtered, x='Frequency', y='Clicks',
                             color='Age', hover_name='Campaign Name',
                             title='Clicks vs Frequency')
st.plotly_chart(fig_clicks_freq, use_container_width=True)

# --- Campaign Efficiency Score (CTR / CPR) ---
st.subheader("🎯 Campaign Efficiency Score (CTR / CPR)")
efficiency_df = filtered.copy()
efficiency_df['Efficiency Score'] = efficiency_df['Click-Through Rate (CTR in %)'] / efficiency_df['Cost per Result (CPR)'].replace(0, pd.NA)
efficiency_df = efficiency_df.dropna(subset=['Efficiency Score'])

efficiency_score = efficiency_df.groupby('Campaign Name')['Efficiency Score'].mean().reset_index()
fig_efficiency = px.bar(efficiency_score.sort_values(by='Efficiency Score', ascending=False),
                        x='Efficiency Score', y='Campaign Name', orientation='h',
                        title='Campaign Efficiency (CTR / CPR)')
st.plotly_chart(fig_efficiency, use_container_width=True)

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
    st.markdown(fig_to_download(fig_ctr_age, "ctr_by_age.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_geo_spend, "spend_by_geo.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_ctr_freq, "ctr_vs_frequency.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_top10_ctr, "top10_ctr.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_imp_age, "impressions_pie.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_cpr_geo_age, "cpr_by_age_geo.png"), unsafe_allow_html=True)

with col2:
    st.markdown(fig_to_download(fig_cpc_cpr, "cpc_vs_cpr.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_clicks_imps, "clicks_impressions.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_spend_click, "spend_per_click.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_geo_map, "geo_map_spend.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_bubble, "cpr_ctr_bubble.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_clicks_freq, "clicks_vs_frequency.png"), unsafe_allow_html=True)
    st.markdown(fig_to_download(fig_efficiency, "campaign_efficiency.png"), unsafe_allow_html=True)