"""
Step 6: Interactive Streamlit Dashboard
=======================================

This script creates an interactive dashboard for exploring French real estate data.
Perfect for showcasing your data analysis skills on Malt.fr!

Run with: streamlit run 06_dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Directories
DATA_DIR = Path("data")


@st.cache_data
def load_data():
    """Load and cache the cleaned data."""
    clean_files = list(DATA_DIR.glob("*_clean.csv*"))
    
    if not clean_files:
        st.error("❌ No cleaned data files found!")
        st.info("Please run the data cleaning script first: `python 03_data_cleaning.py`")
        st.stop()
    
    clean_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    data_file = clean_files[0]
    
    dtype_map = {
        'code_commune': str,
        'code_postal': str,
        'type_local': 'category',
        'nature_mutation': 'category',
    }
    
    df = pd.read_csv(
        data_file,
        sep=',',
        dtype=dtype_map,
        parse_dates=['date_mutation'],
        low_memory=False
    )
    
    # Add time columns
    df['year'] = df['date_mutation'].dt.year
    df['month'] = df['date_mutation'].dt.month
    df['month_name'] = df['date_mutation'].dt.strftime('%B')
    
    return df


def create_header():
    """Create dashboard header."""
    
    st.set_page_config(
        page_title="French Real Estate Analysis",
        page_icon="🏠",
        layout="wide"
    )
    
    st.title("🏠 French Real Estate Market Analysis")
    st.markdown("""
    **Interactive Dashboard** — 5 grandes métropoles françaises (Paris, Marseille, Lyon, Toulouse, Nantes), 2021-2024.
    Données : DVF (data.gouv.fr) · 557k transactions nettoyées · Licence Ouverte 2.0.

    *Projet portfolio pour profil Malt.fr — Data Analyst / Data Scientist.*
    """)
    
    st.divider()


def create_sidebar_filters(df):
    """Create sidebar filters."""
    
    st.sidebar.header("🔍 Filters")
    
    # Property type filter
    property_types = df['type_local'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Property Type",
        options=property_types,
        default=property_types
    )
    
    # Year filter
    years = sorted(df['year'].unique())
    if len(years) > 1:
        selected_years = st.sidebar.slider(
            "Year Range",
            min_value=int(min(years)),
            max_value=int(max(years)),
            value=(int(min(years)), int(max(years)))
        )
    else:
        st.sidebar.info(f"📅 Data year: {years[0]}")
        selected_years = (years[0], years[0])
    
    # Price range filter
    p_min, p_max = int(df['prix_m2'].min()), int(df['prix_m2'].max())
    if p_min < p_max:
        price_min, price_max = st.sidebar.slider(
            "Price per m² Range (€)",
            min_value=p_min,
            max_value=p_max,
            value=(int(df['prix_m2'].quantile(0.05)), int(df['prix_m2'].quantile(0.95)))
        )
    else:
        price_min, price_max = p_min, p_max
    
    # Surface area filter
    s_min, s_max = int(df['surface_reelle_bati'].min()), int(df['surface_reelle_bati'].max())
    if s_min < s_max:
        surface_min, surface_max = st.sidebar.slider(
            "Surface Area Range (m²)",
            min_value=s_min,
            max_value=s_max,
            value=(int(df['surface_reelle_bati'].quantile(0.05)),
                   int(df['surface_reelle_bati'].quantile(0.95)))
        )
    else:
        surface_min, surface_max = s_min, s_max
    
    # Apply filters
    filtered_df = df[
        (df['type_local'].isin(selected_types)) &
        (df['year'] >= selected_years[0]) &
        (df['year'] <= selected_years[1]) &
        (df['prix_m2'] >= price_min) &
        (df['prix_m2'] <= price_max) &
        (df['surface_reelle_bati'] >= surface_min) &
        (df['surface_reelle_bati'] <= surface_max)
    ]
    
    return filtered_df


def display_kpi_metrics(df):
    """Display key performance indicators."""
    
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_transactions = len(df)
        st.metric("Total Transactions", f"{total_transactions:,}")
    
    with col2:
        avg_price = df['prix_m2'].mean()
        st.metric("Average Price/m²", f"{avg_price:,.0f} €")
    
    with col3:
        median_price = df['prix_m2'].median()
        st.metric("Median Price/m²", f"{median_price:,.0f} €")
    
    with col4:
        avg_surface = df['surface_reelle_bati'].mean()
        st.metric("Average Surface", f"{avg_surface:.1f} m²")
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        unique_communes = df['code_commune'].nunique()
        st.metric("Unique Communes", f"{unique_communes:,}")
    
    with col6:
        price_growth = df.groupby('year')['prix_m2'].median().pct_change().mean() * 100
        st.metric("Avg Annual Growth", f"{price_growth:+.1f}%")
    
    with col7:
        apartments_pct = (df['type_local'] == 'Appartement').mean() * 100
        st.metric("Apartments", f"{apartments_pct:.1f}%")
    
    with col8:
        houses_pct = (df['type_local'] == 'Maison').mean() * 100
        st.metric("Houses", f"{houses_pct:.1f}%")


def create_price_evolution_chart(df):
    """Create interactive price evolution chart."""
    
    st.header("📈 Price Evolution Over Time")
    
    # Calculate yearly stats
    yearly_stats = df.groupby(['year', 'type_local']).agg(
        prix_m2_median=('prix_m2', 'median'),
        nb_transactions=('prix_m2', 'count')
    ).reset_index()
    
    # Create line chart
    fig = px.line(
        yearly_stats,
        x='year',
        y='prix_m2_median',
        color='type_local',
        title='Price per m² Evolution by Property Type',
        labels={'prix_m2_median': 'Price per m² (€)', 'year': 'Year'},
        markers=True
    )
    
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Price per m² (€)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Transaction volume chart
    yearly_volume = df.groupby('year').size().reset_index(name='count')
    
    fig_volume = px.bar(
        yearly_volume,
        x='year',
        y='count',
        title='Transaction Volume by Year',
        labels={'count': 'Number of Transactions', 'year': 'Year'}
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)


def create_geographic_analysis(df):
    """Create geographic analysis section."""
    
    st.header("🌍 Geographic Analysis")
    
    # Top communes by price
    st.subheader("Top 20 Most Expensive Communes")
    
    commune_stats = df.groupby('code_commune').agg(
        prix_m2_median=('prix_m2', 'median'),
        nb_transactions=('prix_m2', 'count'),
        surface_median=('surface_reelle_bati', 'median')
    ).reset_index()
    
    # Filter for communes with enough transactions
    commune_stats = commune_stats[commune_stats['nb_transactions'] >= 10]
    top_communes = commune_stats.nlargest(20, 'prix_m2_median')
    
    fig = px.bar(
        top_communes,
        x='code_commune',
        y='prix_m2_median',
        title='Top 20 Communes by Median Price per m²',
        labels={'prix_m2_median': 'Price per m² (€)', 'code_commune': 'Commune Code'},
        color='prix_m2_median',
        color_continuous_scale='YlOrRd'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Geographic scatter plot
    if 'longitude' in df.columns and 'latitude' in df.columns:
        st.subheader("Geographic Price Distribution")
        
        # Sample for performance
        sample_size = min(5000, len(df))
        df_sample = df.sample(n=sample_size, random_state=42)
        
        fig = px.scatter_mapbox(
            df_sample,
            lat='latitude',
            lon='longitude',
            color='prix_m2',
            size='surface_reelle_bati',
            color_continuous_scale='YlOrRd',
            mapbox_style='open-street-map',
            zoom=5,
            title='Property Prices Across France',
            labels={'prix_m2': 'Price per m² (€)'}
        )
        
        st.plotly_chart(fig, use_container_width=True)


def create_property_type_analysis(df):
    """Create property type analysis section."""
    
    st.header("🏠 Property Type Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price comparison
        type_stats = df.groupby('type_local').agg(
            prix_m2_median=('prix_m2', 'median'),
            nb_transactions=('prix_m2', 'count')
        ).reset_index()
        
        fig = px.bar(
            type_stats,
            x='type_local',
            y='prix_m2_median',
            title='Median Price by Property Type',
            labels={'prix_m2_median': 'Price per m² (€)', 'type_local': 'Property Type'},
            color='type_local'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Transaction distribution
        fig = px.pie(
            type_stats,
            values='nb_transactions',
            names='type_local',
            title='Transaction Distribution by Type'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Price distribution
    st.subheader("Price Distribution by Property Type")
    
    fig = px.histogram(
        df,
        x='prix_m2',
        color='type_local',
        nbins=50,
        title='Price Distribution by Property Type',
        labels={'prix_m2': 'Price per m² (€)'},
        barmode='overlay'
    )
    
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)


def create_seasonal_analysis(df):
    """Create seasonal analysis section."""
    
    st.header("📅 Seasonal Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly prices
        monthly_stats = df.groupby('month').agg(
            prix_m2_median=('prix_m2', 'median'),
            nb_transactions=('prix_m2', 'count')
        ).reset_index()
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_stats['month_name'] = monthly_stats['month'].apply(lambda x: month_names[x-1])
        
        fig = px.line(
            monthly_stats,
            x='month_name',
            y='prix_m2_median',
            title='Seasonal Price Variations',
            labels={'prix_m2_median': 'Price per m² (€)', 'month_name': 'Month'},
            markers=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly volume
        fig = px.bar(
            monthly_stats,
            x='month_name',
            y='nb_transactions',
            title='Monthly Transaction Volume',
            labels={'nb_transactions': 'Number of Transactions', 'month_name': 'Month'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal insights
    st.subheader("💡 Seasonal Insights")
    
    cheapest_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmin()]
    most_expensive_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmax()]
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.info(f"""
        **Best Month to Buy:** {cheapest_month['month_name']}
        - Price: {cheapest_month['prix_m2_median']:,.0f} €/m²
        - Transactions: {cheapest_month['nb_transactions']:,}
        """)
    
    with col4:
        st.success(f"""
        **Best Month to Sell:** {most_expensive_month['month_name']}
        - Price: {most_expensive_month['prix_m2_median']:,.0f} €/m²
        - Transactions: {most_expensive_month['nb_transactions']:,}
        """)


def create_market_segments(df):
    """Create market segments analysis."""
    
    st.header("📊 Market Segments")
    
    # Create price segments
    df['price_segment'] = pd.cut(
        df['prix_m2'],
        bins=[0, 2000, 4000, 6000, 8000, float('inf')],
        labels=['Budget (<2K€/m²)', 'Mid-Range (2-4K€/m²)', 
                'Premium (4-6K€/m²)', 'Luxury (6-8K€/m²)', 
                'Ultra-Luxury (>8K€/m²)']
    )
    
    # Segment statistics
    segment_stats = df.groupby('price_segment', observed=True).agg(
        nb_transactions=('prix_m2', 'count'),
        prix_m2_median=('prix_m2', 'median'),
        surface_median=('surface_reelle_bati', 'median')
    ).reset_index()
    
    segment_stats['pct_transactions'] = (
        segment_stats['nb_transactions'] / segment_stats['nb_transactions'].sum() * 100
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(
            segment_stats,
            values='nb_transactions',
            names='price_segment',
            title='Market Segments by Transaction Volume'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            segment_stats,
            x='price_segment',
            y='prix_m2_median',
            title='Median Price by Segment',
            labels={'prix_m2_median': 'Price per m² (€)', 'price_segment': 'Segment'},
            color='price_segment'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def create_data_table(df):
    """Create interactive data table."""
    
    st.header("📋 Data Explorer")
    
    # Add filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_type = st.selectbox(
            "Filter by Property Type",
            options=['All'] + df['type_local'].unique().tolist()
        )
    
    with col2:
        max_rows = st.slider("Max rows to display", 100, 1000, 500)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['type_local'] == selected_type]
    
    # Display table
    st.dataframe(
        filtered_df.head(max_rows),
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='dvf_filtered_data.csv',
        mime='text/csv'
    )


def create_methodology_section():
    """Create methodology documentation."""
    
    st.header("📚 Methodology")
    
    st.markdown("""
    - **Dataset:** DVF (Demandes de Valeurs Foncières)
    - **Source:** data.gouv.fr
    - **License:** Licence Ouverte 2.0
    - **Coverage:** 5 départements (75, 13, 69, 31, 44) — Paris, Marseille, Lyon, Toulouse, Nantes
    - **Period:** 2021-2024
    - **Volume:** 557k transactions nettoyées (sur 1,79M brutes)
    
    ### Data Cleaning Steps
    1. **Filter transactions:** Keep only sales (not VEFA, exchanges)
    2. **Property types:** Apartments and houses only
    3. **Surface validation:** 9m² to 500m² range
    4. **Price validation:** 10,000€ to 10,000,000€ range
    5. **Outlier removal:** 3-sigma rule by commune
    6. **Price calculation:** Price per square meter
    
    ### Statistical Methods
    - **Central tendency:** Median (robust to outliers)
    - **Dispersion:** Standard deviation, percentiles
    - **Time series:** Year-over-year growth rates
    - **Geographic analysis:** Spatial aggregation by commune
    
    ### Tools Used
    - **Python:** pandas, numpy, plotly
    - **Dashboard:** Streamlit
    - **Visualization:** Plotly Express
    """)


def create_footer():
    """Create dashboard footer."""
    
    st.divider()
    
    st.markdown("""
    ### 👤 About This Project
    
    This dashboard was created as a **portfolio project** for a Malt.fr data analyst profile.
    
    **Skills Demonstrated:**
    - Data acquisition from official APIs
    - Data cleaning and preprocessing
    - Statistical analysis
    - Interactive data visualization
    - Business insight generation
    
    **Contact :** profil Malt.fr — Data Analyst / Data Scientist Freelance (région parisienne, bilingue FR/EN)
    
    ---
    *Data source: data.gouv.fr | Analysis: Python | Dashboard: Streamlit*
    """)


def main():
    """Main dashboard function."""
    
    # Create header
    create_header()
    
    # Load data
    df = load_data()
    
    # Create sidebar filters
    filtered_df = create_sidebar_filters(df)
    
    # Display KPIs
    display_kpi_metrics(filtered_df)
    
    # Create main sections
    create_price_evolution_chart(filtered_df)
    
    st.divider()
    
    create_geographic_analysis(filtered_df)
    
    st.divider()
    
    create_property_type_analysis(filtered_df)
    
    st.divider()
    
    create_seasonal_analysis(filtered_df)
    
    st.divider()
    
    create_market_segments(filtered_df)
    
    st.divider()
    
    create_data_table(filtered_df)
    
    st.divider()
    
    create_methodology_section()
    
    create_footer()


if __name__ == "__main__":
    main()
