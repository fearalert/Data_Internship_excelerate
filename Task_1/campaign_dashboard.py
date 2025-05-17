import streamlit as st
import pandas as pd
import plotly.express as px

from visualizations_additional import additional_visualizations
from load_data import load_data
from custom_layout import apply_custom_layout

# --- Page Configuration ---
st.set_page_config(page_title="Campaign Performance Analyzer", layout="wide")

try:
    df = load_data()
    
    # Print column names to debug
    st.sidebar.text("Available columns:")
    st.sidebar.text(df.columns.tolist())
    
    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filter Options")
    campaign_ids = sorted(df['campaign ID'].unique())
    selected_campaigns = st.sidebar.multiselect("Campaign", campaign_ids, default=campaign_ids)
    
    audiences = sorted(df['Audience'].unique())
    selected_audiences = st.sidebar.multiselect("Audience", audiences, default=audiences)
    
    age_groups = sorted(df['Age'].unique())
    selected_age_groups = st.sidebar.multiselect("Age Group", age_groups, default=age_groups)

    geos = st.sidebar.multiselect("Geography", df['Geography'].unique(), default=df['Geography'].unique())

    # Filter data based on selections
    filtered_df = df[(df['campaign ID'].isin(selected_campaigns)) & 
                     (df['Audience'].isin(selected_audiences)) & 
                     (df['Age'].isin(selected_age_groups)) &
                     (df['Geography'].isin(geos))]    
    
    # --- Main Dashboard ---
    st.title("🎯 Campaign Performance Analysis")
    st.write("Use this dashboard to analyze market data performance of globalshala and identify which campaigns to optimize or discontinue.")
    
    # --- Overall KPIs ---
    st.header("📊 Overall Campaign Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_spent = filtered_df['Amount Spent'].sum()
        st.metric("Total Spend", f"${total_spent:,.2f}")
    
    with col2:
        avg_ctr = filtered_df['Click-Through Rate (CTR in %)'].mean()
        st.metric("Average CTR", f"{avg_ctr:.2f}%")
    
    with col3:
        avg_cpc = filtered_df['Cost Per Click (CPC)'].mean()
        st.metric("Average CPC", f"${avg_cpc:.2f}")
    
    with col4:
        avg_cpm = filtered_df['CPM'].mean()
        st.metric("Average CPM", f"${avg_cpm:.2f}")
        
    # --- Campaign Performance Analysis ---
    st.header("🔍 Campaign Performance Analysis")
    
    # --- Campaign Efficiency Score (higher is better) ---
    st.subheader("Campaign Efficiency Score (CTR / CPR)")
    
    # Aggregate by campaign
    campaign_efficiency = filtered_df.groupby('campaign ID').agg({
        'Click-Through Rate (CTR in %)': 'mean',
        'Cost Per Click (CPC)': 'mean',
        'Cost per Result (CPR)': 'mean',
        'Efficiency Score': 'mean',
        'Amount Spent': 'sum',
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Unique Link Clicks (ULC)': 'sum',
        'ROI Score': 'mean',
        'CPM': 'mean'
    }).reset_index()
    
    # Sort by efficiency score (ascending to show worst performers first)
    campaign_efficiency = campaign_efficiency.sort_values('Efficiency Score')
    
    # Create bar chart for efficiency
    fig_efficiency = px.bar(
        campaign_efficiency,
        x='campaign ID', 
        y='Efficiency Score',
        color='Efficiency Score',
        color_continuous_scale='RdYlGn',  # Red (bad) to Yellow to Green (good)
        title='Campaign Efficiency Scores: (CTR / CPR) - (Lower efficiency score shows low performance)',
        hover_data=['Amount Spent', 'Click-Through Rate (CTR in %)', 'Cost per Result (CPR)']
        text = 'Efficiency Score'
    )

    # Update layout
    apply_custom_layout(fig_efficiency, xaxis_label="campaign ID", yaxis_label="Efficiency Score")
    
    fig_efficiency.update_traces(
    texttemplate='%{text:.2f}',
    textposition='inside',
    insidetextanchor='middle'
    )

    fig_efficiency.update_layout(
    yaxis_title="Efficiency Score",
    xaxis_title="Campaign ID",
    uniformtext_minsize=8,
    uniformtext_mode='show'
    )
    
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # --- ROI Analysis ---
    st.subheader("Return on Investment Analysis (ULC / Spend)")
    
    fig_roi = px.bar(
        campaign_efficiency.sort_values('ROI Score'),
        x='campaign ID', 
        y='ROI Score',
        color='ROI Score',
        color_continuous_scale='RdYlGn',  # Red (bad) to Yellow to Green (good)
        title='Campaign ROI Scores: (ULC / Spend) - (Lower ROI Score shows low performance)',
        hover_data=['Amount Spent', 'Unique Link Clicks (ULC)', 'Cost per Result (CPR)']
    )

    # Update layout
    apply_custom_layout(fig_roi, xaxis_label="campaign ID", yaxis_label="ROI Score")
    
    st.plotly_chart(fig_roi, use_container_width=True)
    
    # --- Cost Analysis ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cost per Click (CPC) Analysis")
        fig_cpc = px.bar(
            campaign_efficiency.sort_values('Cost Per Click (CPC)', ascending=False),
            x='campaign ID', 
            y='Cost Per Click (CPC)',
            color='Cost Per Click (CPC)',
            color_continuous_scale='RdYlGn_r',  # Green (good) to Red (bad)
            title='Cost per Click by Campaign - (Higher CPC values Shows low performance)',
            hover_data=['Amount Spent', 'Clicks']
        )
        apply_custom_layout(fig_cpc, xaxis_label="campaign ID", yaxis_label="Cost Per Click (CPC)")
        st.plotly_chart(fig_cpc, use_container_width=True)
    
    with col2:
        st.subheader("Cost per Result (CPR) Analysis")
        fig_cpr = px.bar(
            campaign_efficiency.sort_values('Cost per Result (CPR)', ascending=False),
            x='campaign ID', 
            y='Cost per Result (CPR)',
            color='Cost per Result (CPR)',
            color_continuous_scale='RdYlGn_r',  # Green (good) to Red (bad)
            title='Cost per Result by Campaign - (Higher CRC values Shows low performance)',
            hover_data=['Amount Spent', 'Unique Link Clicks (ULC)']
        )

        # Update layout
        apply_custom_layout(fig_cpr, xaxis_label="campaign ID", yaxis_label="Cost per Result (CPR)")

        st.plotly_chart(fig_cpr, use_container_width=True)
    
    # --- Performance vs Spend Analysis ---
    st.subheader("Performance vs Spend Analysis")
    
    fig_bubble = px.scatter(
        campaign_efficiency,
        x='Click-Through Rate (CTR in %)', 
        y='Cost per Result (CPR)',
        size='Amount Spent',
        color='ROI Score',
        hover_name='campaign ID',
        text='campaign ID',
        color_continuous_scale='RdYlGn',
        title='Performance vs Cost (Bubble Size = Total Spend)',
        labels={'Click-Through Rate (CTR in %)': 'CTR (%)', 'Cost per Result (CPR)': 'CPR ($)'}
    )
    apply_custom_layout(fig_bubble, xaxis_label="Click-Through Rate (CTR in %)", yaxis_label="Cost per Result (CPR)")

    # Add quadrant lines to identify high cost, low performance campaigns
    avg_ctr = campaign_efficiency['Click-Through Rate (CTR in %)'].mean()
    avg_cpr = campaign_efficiency['Cost per Result (CPR)'].mean()
    
    fig_bubble.add_shape(
        type='line', line=dict(dash='dash', width=1),
        x0=avg_ctr, y0=0, x1=avg_ctr, y1=campaign_efficiency['Cost per Result (CPR)'].max()*1.1
    )
    fig_bubble.add_shape(
        type='line', line=dict(dash='dash', width=1),
        x0=0, y0=avg_cpr, x1=campaign_efficiency['Click-Through Rate (CTR in %)'].max()*1.1, y1=avg_cpr
    )
    
    # Add quadrant labels
    fig_bubble.add_annotation(
        x=avg_ctr/2, y=avg_cpr/2,
        text="Low CTR, Low CPR",
        showarrow=False
    )
    fig_bubble.add_annotation(
        x=avg_ctr*1.5, y=avg_cpr/2,
        text="High CTR, Low CPR (Best)",
        showarrow=False
    )
    fig_bubble.add_annotation(
        x=avg_ctr/2, y=avg_cpr*1.5,
        text="Low CTR, High CPR (Worst)",
        showarrow=False,
        font=dict(color="red")
    )
    fig_bubble.add_annotation(
        x=avg_ctr*1.5, y=avg_cpr*1.5,
        text="High CTR, High CPR",
        showarrow=False
    )
    
    st.plotly_chart(fig_bubble, use_container_width=True)
    
    # --- Campaign to Discontinue Recommendation ---
    st.header("🚫 Campaign Discontinuation Recommendation")
    
    # Calculate a composite score for each campaign
    # Lower scores are worse performing campaigns
    campaign_efficiency['Composite Score'] = (
        (campaign_efficiency['Efficiency Score'] / campaign_efficiency['Efficiency Score'].max()) * 0.4 +
        (campaign_efficiency['ROI Score'] / campaign_efficiency['ROI Score'].max()) * 0.4 +
        (1 - (campaign_efficiency['Cost per Result (CPR)'] / campaign_efficiency['Cost per Result (CPR)'].max())) * 0.2
    )
    
    # Get the worst performing campaign
    worst_campaign = campaign_efficiency.sort_values('Composite Score').iloc[0]
    
    st.subheader(f"Recommended Campaign to Discontinue: {worst_campaign['campaign ID']}")
    
    # Create a metrics explanation card
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("Performance Metrics for this Campaign")
        st.write(f"Efficiency Score: {worst_campaign['Efficiency Score']:.4f}")
        st.write(f"ROI Score: {worst_campaign['ROI Score']:.4f}")
        st.write(f"CTR: {worst_campaign['Click-Through Rate (CTR in %)']:.2f}%")
        st.write(f"CPR: ${worst_campaign['Cost per Result (CPR)']:.2f}")
        st.write(f"CPC: ${worst_campaign['Cost Per Click (CPC)']:.2f}")
        st.write(f"Total Spend: ${worst_campaign['Amount Spent']:.2f}")
        st.write(f"Impressions: {worst_campaign['Impressions']:,}")
        st.write(f"Clicks: {worst_campaign['Clicks']:,}")
        st.write(f"Unique Link Clicks: {worst_campaign['Unique Link Clicks (ULC)']:,}")
    
    with col2:
        st.warning("Recommendation Reasoning")
        st.write("""
        This campaign has been identified as the worst performer based on a composite score that considers:
        
        1. **Efficiency Score** (CTR/CPR) - How well the campaign converts views to clicks relative to cost
        2. **ROI Score** (ULC/Spend) - Return on investment in terms of valuable user actions
        3. **Cost per Result** - The cost efficiency of achieving the desired outcome
        
        The low composite score indicates poor performance across these key metrics,
        suggesting budget could be better allocated to higher-performing campaigns.
        """)
                
    # --- Reach & Impressions Line Chart ---
    st.header("📈 Reach and Impressions Analysis")

        # Ensure Age groups are sorted consistently
    all_age_groups = sorted(filtered_df['Age'].dropna().unique())

    # Group and pivot for consistent age groups across campaigns
    reach_impressions_df = (
            filtered_df
            .groupby(['campaign ID', 'Age'])[['Reach', 'Impressions']]
            .sum()
            .reset_index()
        )

    # Add missing age groups for each campaign with 0 values
    campaign_age_grid = pd.MultiIndex.from_product(
            [reach_impressions_df['campaign ID'].unique(), all_age_groups],
            names=["campaign ID", "Age"]
        )
    reach_impressions_df = (
            reach_impressions_df
            .set_index(['campaign ID', 'Age'])
            .reindex(campaign_age_grid, fill_value=0)
            .reset_index()
        )

    # Dropdown to select campaign
    selected_line_campaign = st.selectbox("Select Campaign for Reach & Impressions Trend", sorted(filtered_df['campaign ID'].unique()))
    line_data = reach_impressions_df[reach_impressions_df['campaign ID'] == selected_line_campaign]

    fig_line = px.line(
            line_data,
            x='Age',
            y=['Reach', 'Impressions'],
            markers=True,
            title=f"Reach and Impressions by Age Group for Campaign ID:  {selected_line_campaign}",
            labels={'value': 'Count', 'Age': 'Age Group', 'variable': 'Metric'}
        )

    # Emphasis: annotate highest Reach point
    max_reach = line_data.loc[line_data['Reach'].idxmax()]
    fig_line.add_annotation(
            x=max_reach['Age'], y=max_reach['Reach'],
            text=f"🔺 Max Reach: {int(max_reach['Reach']):,}",
            showarrow=True, arrowhead=2, arrowcolor="green",
            font=dict(color="green", size=12), bgcolor="white"
        )

    # Emphasis: annotate highest Impressions point
    max_impressions = line_data.loc[line_data['Impressions'].idxmax()]
    fig_line.add_annotation(
            x=max_impressions['Age'], y=max_impressions['Impressions'],
            text=f"🔵 Max Impressions: {int(max_impressions['Impressions']):,}",
            showarrow=True, arrowhead=2, arrowcolor="blue",
            font=dict(color="blue", size=12), bgcolor="white"
    )

    apply_custom_layout(fig_line, xaxis_label="Age Group", yaxis_label="Count")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- Spend Distribution by Geography ---
    st.header("🌍 Spend Distribution by Geography")

    spend_geo = filtered_df.groupby('Geography')['Amount Spent'].sum().reset_index()

    if len(spend_geo) <= 5:
            fig_geo = px.pie(
                spend_geo,
                values='Amount Spent',
                names='Geography',
                title="Spend Distribution Across Geographies",
                hole=0.4
            )
            fig_geo.update_traces(textposition='inside', textinfo='percent+label')
    else:
            fig_geo = px.bar(
                spend_geo,
                x='Geography',
                y='Amount Spent',
                title="Spend Distribution Across Geographies",
                color='Amount Spent',
                color_continuous_scale='Oranges',
                labels={'Amount Spent': 'Amount ($)', 'Geography': 'Region'}
            )

    apply_custom_layout(fig_geo, xaxis_label="Geography", yaxis_label="Amount Spent")
    st.plotly_chart(fig_geo, use_container_width=True)

    # --- Spend Distribution by Geography (Map) ---
    st.header("🗺️ Spend Distribution by Geography (Map View)")

    # Aggregate spend by geography
    spend_geo = filtered_df.groupby('Geography')['Amount Spent'].sum().reset_index()

    # Choropleth map visualization
    fig_geo_map = px.choropleth(
        spend_geo,
        locations='Geography',
        locationmode='country names',
        color='Amount Spent',
        color_continuous_scale='Oranges',
        title='💸 Global Spend Distribution by Country',
        labels={'Amount Spent': 'Amount ($)', 'Geography': 'Country'},
        hover_name='Geography'
    )

    fig_geo_map.update_geos(showframe=False, showcoastlines=False)
    apply_custom_layout(fig_geo_map)
    st.plotly_chart(fig_geo_map, use_container_width=True)


    # --- Clicks by Audience ---
    st.header("🧑‍🤝‍🧑 Clicks by Audience")

    clicks_audience = filtered_df.groupby('Audience')['Clicks'].sum().reset_index()

    fig_clicks = px.bar(
            clicks_audience,
            x='Audience',
            y='Clicks',
            color='Clicks',
            color_continuous_scale='Blues',
            title="Total Clicks by Audience Group",
            labels={'Clicks': 'Number of Clicks', 'Audience': 'Audience Group'}
        )

    apply_custom_layout(fig_clicks, xaxis_label="Audience Group", yaxis_label="Clicks")
    st.plotly_chart(fig_clicks, use_container_width=True)

            
    # --- Detailed Campaign Analysis ---
    st.header("📈 Detailed Campaign Analysis")
    
    # Select a campaign for detailed analysis
    selected_campaign = st.selectbox("Select Campaign for Detailed Analysis", df['campaign ID'].unique())
    
    campaign_data = df[df['campaign ID'] == selected_campaign]
    
    # Display campaign details
    st.subheader(f"Details for {selected_campaign}")
    
    # Age group analysis
    age_performance = campaign_data.groupby('Age').agg({
        'Click-Through Rate (CTR in %)': 'mean',
        'Cost Per Click (CPC)': 'mean',
        'Cost per Result (CPR)': 'mean',
        'Efficiency Score': 'mean',
        'Amount Spent': 'sum',
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Unique Link Clicks (ULC)': 'sum'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_age_ctr = px.bar(
            age_performance,
            x='Age', 
            y='Click-Through Rate (CTR in %)',
            color='Click-Through Rate (CTR in %)',
            title=f'CTR by Age Group for {selected_campaign}'
        )

        apply_custom_layout(fig_age_ctr, xaxis_label="Age Group", yaxis_label="CTR (%)")
        st.plotly_chart(fig_age_ctr, use_container_width=True)
    
    with col2:
        fig_age_cpr = px.bar(
            age_performance,
            x='Age', 
            y='Cost per Result (CPR)',
            color='Cost per Result (CPR)',
            color_continuous_scale='RdYlGn_r',
            title=f'CPR by Age Group for {selected_campaign}'
        )
        apply_custom_layout(fig_age_cpr, xaxis_label="Age Group", yaxis_label="Cost per Result (CPR)")
        st.plotly_chart(fig_age_cpr, use_container_width=True)
    
    # Geography analysis
    if 'Geography' in campaign_data.columns:
        geo_performance = campaign_data.groupby('Geography').agg({
            'Click-Through Rate (CTR in %)': 'mean',
            'Cost Per Click (CPC)': 'mean',
            'Cost per Result (CPR)': 'mean',
            'Efficiency Score': 'mean',
            'Amount Spent': 'sum',
            'Impressions': 'sum',
            'Clicks': 'sum',
            'Unique Link Clicks (ULC)': 'sum'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_geo_ctr = px.bar(
                geo_performance,
                x='Geography', 
                y='Click-Through Rate (CTR in %)',
                color='Click-Through Rate (CTR in %)',
                title=f'CTR by Geography for {selected_campaign}'
            )
            apply_custom_layout(fig_geo_ctr, xaxis_label="Geography", yaxis_label="CTR (%)")
            st.plotly_chart(fig_geo_ctr, use_container_width=True)
        
        with col2:
            fig_geo_cpr = px.bar(
                geo_performance,
                x='Geography', 
                y='Cost per Result (CPR)',
                color='Cost per Result (CPR)',
                color_continuous_scale='RdYlGn_r',
                title=f'CPR by Geography for {selected_campaign}'
            )
            apply_custom_layout(fig_geo_cpr, xaxis_label="Geography", yaxis_label="Cost per Result (CPR)")
            st.plotly_chart(fig_geo_cpr, use_container_width=True)
    

    # --- Age Distribution by Campaign ---
    st.header("🎯 Age Distribution by Campaign")

    # Select campaign for visualization
    selected_age_campaign = st.selectbox("Select Campaign for Age Distribution", sorted(filtered_df['campaign ID'].unique()))

    # Filter data
    age_dist_df = (
        filtered_df[filtered_df['campaign ID'] == selected_age_campaign]
        .groupby('Age')[['Reach', 'Impressions', 'Clicks']]
        .sum()
        .reset_index()
        .sort_values(by='Age')
    )
    # Bar chart for Reach, Impressions, Clicks
    fig_age_dist = px.bar(
        age_dist_df,
        x='Age',
        y=['Reach', 'Impressions', 'Clicks'],
        barmode='group',
        title=f"Distribution of Reach, Impressions & Clicks by Age for Campaign {selected_age_campaign}",
        labels={'value': 'Count', 'Age': 'Age Group', 'variable': 'Metric'}
    )

    apply_custom_layout(fig_age_dist, xaxis_label="Age Group", yaxis_label="Count")
    st.plotly_chart(fig_age_dist, use_container_width=True)

    st.subheader("🎯 Comparision of Age Distribution by Campaign")
    st.write("This section compares the reach of different campaigns across various age groups.")
    # Compare multiple campaigns
    age_compare_df = (
        filtered_df
        .groupby(['campaign ID', 'Age'])[['Reach']]
        .sum()
        .reset_index()
    )

    fig_compare = px.bar(
        age_compare_df,
        x='Age',
        y='Reach',
        color='campaign ID',
        barmode='group',
        title="Reach by Age Group Across Campaigns",
        labels={'Reach': 'Reach Count', 'Age': 'Age Group', 'campaign ID': 'Campaign'}
    )

    apply_custom_layout(fig_compare, xaxis_label="Age Group", yaxis_label="Reach")
    st.plotly_chart(fig_compare, use_container_width=True)


    
    # --- Comparative Analysis ---
    st.header("🔍 Campaign Comparative Analysis")
    
    # Get campaign options for comparison
    campaign_options = df['campaign ID'].unique()
    
    col1, col2 = st.columns(2)
    with col1:
        campaign1 = st.selectbox("Select First Campaign", campaign_options, index=0)
    with col2:
        campaign2 = st.selectbox("Select Second Campaign", campaign_options, index=min(1, len(campaign_options)-1))
    
    campaign1_data = df[df['campaign ID'] == campaign1]
    campaign2_data = df[df['campaign ID'] == campaign2]
    
    # Calculate aggregates for comparison
    campaign1_agg = campaign1_data.agg({
        'Click-Through Rate (CTR in %)': 'mean',
        'Cost Per Click (CPC)': 'mean',
        'Cost per Result (CPR)': 'mean',
        'Efficiency Score': 'mean',
        'ROI Score': 'mean',
        'Amount Spent': 'sum',
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Unique Link Clicks (ULC)': 'sum'
    }).to_dict()
    
    campaign2_agg = campaign2_data.agg({
        'Click-Through Rate (CTR in %)': 'mean',
        'Cost Per Click (CPC)': 'mean',
        'Cost per Result (CPR)': 'mean',
        'Efficiency Score': 'mean',
        'ROI Score': 'mean',
        'Amount Spent': 'sum',
        'Impressions': 'sum',
        'Clicks': 'sum',
        'Unique Link Clicks (ULC)': 'sum'
    }).to_dict()
    
    # Create comparison table
    comparison_data = {
        'Metric': [
            'Click-Through Rate (CTR in %)',
            'Cost Per Click (CPC)',
            'Cost per Result (CPR)',
            'Efficiency Score',
            'ROI Score',
            'Total Spend',
            'Impressions',
            'Clicks',
            'Unique Link Clicks'
        ],
        campaign1: [
            f"{campaign1_agg['Click-Through Rate (CTR in %)']:.2f}%",
            f"${campaign1_agg['Cost Per Click (CPC)']:.2f}",
            f"${campaign1_agg['Cost per Result (CPR)']:.2f}",
            f"{campaign1_agg['Efficiency Score']:.4f}",
            f"{campaign1_agg['ROI Score']:.4f}",
            f"${campaign1_agg['Amount Spent']:.2f}",
            f"{campaign1_agg['Impressions']:,}",
            f"{campaign1_agg['Clicks']:,}",
            f"{campaign1_agg['Unique Link Clicks (ULC)']:,}"
        ],
        campaign2: [
            f"{campaign2_agg['Click-Through Rate (CTR in %)']:.2f}%",
            f"${campaign2_agg['Cost Per Click (CPC)']:.2f}",
            f"${campaign2_agg['Cost per Result (CPR)']:.2f}",
            f"{campaign2_agg['Efficiency Score']:.4f}",
            f"{campaign2_agg['ROI Score']:.4f}",
            f"${campaign2_agg['Amount Spent']:.2f}",
            f"{campaign2_agg['Impressions']:,}",
            f"{campaign2_agg['Clicks']:,}",
            f"{campaign2_agg['Unique Link Clicks (ULC)']:,}"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.dataframe(comparison_df)
    
    # --- Campaign Performance Table ---
    st.header("📋 Campaign Performance Summary")
    
    # Create a summary table
    summary_table = campaign_efficiency.sort_values('Composite Score')[
        ['campaign ID', 'Click-Through Rate (CTR in %)', 'Cost Per Click (CPC)', 'Cost per Result (CPR)', 
         'ROI Score', 'Efficiency Score', 'Amount Spent', 'Composite Score']
    ]
    
    # Rename columns for clarity
    summary_table = summary_table.rename(columns={
        'campaign ID': 'Campaign',
        'Click-Through Rate (CTR in %)': 'CTR (%)',
        'Cost Per Click (CPC)': 'CPC ($)',
        'Cost per Result (CPR)': 'CPR ($)',
        'ROI Score': 'ROI',
        'Efficiency Score': 'Efficiency',
        'Amount Spent': 'Spend ($)',
        'Composite Score': 'Performance Score'
    })
    
    # Format the table
    st.dataframe(summary_table.style.format({
        'CTR (%)': '{:.2f}',
        'CPC ($)': '${:.2f}',
        'CPR ($)': '${:.2f}',
        'ROI': '{:.4f}',
        'Efficiency': '{:.4f}',
        'Spend ($)': '${:.2f}',
        'Performance Score': '{:.4f}'
    }).background_gradient(subset=['Performance Score'], cmap='RdYlGn'))

   # --- Campaign Performance Visualization ---
    st.subheader("📊 Visual Campaign Performance Comparison")

    fig_perf = px.bar(
        summary_table.sort_values('Performance Score', ascending=True),  # ascending for horizontal bars
        x='Performance Score',
        y='Campaign',
        orientation='h',
        color='Performance Score',
        color_continuous_scale='RdYlGn',
        title="Campaigns Ranked by Performance Score",
        labels={'Performance Score': 'Score', 'Campaign': 'Campaign ID'},
        text='Performance Score'
    )

    fig_perf.update_traces(
        texttemplate='%{text:.4f}',
        textposition='outside'
    )

    fig_perf.update_layout(
        xaxis_title="Performance Score",
        yaxis_title="Campaign",
        margin=dict(l=100, r=40, t=60, b=40),
        height=500
    )
    apply_custom_layout(fig_perf, xaxis_label="Performance Score", yaxis_label="Campaign ID")
    st.plotly_chart(fig_perf, use_container_width=True)

    # Basic_additional_visuals
    st.subheader("📊 Additional Visualizations")
    st.write("Explore additional visualizations to gain deeper insights into campaign performance.")
    
    additional_visualizations(filtered_df)
 
    st.markdown("---")
    st.caption("Campaign Analysis Tool - Prioritize campaigns with higher Performance Scores")

except Exception as e:
    st.error(f"An error occurred: {e}")
    st.write("Please ensure the data file is in the correct format and located in the same directory as this script.")
    if 'df' in locals():
        st.write("Available columns:", df.columns.tolist())