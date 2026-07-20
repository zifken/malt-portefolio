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

THEME = {
    "colors": {
        "bg": "#FFFFFF",
        "surface": "#F5F5F7",
        "primary": "#1B3A5C",
        "secondary": "#C8553D",
        "tertiary": "#5B8C5A",
        "text": "#1A1A1A",
        "muted": "#6B6B6B",
        "grid": "#E0E0E0",
        "font": "Helvetica Neue, Arial, sans-serif",
    }
}

TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=THEME["colors"]["bg"],
        plot_bgcolor=THEME["colors"]["surface"],
        font=dict(
            family=THEME["colors"]["font"],
            color=THEME["colors"]["text"],
        ),
        title=dict(
            font=dict(
                family=THEME["colors"]["font"],
                color=THEME["colors"]["primary"],
            )
        ),
        xaxis=dict(
            gridcolor=THEME["colors"]["grid"],
            linecolor=THEME["colors"]["grid"],
            tickfont=dict(color=THEME["colors"]["text"]),
            title=dict(font=dict(color=THEME["colors"]["primary"])),
            zerolinecolor=THEME["colors"]["grid"],
        ),
        yaxis=dict(
            gridcolor=THEME["colors"]["grid"],
            linecolor=THEME["colors"]["grid"],
            tickfont=dict(color=THEME["colors"]["text"]),
            title=dict(font=dict(color=THEME["colors"]["primary"])),
            zerolinecolor=THEME["colors"]["grid"],
        ),
        colorway=[
            THEME["colors"]["primary"],
            THEME["colors"]["secondary"],
            THEME["colors"]["tertiary"],
        ],
        legend=dict(font=dict(color=THEME["colors"]["text"])),
        hoverlabel=dict(
            bgcolor=THEME["colors"]["surface"],
            font=dict(
                family=THEME["colors"]["font"],
                color=THEME["colors"]["text"],
            ),
        ),
    )
)

# Directories — use __file__-relative path for Streamlit Cloud compatibility
DATA_DIR = Path(__file__).resolve().parent / "data"


@st.cache_data(show_spinner="Chargement de 557 000 transactions...")
def load_data():
    """Load slim parquet (9 columns, ~51 MB in memory) — fits Streamlit Cloud 1 GB limit."""
    parquet_path = DATA_DIR / "dvf_slim.parquet"
    if not parquet_path.exists():
        # Fallback: try CSV.gz (for local dev without the slim parquet)
        clean_files = list(DATA_DIR.glob("*_clean.csv*"))
        if not clean_files:
            st.error("Aucun fichier de données trouvé !")
            st.info("Exécutez d'abord `python 03_data_cleaning.py`, puis `python 04_analysis.py`.")
            st.stop()
        clean_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        df = pd.read_csv(clean_files[0], dtype={'type_local': 'category'},
                         parse_dates=['date_mutation'], low_memory=False)
    else:
        df = pd.read_parquet(parquet_path)

    # Add time columns
    df['year'] = pd.to_datetime(df['date_mutation']).dt.year
    df['month'] = pd.to_datetime(df['date_mutation']).dt.month
    df['month_name'] = pd.to_datetime(df['date_mutation']).dt.strftime('%B')

    return df


def create_header():
    """Create dashboard header."""
    
    st.set_page_config(
        page_title="Analyse du marché immobilier français",
        page_icon=None,
        layout="wide"
    )
    
    st.title("Analyse du marché immobilier français")
    st.markdown("""
    **Tableau de bord interactif** — 5 grandes métropoles françaises (Paris, Marseille, Lyon, Toulouse, Nantes), 2021-2024.
    Données : DVF (data.gouv.fr) · 557 000 transactions nettoyées · Licence Ouverte 2.0.

    *Projet portfolio pour profil Malt.fr — Analyste de données / Scientifique des données.*
    """)
    
    st.divider()


