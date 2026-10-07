"""
Step 2: Explore the DVF Dataset
================================

Initial exploration of the French real estate data to understand:
- Dataset structure and columns
- Data types and missing values
- Basic statistics
- Sample records

This is the first step in any data analysis project!
"""

import pandas as pd
from pathlib import Path
import sys

# Data directory
DATA_DIR = Path("data")


def find_latest_data() -> Path:
    """Find the most recent DVF data file."""
    dvf_files = list(DATA_DIR.glob("dvf_*.csv.gz"))
    
    if not dvf_files:
        print("❌ No DVF data files found!")
        print("Please run 01_data_download.py first.")
        sys.exit(1)
    
    # Sort by modification time (newest first)
    dvf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    latest_file = dvf_files[0]
    
    print(f"📁 Using data file: {latest_file.name}")
    return latest_file


def explore_dataset(df: pd.DataFrame) -> None:
    """Perform initial exploration of the dataset."""
    
    print("\n" + "=" * 60)
    print("🔍 DATASET OVERVIEW")
    print("=" * 60)
    
    # Basic info
    print(f"\n📊 Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
    print(f"💾 Memory Usage: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")
    
    # Column information
    print("\n📋 COLUMNS:")
    print("-" * 60)
    for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
        null_count = df[col].isna().sum()
        null_pct = (null_count / len(df)) * 100
        print(f"{i:2d}. {col:<30} | {str(dtype):<10} | {null_count:>6,} nulls ({null_pct:.1f}%)")
    
    # Key columns for analysis
    print("\n🎯 KEY COLUMNS FOR ANALYSIS:")
    print("-" * 60)
    key_columns = [
        'date_mutation', 'valeur_fonciere', 'surface_reelle_bati',
        'type_local', 'nature_mutation', 'code_commune',
        'longitude', 'latitude'
    ]
    
    for col in key_columns:
        if col in df.columns:
            print(f"✓ {col}")
        else:
            print(f"✗ {col} (not found)")
    
    # Sample records
    print("\n📝 SAMPLE RECORDS (first 5):")
    print("-" * 60)
    print(df.head().to_string())
    
    # Data types summary
    print("\n📊 DATA TYPES SUMMARY:")
    print("-" * 60)
    print(df.dtypes.value_counts().to_string())
    
    # Missing values analysis
    print("\n⚠️  MISSING VALUES ANALYSIS:")
    print("-" * 60)
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    
    if len(missing) > 0:
        for col, count in missing.head(10).items():
            pct = (count / len(df)) * 100
            print(f"{col:<30} | {count:>6,} ({pct:.1f}%)")
    else:
        print("No missing values found!")


def explore_categorical_columns(df: pd.DataFrame) -> None:
    """Explore categorical columns (type_local, nature_mutation)."""
    
    print("\n" + "=" * 60)
    print("📊 CATEGORICAL COLUMN ANALYSIS")
    print("=" * 60)
    
    # Type of property
    if 'type_local' in df.columns:
        print("\n🏠 Property Types (type_local):")
        print("-" * 40)
        type_counts = df['type_local'].value_counts()
        for prop_type, count in type_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {prop_type:<25} | {count:>6,} ({pct:.1f}%)")
    
    # Nature of transaction
    if 'nature_mutation' in df.columns:
        print("\n💰 Transaction Types (nature_mutation):")
        print("-" * 40)
        nature_counts = df['nature_mutation'].value_counts()
        for nature, count in nature_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {nature:<25} | {count:>6,} ({pct:.1f}%)")


def explore_numerical_columns(df: pd.DataFrame) -> None:
    """Explore numerical columns (price, surface)."""
    
    print("\n" + "=" * 60)
    print("📊 NUMERICAL COLUMN ANALYSIS")
    print("=" * 60)
    
    # Price analysis
    if 'valeur_fonciere' in df.columns:
        print("\n💶 Property Values (valeur_fonciere):")
        print("-" * 40)
        price_stats = df['valeur_fonciere'].describe()
        
        print(f"  Count:    {price_stats['count']:>12,.0f}")
        print(f"  Mean:     {price_stats['mean']:>12,.0f} €")
        print(f"  Median:   {df['valeur_fonciere'].median():>12,.0f} €")
        print(f"  Std:      {price_stats['std']:>12,.0f} €")
        print(f"  Min:      {price_stats['min']:>12,.0f} €")
        print(f"  25%:      {price_stats['25%']:>12,.0f} €")
        print(f"  75%:      {price_stats['75%']:>12,.0f} €")
        print(f"  Max:      {price_stats['max']:>12,.0f} €")
        
        # Price distribution
        print("\n  Price Ranges:")
        ranges = [
            (0, 100_000, "0-100K€"),
            (100_000, 200_000, "100K-200K€"),
            (200_000, 500_000, "200K-500K€"),
            (500_000, 1_000_000, "500K-1M€"),
            (1_000_000, float('inf'), "1M€+")
        ]
        
        for low, high, label in ranges:
            count = ((df['valeur_fonciere'] >= low) & (df['valeur_fonciere'] < high)).sum()
            pct = (count / len(df)) * 100
            print(f"    {label:<15} | {count:>6,} ({pct:.1f}%)")
    
    # Surface area analysis
    if 'surface_reelle_bati' in df.columns:
        print("\n📐 Surface Areas (surface_reelle_bati):")
        print("-" * 40)
        surface_stats = df['surface_reelle_bati'].describe()
        
        print(f"  Count:    {surface_stats['count']:>12,.0f}")
        print(f"  Mean:     {surface_stats['mean']:>12,.1f} m²")
        print(f"  Median:   {df['surface_reelle_bati'].median():>12,.1f} m²")
        print(f"  Min:      {surface_stats['min']:>12,.1f} m²")
        print(f"  Max:      {surface_stats['max']:>12,.1f} m²")


def explore_temporal_columns(df: pd.DataFrame) -> None:
    """Explore temporal columns (dates)."""
    
    print("\n" + "=" * 60)
    print("📅 TEMPORAL ANALYSIS")
    print("=" * 60)
    
    if 'date_mutation' in df.columns:
        # Convert to datetime if needed
        if not pd.api.types.is_datetime64_any_dtype(df['date_mutation']):
            df['date_mutation'] = pd.to_datetime(df['date_mutation'], errors='coerce')
        
        print("\n📆 Date Range:")
        print("-" * 40)
        print(f"  Earliest: {df['date_mutation'].min()}")
        print(f"  Latest:   {df['date_mutation'].max()}")
        print(f"  Span:     {(df['date_mutation'].max() - df['date_mutation'].min()).days} days")
        
        # Transactions by year
        print("\n📊 Transactions by Year:")
        print("-" * 40)
        yearly = df.groupby(df['date_mutation'].dt.year).size()
        for year, count in yearly.items():
            print(f"  {year}: {count:>6,} transactions")
        
        # Transactions by month
        print("\n📊 Transactions by Month:")
        print("-" * 40)
        monthly = df.groupby(df['date_mutation'].dt.month).size()
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        for month, count in monthly.items():
            print(f"  {month_names[month-1]}: {count:>6,} transactions")


def explore_geographic_columns(df: pd.DataFrame) -> None:
    """Explore geographic columns (communes, coordinates)."""
    
    print("\n" + "=" * 60)
    print("🌍 GEOGRAPHIC ANALYSIS")
    print("=" * 60)
    
    if 'code_commune' in df.columns:
        print("\n🏘️  Communes:")
        print("-" * 40)
        unique_communes = df['code_commune'].nunique()
        print(f"  Unique communes: {unique_communes:,}")
        
        # Top 10 communes by transaction count
        print("\n  Top 10 Communes by Transaction Count:")
        top_communes = df['code_commune'].value_counts().head(10)
        for commune, count in top_communes.items():
            print(f"    {commune}: {count:>4,} transactions")
    
    if 'longitude' in df.columns and 'latitude' in df.columns:
        print("\n📍 Coordinates:")
        print("-" * 40)
        
        # Filter out null coordinates
        coords = df[['longitude', 'latitude']].dropna()
        
        if len(coords) > 0:
            print(f"  Records with coordinates: {len(coords):,} ({len(coords)/len(df)*100:.1f}%)")
            print(f"  Longitude range: {coords['longitude'].min():.3f} to {coords['longitude'].max():.3f}")
            print(f"  Latitude range:  {coords['latitude'].min():.3f} to {coords['latitude'].max():.3f}")
            
            # Check if data is in France (approximate bounds)
            france_bounds = {
                'lon_min': -5.0, 'lon_max': 10.0,
                'lat_min': 41.0, 'lat_max': 51.0
            }
            
            in_france = (
                (coords['longitude'] >= france_bounds['lon_min']) &
                (coords['longitude'] <= france_bounds['lon_max']) &
                (coords['latitude'] >= france_bounds['lat_min']) &
                (coords['latitude'] <= france_bounds['lat_max'])
            ).sum()
            
            print(f"  Coordinates in France bounds: {in_france:,} ({in_france/len(coords)*100:.1f}%)")


def main():
    """Main exploration function."""
    
    print("🔍 French Real Estate Data Explorer")
    print("=" * 60)
    print("Dataset: DVF (Demandes de Valeurs Foncières)")
    print("Source: data.gouv.fr")
    print()
    
    # Find data file
    data_file = find_latest_data()
    
    # Load data with optimized settings
    print("📥 Loading data...")
    
    # Define column types for faster loading
    dtype_map = {
        'code_commune': str,
        'code_postal': str,
        'type_local': 'category',
        'nature_mutation': 'category',
        'nombre_pieces_principales': 'Int64',  # nullable integer
    }
    
    try:
        df = pd.read_csv(
            data_file,
            sep=',',
            dtype=dtype_map,
            parse_dates=['date_mutation'],
            low_memory=False
        )
        print(f"✅ Loaded {len(df):,} records")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print("Make sure you've run 01_data_download.py first.")
        sys.exit(1)
    
    # Run all explorations
    explore_dataset(df)
    explore_categorical_columns(df)
    explore_numerical_columns(df)
    explore_temporal_columns(df)
    explore_geographic_columns(df)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ EXPLORATION COMPLETE")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("  1. Review the data quality issues identified above")
    print("  2. Run: python 03_data_cleaning.py to clean the data")
    print("  3. Or explore interactively in notebooks/01_exploration.ipynb")
    print("\n💡 Key Insights to Note:")
    print("  - What percentage of records have missing values?")
    print("  - What are the most common property types?")
    print("  - What's the date range of the data?")
    print("  - Which communes have the most transactions?")


if __name__ == "__main__":
    main()
