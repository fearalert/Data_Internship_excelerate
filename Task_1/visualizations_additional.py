import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
import pycountry

from custom_layout import apply_custom_layout


def additional_visualizations(filtered: pd.DataFrame):
    # --- CPC by Age Group ---
    st.subheader("CPC by Age Group")
    ctr_data = filtered.groupby('Age')["Cost Per Click (CPC)"].mean().reset_index()
    fig_ctr_age = px.bar(ctr_data, x='Age', y='Cost Per Click (CPC)', color='Age',
                        title="CPC by Age Group", labels={'Cost Per Click (CPC)': 'CPC'},
                        text= "Cost Per Click (CPC)",
                        )
    apply_custom_layout(fig_ctr_age, xaxis_label="Age Group", yaxis_label="CPC")

    st.plotly_chart(fig_ctr_age, use_container_width=True)

    # --- CTR by Age Group ---
    st.subheader("CTR by Age Group")
    ctr_data = filtered.groupby('Age')["Click-Through Rate (CTR in %)"].mean().reset_index()
    fig_ctr_age = px.bar(ctr_data, x='Age', y='Click-Through Rate (CTR in %)', color='Age',
                        title="CTR by Age Group", labels={'Click-Through Rate (CTR in %)': 'CTR (%)'},
                        text = 'Click-Through Rate (CTR in %)',
                        )
    apply_custom_layout(fig_ctr_age, xaxis_label="Age Group", yaxis_label="CTR (%)")
 
    st.plotly_chart(fig_ctr_age, use_container_width=True)

    # --- CPC vs CPR Scatter ---
    st.subheader("CPC vs CPR")
    fig_cpc_cpr = px.scatter(filtered, x="Cost Per Click (CPC)", y="Cost per Result (CPR)",
                            color="Age", hover_data=["campaign ID"], title="CPC vs CPR")
    apply_custom_layout(fig_cpc_cpr, xaxis_label="CPC ", yaxis_label="CPR", update_trace=False)
    st.plotly_chart(fig_cpc_cpr, use_container_width=True)

    # --- Spend by Geography ---
    st.subheader("Amount Spent by Geography")
    geo_spent = filtered.groupby("Geography")["Amount Spent"].sum().reset_index()
    fig_geo_spend = px.bar(geo_spent, x="Geography", y="Amount Spent", title="Total Spend by Geography")
    apply_custom_layout(fig_geo_spend, xaxis_label="Geography", yaxis_label="Amount Spent", update_trace= False)
    st.plotly_chart(fig_geo_spend, use_container_width=True)

    # --- Clicks vs Impressions ---
    st.subheader("Clicks vs Impressions")
    clicks_imps = filtered.groupby("campaign ID")[["Clicks", "Impressions", "Unique Clicks", "Unique Link Clicks (ULC)"]].sum().reset_index()
    fig_clicks_imps = px.line(clicks_imps, x="campaign ID", y=["Clicks", "Impressions", "Unique Clicks", "Unique Link Clicks (ULC)"],
                            title="Clicks and Impressions", line_shape="linear", line_dash_sequence=["solid", "dot"],)
    apply_custom_layout(fig_clicks_imps, xaxis_label="Campaign ID", yaxis_label="Count", update_trace=False)
    st.plotly_chart(fig_clicks_imps, use_container_width=True)


    # --- Clicks vs Unique Clicks vs Unique Link Clicks ---
    st.subheader("Clicks vs Unique Clicks vs Unique Link Clicks")
    clicks_imps = filtered.groupby("campaign ID")[["Clicks", "Unique Clicks", "Unique Link Clicks (ULC)"]].sum().reset_index()
    fig_clicks_imps = px.line(clicks_imps, x="campaign ID", y=["Clicks", "Unique Clicks", "Unique Link Clicks (ULC)"],
                            title="Clicks, UC and ULC", line_shape="linear", line_dash_sequence=["solid", "dot"],)
    apply_custom_layout(fig_clicks_imps, xaxis_label="Campaign ID", yaxis_label="Count", update_trace=False)
    st.plotly_chart(fig_clicks_imps, use_container_width=True)
    # --- CTR vs Frequency ---
    st.subheader("CTR vs Frequency")
    fig_ctr_freq = px.scatter(filtered, x="Frequency", y="Click-Through Rate (CTR in %)",
                            color="Age", hover_data=["campaign ID"],
                            title="CTR vs Frequency")
    fig_ctr_freq.update_traces(texttemplate='%{y:.2f}%', textposition='top center')
    apply_custom_layout(fig_ctr_freq, xaxis_label="Frequency", yaxis_label="CTR (%)", update_trace= False)
    st.plotly_chart(fig_ctr_freq, use_container_width=True)

    # --- Spend per Click by Campaign ---
    st.subheader("Spend per Click by Campaign")
    spc_df = filtered.copy()
    spc_df['Spend per Click'] = spc_df['Amount Spent'] / spc_df['Clicks'].replace(0, pd.NA)
    spc_df = spc_df.dropna(subset=['Spend per Click'])
    fig_spend_click = px.bar(spc_df, x="campaign ID", y="Spend per Click",
                            color="campaign ID", title="Spend per Click by Campaign")
    apply_custom_layout(fig_spend_click, xaxis_label="Campaign ID", yaxis_label="Spend per Click", update_trace= False)
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
                            color="Amount Spent",
                            hover_name="Geography",
                            color_continuous_scale=px.colors.sequential.Plasma,
                            title="Amount Spent by Geography (Map)")
    fig_geo_map.update_geos(projection_type="natural earth")
    # apply_custom_layout(fig_geo_map, xaxis_label="Geography", yaxis_label="Amount Spent")
    st.plotly_chart(fig_geo_map, use_container_width=True)

    # --- Top 10 Campaigns by CTR ---
    st.subheader("🏆 Top 10 Campaigns by CTR")
    top_ctr = filtered.groupby('campaign ID')['Click-Through Rate (CTR in %)'].mean().nlargest(10).reset_index()
    fig_top10_ctr = px.bar(top_ctr, x='Click-Through Rate (CTR in %)', y='campaign ID', orientation='h',
                        title='Top 10 Campaigns by Average CTR', color='Click-Through Rate (CTR in %)')
    apply_custom_layout(fig_top10_ctr, xaxis_label="CTR (%)", yaxis_label="Campaign ID", update_trace=False)
    st.plotly_chart(fig_top10_ctr, use_container_width=True)

    # --- Impressions by Age Group ---
    st.subheader("📊 Impressions by Age Group")
    imp_age = filtered.groupby('Age')['Impressions'].sum().reset_index()
    fig_imp_age = px.pie(imp_age, names='Age', values='Impressions', title='Impressions Distribution by Age Group')
    apply_custom_layout(fig_imp_age, xaxis_label="Age Group", yaxis_label="Impressions", update_trace= False)
    st.plotly_chart(fig_imp_age, use_container_width=True)

    # --- Bubble Chart: CPR vs CTR with Spend as Size ---
    st.subheader("📌 CPR vs CTR Bubble Chart")
    fig_bubble = px.scatter(filtered, x='Click-Through Rate (CTR in %)', y='Cost per Result (CPR)',
                            size='Amount Spent', color='Geography', hover_name='campaign ID',
                            title="CTR vs CPR (Bubble Size = Spend)")
    fig_top10_ctr.update_traces(texttemplate='%{x:.2f}%', textposition='outside')
    apply_custom_layout(fig_bubble, xaxis_label="CTR (%)", yaxis_label="CPR ", update_trace=False)
    st.plotly_chart(fig_bubble, use_container_width=True)

    # --- Cost per Result (CPR) by Age and Geography ---
    st.subheader("📊 Cost per Result (CPR) by Age and Geography")
    cpr_geo_age = filtered.groupby(['Geography', 'Age'])['Cost per Result (CPR)'].mean().reset_index()
    fig_cpr_geo_age = px.bar(cpr_geo_age, x='Geography', y='Cost per Result (CPR)', color='Age',
                            barmode='group', title='CPR by Age and Geography')
    apply_custom_layout(fig_cpr_geo_age, xaxis_label="Geography", yaxis_label="CPR ", update_trace=False)
    st.plotly_chart(fig_cpr_geo_age, use_container_width=True)

    # --- Clicks vs Frequency ---
    st.subheader("📍 Clicks vs Frequency")
    fig_clicks_freq = px.scatter(filtered, x='Frequency', y='Clicks',
                                color='Age', hover_name='campaign ID',
                                title='Clicks vs Frequency')
    fig_clicks_freq.update_traces(texttemplate='%{y}', textposition='top center')
    apply_custom_layout(fig_clicks_freq, xaxis_label="Frequency", yaxis_label="Clicks", update_trace=False)
    st.plotly_chart(fig_clicks_freq, use_container_width=True)