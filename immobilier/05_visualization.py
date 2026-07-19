"""
Step 5: Data Visualization for French Real Estate Analysis
==========================================================

This script creates professional visualizations for the DVF analysis:
- Price trend charts
- Geographic heat maps
- Property type comparisons
- Statistical distributions

Perfect for Malt.fr portfolio presentation!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path
import sys

# Set style for professional charts
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Directories
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def find_cleaned_data() -> Path:
    """Find the cleaned DVF data file."""
    clean_files = list(DATA_DIR.glob("*_clean.csv*"))
    
    if not clean_files:
        print("❌ No cleaned data files found!")
        print("Please run 03_data_cleaning.py first.")
        sys.exit(1)
    
    clean_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return clean_files[0]


def load_cleaned_data(file_path: Path) -> pd.DataFrame:
    """Load cleaned DVF data."""
    
    print(f"📥 Loading cleaned data from: {file_path.name}")
    
    dtype_map = {
        'code_commune': str,
        'code_postal': str,
        'type_local': 'category',
        'nature_mutation': 'category',
    }
    
    df = pd.read_csv(
        file_path,
        sep=',',
        dtype=dtype_map,
        parse_dates=['date_mutation'],
        low_memory=False
    )
    
    # Add time columns
    df['year'] = df['date_mutation'].dt.year
    df['month'] = df['date_mutation'].dt.month
    
    print(f"✅ Loaded {len(df):,} cleaned records")
    return df


def create_price_evolution_chart(df: pd.DataFrame) -> None:
    """Create price evolution chart over time."""
    
    print("\n📈 Creating Price Evolution Chart...")
    
    # Calculate yearly stats
    yearly_stats = df.groupby('year').agg(
        prix_m2_median=('prix_m2', 'median'),
        prix_m2_mean=('prix_m2', 'mean'),
        nb_transactions=('prix_m2', 'count')
    ).reset_index()
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Price evolution
    ax1.plot(yearly_stats['year'], yearly_stats['prix_m2_median'], 
             marker='o', linewidth=2.5, markersize=8, color='#2E86AB', label='Median')
    ax1.plot(yearly_stats['year'], yearly_stats['prix_m2_mean'], 
             marker='s', linewidth=2, markersize=6, color='#A23B72', 
             linestyle='--', label='Mean')
    
    ax1.set_title('Price per m² Evolution (2021-2024)', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Price per m² (€)', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # Format y-axis with euro symbol
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # Transaction volume
    ax2.bar(yearly_stats['year'], yearly_stats['nb_transactions'], 
            color='#F18F01', alpha=0.8, edgecolor='white')
    
    ax2.set_title('Transaction Volume by Year', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Number of Transactions', fontsize=12)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (year, count) in enumerate(zip(yearly_stats['year'], yearly_stats['nb_transactions'])):
        ax2.text(year, count + max(yearly_stats['nb_transactions'])*0.02, 
                f'{count:,}', ha='center', fontsize=10)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'price_evolution.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def create_property_type_comparison(df: pd.DataFrame) -> None:
    """Create property type comparison charts."""
    
    print("\n🏠 Creating Property Type Comparison Charts...")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Price comparison by type
    type_stats = df.groupby('type_local').agg(
        prix_m2_median=('prix_m2', 'median'),
        nb_transactions=('prix_m2', 'count')
    ).reset_index()
    
    colors = ['#2E86AB', '#A23B72']
    bars = axes[0, 0].bar(type_stats['type_local'], type_stats['prix_m2_median'], 
                         color=colors, alpha=0.8, edgecolor='white')
    
    axes[0, 0].set_title('Median Price per m² by Property Type', fontsize=12, fontweight='bold')
    axes[0, 0].set_ylabel('Price per m² (€)', fontsize=11)
    axes[0, 0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # Add value labels
    for bar, price in zip(bars, type_stats['prix_m2_median']):
        axes[0, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                       f'{price:,.0f} €', ha='center', fontsize=11, fontweight='bold')
    
    # 2. Transaction distribution
    axes[0, 1].pie(type_stats['nb_transactions'], labels=type_stats['type_local'],
                  autopct='%1.1f%%', colors=colors, startangle=90)
    axes[0, 1].set_title('Transaction Distribution', fontsize=12, fontweight='bold')
    
    # 3. Price distribution by type
    for i, prop_type in enumerate(df['type_local'].unique()):
        data = df[df['type_local'] == prop_type]['prix_m2']
        axes[1, 0].hist(data, bins=50, alpha=0.6, color=colors[i], 
                       label=prop_type, edgecolor='white')
    
    axes[1, 0].set_title('Price Distribution by Property Type', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Price per m² (€)', fontsize=11)
    axes[1, 0].set_ylabel('Frequency', fontsize=11)
    axes[1, 0].legend(fontsize=10)
    axes[1, 0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # 4. Surface area comparison
    surface_stats = df.groupby('type_local')['surface_reelle_bati'].median()
    
    bars = axes[1, 1].bar(surface_stats.index, surface_stats.values, 
                         color=colors, alpha=0.8, edgecolor='white')
    
    axes[1, 1].set_title('Median Surface Area by Type', fontsize=12, fontweight='bold')
    axes[1, 1].set_ylabel('Surface Area (m²)', fontsize=11)
    
    # Add value labels
    for bar, surface in zip(bars, surface_stats.values):
        axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       f'{surface:.0f} m²', ha='center', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'property_type_comparison.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def create_geographic_heatmap(df: pd.DataFrame) -> None:
    """Create geographic price heatmap."""
    
    print("\n🌍 Creating Geographic Heatmap...")
    
    # Filter out rows without coordinates
    df_geo = df.dropna(subset=['longitude', 'latitude'])
    
    if len(df_geo) == 0:
        print("⚠️  No geographic coordinates available for heatmap")
        return
    
    # Sample data for better visualization (if too many points)
    if len(df_geo) > 10000:
        df_sample = df_geo.sample(n=10000, random_state=42)
    else:
        df_sample = df_geo
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Create scatter plot with price coloring
    scatter = ax.scatter(df_sample['longitude'], df_sample['latitude'],
                        c=df_sample['prix_m2'], cmap='YlOrRd',
                        alpha=0.6, s=20, edgecolors='none')
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, label='Price per m² (€)')
    cbar.ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    ax.set_title('Geographic Distribution of Property Prices', fontsize=14, fontweight='bold')
    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    
    # Set aspect ratio equal for proper map display
    ax.set_aspect('equal')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'geographic_heatmap.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def create_seasonal_analysis(df: pd.DataFrame) -> None:
    """Create seasonal analysis charts."""
    
    print("\n📅 Creating Seasonal Analysis Charts...")
    
    # Monthly statistics
    monthly_stats = df.groupby('month').agg(
        prix_m2_median=('prix_m2', 'median'),
        nb_transactions=('prix_m2', 'count')
    ).reset_index()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # 1. Monthly price variations
    ax1.plot(monthly_stats['month'], monthly_stats['prix_m2_median'],
            marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
    
    ax1.fill_between(monthly_stats['month'], monthly_stats['prix_m2_median'],
                    alpha=0.3, color='#2E86AB')
    
    ax1.set_title('Seasonal Price Variations', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Month', fontsize=12)
    ax1.set_ylabel('Median Price per m² (€)', fontsize=12)
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(month_names, rotation=45)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    ax1.grid(True, alpha=0.3)
    
    # Add min/max annotations
    min_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmin()]
    max_month = monthly_stats.loc[monthly_stats['prix_m2_median'].idxmax()]
    
    ax1.annotate(f'Min: {min_month["prix_m2_median"]:,.0f} €',
                xy=(min_month['month'], min_month['prix_m2_median']),
                xytext=(min_month['month'] + 0.5, min_month['prix_m2_median'] - 100),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=10, color='red')
    
    ax1.annotate(f'Max: {max_month["prix_m2_median"]:,.0f} €',
                xy=(max_month['month'], max_month['prix_m2_median']),
                xytext=(max_month['month'] - 0.5, max_month['prix_m2_median'] + 100),
                arrowprops=dict(arrowstyle='->', color='green'),
                fontsize=10, color='green')
    
    # 2. Monthly transaction volume
    colors = ['#F18F01' if count > monthly_stats['nb_transactions'].mean() 
              else '#C73E1D' for count in monthly_stats['nb_transactions']]
    
    bars = ax2.bar(monthly_stats['month'], monthly_stats['nb_transactions'],
                  color=colors, alpha=0.8, edgecolor='white')
    
    ax2.set_title('Monthly Transaction Volume', fontsize=14, fontweight='bold')
    ax2.set_xlabel('Month', fontsize=12)
    ax2.set_ylabel('Number of Transactions', fontsize=12)
    ax2.set_xticks(range(1, 13))
    ax2.set_xticklabels(month_names, rotation=45)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add average line
    avg_transactions = monthly_stats['nb_transactions'].mean()
    ax2.axhline(y=avg_transactions, color='black', linestyle='--', alpha=0.7, 
                label=f'Average: {avg_transactions:,.0f}')
    ax2.legend(fontsize=10)
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'seasonal_analysis.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def create_price_distribution(df: pd.DataFrame) -> None:
    """Create price distribution charts."""
    
    print("\n📊 Creating Price Distribution Charts...")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    
    # 1. Overall price distribution
    axes[0, 0].hist(df['prix_m2'], bins=50, color='#2E86AB', alpha=0.8, edgecolor='white')
    axes[0, 0].axvline(df['prix_m2'].median(), color='red', linestyle='--', linewidth=2,
                       label=f'Median: {df["prix_m2"].median():,.0f} €/m²')
    axes[0, 0].axvline(df['prix_m2'].mean(), color='orange', linestyle='--', linewidth=2,
                       label=f'Mean: {df["prix_m2"].mean():,.0f} €/m²')
    
    axes[0, 0].set_title('Overall Price Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Price per m² (€)', fontsize=11)
    axes[0, 0].set_ylabel('Frequency', fontsize=11)
    axes[0, 0].legend(fontsize=10)
    axes[0, 0].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # 2. Price distribution by property type
    for i, prop_type in enumerate(df['type_local'].unique()):
        data = df[df['type_local'] == prop_type]['prix_m2']
        axes[0, 1].hist(data, bins=40, alpha=0.6, label=prop_type, edgecolor='white')
    
    axes[0, 1].set_title('Price Distribution by Property Type', fontsize=12, fontweight='bold')
    axes[0, 1].set_xlabel('Price per m² (€)', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].legend(fontsize=10)
    axes[0, 1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # 3. Box plot by property type
    df.boxplot(column='prix_m2', by='type_local', ax=axes[1, 0])
    axes[1, 0].set_title('Price Distribution by Property Type', fontsize=12, fontweight='bold')
    axes[1, 0].set_xlabel('Property Type', fontsize=11)
    axes[1, 0].set_ylabel('Price per m² (€)', fontsize=11)
    axes[1, 0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    plt.suptitle('')  # Remove default title
    
    # 4. Price vs Surface area scatter plot
    sample_size = min(5000, len(df))
    df_sample = df.sample(n=sample_size, random_state=42)
    
    scatter = axes[1, 1].scatter(df_sample['surface_reelle_bati'], df_sample['prix_m2'],
                                alpha=0.4, s=20, color='#2E86AB')
    
    axes[1, 1].set_title('Price vs Surface Area', fontsize=12, fontweight='bold')
    axes[1, 1].set_xlabel('Surface Area (m²)', fontsize=11)
    axes[1, 1].set_ylabel('Price per m² (€)', fontsize=11)
    axes[1, 1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'price_distribution.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def create_market_segments_chart(df: pd.DataFrame) -> None:
    """Create market segments visualization."""
    
    print("\n📊 Creating Market Segments Chart...")
    
    # Create price segments
    df['price_segment'] = pd.cut(
        df['prix_m2'],
        bins=[0, 2000, 4000, 6000, 8000, float('inf')],
        labels=['Budget\n(<2K€/m²)', 'Mid-Range\n(2-4K€/m²)', 
                'Premium\n(4-6K€/m²)', 'Luxury\n(6-8K€/m²)', 
                'Ultra-Luxury\n(>8K€/m²)']
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
    
    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. Transaction distribution by segment
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    bars = ax1.bar(segment_stats['price_segment'], segment_stats['pct_transactions'],
                  color=colors, alpha=0.8, edgecolor='white')
    
    ax1.set_title('Market Segments by Transaction Volume', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Price Segment', fontsize=11)
    ax1.set_ylabel('Percentage of Transactions (%)', fontsize=11)
    
    # Add value labels
    for bar, pct in zip(bars, segment_stats['pct_transactions']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{pct:.1f}%', ha='center', fontsize=10, fontweight='bold')
    
    # 2. Median price by segment
    bars = ax2.bar(segment_stats['price_segment'], segment_stats['prix_m2_median'],
                  color=colors, alpha=0.8, edgecolor='white')
    
    ax2.set_title('Median Price by Segment', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Price Segment', fontsize=11)
    ax2.set_ylabel('Median Price per m² (€)', fontsize=11)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f} €'))
    
    # Add value labels
    for bar, price in zip(bars, segment_stats['prix_m2_median']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{price:,.0f} €', ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = OUTPUT_DIR / 'market_segments.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {chart_path.name}")


def main():
    """Main visualization function."""
    
    print("📊 French Real Estate Data Visualization")
    print("=" * 60)
    print("Dataset: DVF (Demandes de Valeurs Foncières)")
    print("Source: data.gouv.fr")
    print()
    
    # Find cleaned data
    data_file = find_cleaned_data()
    
    # Load cleaned data
    df = load_cleaned_data(data_file)
    
    # Create all visualizations
    create_price_evolution_chart(df)
    create_property_type_comparison(df)
    create_geographic_heatmap(df)
    create_seasonal_analysis(df)
    create_price_distribution(df)
    create_market_segments_chart(df)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ ALL VISUALIZATIONS COMPLETE")
    print("=" * 60)
    print(f"\n📁 Charts saved to: {OUTPUT_DIR.absolute()}")
    print("\n📋 Generated Charts:")
    print("  1. price_evolution.png - Price trends over time")
    print("  2. property_type_comparison.png - Apartments vs Houses")
    print("  3. geographic_heatmap.png - Price distribution map")
    print("  4. seasonal_analysis.png - Monthly patterns")
    print("  5. price_distribution.png - Statistical distributions")
    print("  6. market_segments.png - Market segmentation")
    print("\n🚀 Next Steps:")
    print("  1. Use these charts in your Malt.fr portfolio")
    print("  2. Run: streamlit run 06_dashboard.py for interactive version")
    print("  3. Add insights and explanations to your presentation")
    print("\n💼 Portfolio Tips:")
    print("  - Include these visualizations in your project documentation")
    print("  - Explain the business insights each chart reveals")
    print("  - Highlight your technical skills in data visualization")


if __name__ == "__main__":
    main()