def create_sidebar_filters(df):
    """Create sidebar filters."""
    
    st.sidebar.header("Filtres")
    
    # Property type filter
    property_types = df['type_local'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Type de bien",
        options=property_types,
        default=property_types
    )
    
    # Year filter
    years = sorted(df['year'].unique())
    if len(years) > 1:
        selected_years = st.sidebar.slider(
            "Plage d'années",
            min_value=int(min(years)),
            max_value=int(max(years)),
            value=(int(min(years)), int(max(years)))
        )
    else:
        st.sidebar.info(f"Année des données : {years[0]}")
        selected_years = (years[0], years[0])
    
    # Price range filter
    p_min, p_max = int(df['prix_m2'].min()), int(df['prix_m2'].max())
    if p_min < p_max:
        price_min, price_max = st.sidebar.slider(
            "Plage de prix au m² (€)",
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
            "Plage de surface (m²)",
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
    
    st.header("Indicateurs clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_transactions = len(df)
        st.metric("Total transactions", f"{total_transactions:,.0f}")
    
    with col2:
        avg_price = df['prix_m2'].mean()
        st.metric("Prix moyen au m²", f"{avg_price:,.0f} €")
    
    with col3:
        median_price = df['prix_m2'].median()
        st.metric("Prix médian au m²", f"{median_price:,.0f} €")
    
    with col4:
        avg_surface = df['surface_reelle_bati'].mean()
        st.metric("Surface moyenne", f"{avg_surface:.1f} m²")
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        unique_communes = df['code_commune'].nunique()
        st.metric("Communes distinctes", f"{unique_communes:,.0f}")
    
    with col6:
        price_growth = df.groupby('year')['prix_m2'].median().pct_change().mean() * 100
        st.metric("Croissance annuelle moyenne", f"{price_growth:+.1f}%")
    
    with col7:
        apartments_pct = (df['type_local'] == 'Appartement').mean() * 100
        st.metric("Appartements", f"{apartments_pct:.1f}%")
    
    with col8:
        houses_pct = (df['type_local'] == 'Maison').mean() * 100
        st.metric("Maisons", f"{houses_pct:.1f}%")


def create_price_evolution_chart(df):
    """Create interactive price evolution chart."""
    
    st.header("Évolution des prix dans le temps")
    
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
        title='Évolution du prix au m² par type de bien',
        labels={
            'prix_m2_median': 'Prix au m² (€)',
            'year': 'Année',
            'type_local': 'Type de bien',
        },
        color_discrete_sequence=[
            THEME["colors"]["primary"],
            THEME["colors"]["secondary"],
            THEME["colors"]["tertiary"],
        ],
        markers=True
    )
    
    fig.update_layout(
        template=TEMPLATE,
        **TEMPLATE.layout.to_plotly_json(),
        xaxis_title="Année",
        yaxis_title="Prix au m² (€)",
        hovermode='x unified',
    )
    fig.update_xaxes(tickformat="d")
    fig.update_yaxes(tickformat=",.0f")
    
    st.plotly_chart(fig, use_container_width=True, theme=None)
    
    # Transaction volume chart
    yearly_volume = df.groupby('year').size().reset_index(name='count')
    
    fig_volume = px.bar(
        yearly_volume,
        x='year',
        y='count',
        title='Volume des transactions par année',
        labels={'count': 'Nombre de transactions', 'year': 'Année'},
        color_discrete_sequence=[THEME["colors"]["primary"]]
    )
    fig_volume.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
    fig_volume.update_xaxes(tickformat="d")
    fig_volume.update_yaxes(tickformat=",d")
    
    st.plotly_chart(fig_volume, use_container_width=True, theme=None)


def create_geographic_analysis(df):
    """Create geographic analysis section."""
    
    st.header("Analyse géographique")
    
    # Top communes by price
    st.subheader("Les 20 communes les plus chères")
    
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
        title='Les 20 communes au prix médian au m² le plus élevé',
        labels={'prix_m2_median': 'Prix au m² (€)', 'code_commune': 'Code commune'},
        color='prix_m2_median',
        color_continuous_scale=[
            THEME["colors"]["primary"],
            THEME["colors"]["secondary"],
        ]
    )
    fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
    fig.update_xaxes(type="category")
    fig.update_yaxes(tickformat=",.0f")
    
    st.plotly_chart(fig, use_container_width=True, theme=None)
    
    # Geographic scatter plot
    if 'longitude' in df.columns and 'latitude' in df.columns:
        st.subheader("Répartition géographique des prix")
        
        # Sample for performance
        sample_size = min(5000, len(df))
        df_sample = df.sample(n=sample_size, random_state=42)
        
        fig = px.scatter_mapbox(
            df_sample,
            lat='latitude',
            lon='longitude',
            color='prix_m2',
            size='surface_reelle_bati',
            color_continuous_scale=[
                THEME["colors"]["primary"],
                THEME["colors"]["secondary"],
            ],
            mapbox_style='open-street-map',
            zoom=5,
            title='Prix des biens immobiliers en France',
            labels={
                'prix_m2': 'Prix au m² (€)',
                'surface_reelle_bati': 'Surface bâtie réelle (m²)',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
            }
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        
        st.plotly_chart(fig, use_container_width=True, theme=None)


def create_property_type_analysis(df):
    """Create property type analysis section."""
    
    st.header("Analyse par type de bien")
    
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
            title='Prix médian par type de bien',
            labels={'prix_m2_median': 'Prix au m² (€)', 'type_local': 'Type de bien'},
            color='type_local',
            color_discrete_sequence=[
                THEME["colors"]["primary"],
                THEME["colors"]["secondary"],
                THEME["colors"]["tertiary"],
            ]
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        fig.update_yaxes(tickformat=",.0f")
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
    
    with col2:
        # Transaction distribution
        fig = px.pie(
            type_stats,
            values='nb_transactions',
            names='type_local',
            title='Répartition des transactions par type',
            labels={
                'type_local': 'Type de bien',
                'nb_transactions': 'Transactions',
            },
            color_discrete_sequence=[
                THEME["colors"]["primary"],
                THEME["colors"]["secondary"],
                THEME["colors"]["tertiary"],
            ]
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
    
    # Price distribution
    st.subheader("Répartition des prix par type de bien")
    
    fig = px.histogram(
        df,
        x='prix_m2',
        color='type_local',
        nbins=50,
        title='Répartition des prix par type de bien',
        labels={'prix_m2': 'Prix au m² (€)', 'type_local': 'Type de bien'},
        color_discrete_sequence=[
            THEME["colors"]["primary"],
            THEME["colors"]["secondary"],
            THEME["colors"]["tertiary"],
        ],
        barmode='overlay'
    )
    
    fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json(), bargap=0.1)
    fig.update_xaxes(tickformat=",.0f")
    fig.update_yaxes(tickformat=",d")
    st.plotly_chart(fig, use_container_width=True, theme=None)


def create_seasonal_analysis(df):
    """Create seasonal analysis section."""
    
    st.header("Analyse saisonnière")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly prices
        monthly_stats = df.groupby('month').agg(
            prix_m2_median=('prix_m2', 'median'),
            nb_transactions=('prix_m2', 'count')
        ).reset_index()
        
        month_names = ['Jan', 'Fév', 'Mars', 'Avr', 'Mai', 'Juin',
                       'Juil', 'Août', 'Sept', 'Oct', 'Nov', 'Déc']
        monthly_stats['month_name'] = monthly_stats['month'].apply(lambda x: month_names[x-1])
        
        fig = px.line(
            monthly_stats,
            x='month_name',
            y='prix_m2_median',
            title='Variations saisonnières des prix',
            labels={'prix_m2_median': 'Prix au m² (€)', 'month_name': 'Mois'},
            color_discrete_sequence=[THEME["colors"]["primary"]],
            markers=True
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        fig.update_yaxes(tickformat=",.0f")
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
    
    with col2:
        # Monthly volume
        fig = px.bar(
            monthly_stats,
            x='month_name',
            y='nb_transactions',
            title='Volume mensuel des transactions',
            labels={'nb_transactions': 'Nombre de transactions', 'month_name': 'Mois'},
            color_discrete_sequence=[THEME["colors"]["secondary"]]
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        fig.update_yaxes(tickformat=",d")
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
    
    # Seasonal insights
    st.subheader("Repères saisonniers")
    
    cheapest_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmin()]
    most_expensive_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmax()]
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.info(f"""
        **Meilleur mois pour acheter :** {cheapest_month['month_name']}
        - Prix : {cheapest_month['prix_m2_median']:,.0f} €/m²
        - Transactions : {cheapest_month['nb_transactions']:,.0f}
        """)
    
    with col4:
        st.success(f"""
        **Meilleur mois pour vendre :** {most_expensive_month['month_name']}
        - Prix : {most_expensive_month['prix_m2_median']:,.0f} €/m²
        - Transactions : {most_expensive_month['nb_transactions']:,.0f}
        """)


def create_market_segments(df):
    """Create market segments analysis."""
    
    st.header("Segments de marché")
    
    # Create price segments
    df['price_segment'] = pd.cut(
        df['prix_m2'],
        bins=[0, 2000, 4000, 6000, 8000, float('inf')],
        labels=['Économique (< 2 000 €/m²)', 'Intermédiaire (2 000–4 000 €/m²)',
                'Premium (4 000–6 000 €/m²)', 'Luxe (6 000–8 000 €/m²)',
                'Ultra-luxe (> 8 000 €/m²)']
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
            title='Segments de marché par volume de transactions',
            labels={
                'price_segment': 'Segment',
                'nb_transactions': 'Transactions',
            },
            color_discrete_sequence=[
                THEME["colors"]["primary"],
                THEME["colors"]["secondary"],
                THEME["colors"]["tertiary"],
            ]
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        
        st.plotly_chart(fig, use_container_width=True, theme=None)
    
    with col2:
        fig = px.bar(
            segment_stats,
            x='price_segment',
            y='prix_m2_median',
            title='Prix médian par segment',
            labels={'prix_m2_median': 'Prix au m² (€)', 'price_segment': 'Segment'},
            color='price_segment',
            color_discrete_sequence=[
                THEME["colors"]["primary"],
                THEME["colors"]["secondary"],
                THEME["colors"]["tertiary"],
            ]
        )
        fig.update_layout(template=TEMPLATE, **TEMPLATE.layout.to_plotly_json())
        fig.update_yaxes(tickformat=",.0f")
        
        st.plotly_chart(fig, use_container_width=True, theme=None)


def create_data_table(df):
    """Create interactive data table."""
    
    st.header("Explorateur de données")
    
    # Add filters
    col1, col2 = st.columns(2)
    
    with col1:
        selected_type = st.selectbox(
            "Filtrer par type de bien",
            options=['Tous'] + df['type_local'].unique().tolist()
        )
    
    with col2:
        max_rows = st.slider("Nombre maximal de lignes à afficher", 100, 1000, 500)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_type != 'Tous':
        filtered_df = filtered_df[filtered_df['type_local'] == selected_type]
    
    # Display table
    st.dataframe(
        filtered_df.head(max_rows),
        column_config={
            "date_mutation": "Date de mutation",
            "type_local": "Type de bien",
            "code_commune": st.column_config.NumberColumn(
                "Code commune",
                format="%d",
            ),
            "code_departement": st.column_config.NumberColumn(
                "Code département",
                format="%d",
            ),
            "nom_commune": "Nom de la commune",
            "valeur_fonciere": st.column_config.NumberColumn(
                "Valeur foncière",
                format="%.0f €",
            ),
            "surface_reelle_bati": st.column_config.NumberColumn(
                "Surface réelle bâtie",
                format="%.0f m²",
            ),
            "prix_m2": st.column_config.NumberColumn(
                "Prix au m²",
                format="%.0f €/m²",
            ),
            "latitude": st.column_config.NumberColumn("Latitude", format="%.5f"),
            "longitude": st.column_config.NumberColumn("Longitude", format="%.5f"),
            "year": st.column_config.NumberColumn("Année", format="%d"),
            "month": st.column_config.NumberColumn("Mois", format="%d"),
            "month_name": "Nom du mois",
        },
        use_container_width=True,
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Télécharger les données filtrées au format CSV",
        data=csv,
        file_name='dvf_filtered_data.csv',
        mime='text/csv'
    )


def create_methodology_section():
    """Create methodology documentation."""
    
    st.header("Méthodologie")
    
    st.markdown("""
    - **Jeu de données :** DVF (Demandes de Valeurs Foncières)
    - **Source :** data.gouv.fr
    - **Licence :** Licence Ouverte 2.0
    - **Périmètre :** 5 départements (75, 13, 69, 31, 44) — Paris, Marseille, Lyon, Toulouse, Nantes
    - **Période :** 2021-2024
    - **Volume :** 557 000 transactions nettoyées (sur 1,79 M brutes)
    
    ### Étapes de nettoyage des données
    1. **Filtrage des transactions :** conservation des ventes uniquement (hors VEFA et échanges)
    2. **Types de biens :** appartements et maisons uniquement
    3. **Validation des surfaces :** plage de 9 m² à 500 m²
    4. **Validation des prix :** plage de 10 000 € à 10 000 000 €
    5. **Suppression des valeurs aberrantes :** règle des 3 sigma par commune
    6. **Calcul du prix :** prix au mètre carré
    
    ### Méthodes statistiques
    - **Tendance centrale :** médiane (robuste aux valeurs aberrantes)
    - **Dispersion :** écart-type et percentiles
    - **Séries temporelles :** taux de croissance annuels
    - **Analyse géographique :** agrégation spatiale par commune
    
    ### Outils utilisés
    - **Python :** pandas, numpy, plotly
    - **Tableau de bord :** Streamlit
    - **Visualisation :** Plotly Express
    """)


def create_footer():
    """Create dashboard footer."""
    
    st.divider()
    
    st.markdown("""
    ### À propos de ce projet
    
    Ce tableau de bord a été créé comme **projet de portfolio** pour un profil d'analyste de données sur Malt.fr.
    
    **Compétences mises en œuvre :**
    - Acquisition de données depuis des API officielles
    - Nettoyage et prétraitement des données
    - Analyse statistique
    - Visualisation interactive des données
    - Production d'analyses métier
    
    **Contact :** profil Malt.fr — Analyste de données / Scientifique des données freelance (région parisienne, bilingue FR/EN)
    
    ---
    *Source des données : data.gouv.fr | Analyse : Python | Tableau de bord : Streamlit*
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
