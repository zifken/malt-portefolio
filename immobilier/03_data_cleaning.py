"""
Step 3: Clean and Preprocess DVF Data
======================================

This script cleans the raw DVF data to make it suitable for analysis:
- Filter for residential properties only
- Remove outliers and invalid data
- Calculate price per square meter
- Prepare data for analysis

Data cleaning is crucial for accurate analysis!
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Directories
DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def find_data_files() -> list[Path]:
    """Find all DVF data files (5 départements × 4 années)."""
    dvf_files = sorted(DATA_DIR.glob("dvf_*.csv.gz"))
    if not dvf_files:
        print("❌ No DVF data files found!")
        print("Please run 01_data_download.py first.")
        sys.exit(1)
    return dvf_files


def load_data(file_paths: list[Path]) -> pd.DataFrame:
    """Load and concatenate all DVF files (5 départements × 4 années)."""
    dtype_map = {
        'code_commune': str,
        'code_postal': str,
        'type_local': 'category',
        'nature_mutation': 'category',
        'nombre_pieces_principales': 'Int64',
    }
    frames = []
    for fp in file_paths:
        print(f"📥 Loading: {fp.name}")
        frames.append(pd.read_csv(
            fp, sep=',', dtype=dtype_map,
            parse_dates=['date_mutation'], low_memory=False,
        ))
    df = pd.concat(frames, ignore_index=True)
    print(f"✅ Loaded {len(df):,} records from {len(file_paths)} files")
    return df


def analyze_raw_data(df: pd.DataFrame) -> None:
    """Analyze the raw data before cleaning."""
    
    print("\n" + "=" * 60)
    print("📊 RAW DATA ANALYSIS")
    print("=" * 60)
    
    print(f"\n📋 Total records: {len(df):,}")
    
    # Transaction types
    if 'nature_mutation' in df.columns:
        print("\n💰 Transaction Types:")
        print("-" * 40)
        nature_counts = df['nature_mutation'].value_counts()
        for nature, count in nature_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {nature:<30} | {count:>6,} ({pct:.1f}%)")
    
    # Property types
    if 'type_local' in df.columns:
        print("\n🏠 Property Types:")
        print("-" * 40)
        type_counts = df['type_local'].value_counts()
        for prop_type, count in type_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {prop_type:<30} | {count:>6,} ({pct:.1f}%)")
    
    # Missing values in key columns
    print("\n⚠️  Missing Values in Key Columns:")
    print("-" * 40)
    key_cols = ['valeur_fonciere', 'surface_reelle_bati', 'type_local', 
                'nature_mutation', 'code_commune']
    
    for col in key_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            pct = (missing / len(df)) * 100
            print(f"  {col:<25} | {missing:>6,} ({pct:.1f}%)")


def clean_dvf_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean DVF data for residential real estate analysis.
    
    Cleaning steps:
    1. Filter for sales only (not VEFA, exchanges, etc.)
    2. Keep only residential properties (apartments and houses)
    3. Remove invalid surface areas
    4. Remove invalid prices
    5. Calculate price per square meter
    6. Remove statistical outliers
    
    Returns:
        Cleaned DataFrame
    """
    
    print("\n" + "=" * 60)
    print("🧹 DATA CLEANING PIPELINE")
    print("=" * 60)
    
    initial_count = len(df)
    print(f"\n📊 Starting with {initial_count:,} records")
    
    # Step 1: Filter for sales only
    print("\n🔍 Step 1: Filtering for sales transactions...")
    if 'nature_mutation' in df.columns:
        # Keep only regular sales (not VEFA, exchanges, etc.)
        sales_mask = df['nature_mutation'] == 'Vente'
        df = df[sales_mask].copy()
        print(f"  ✓ Kept {len(df):,} sales transactions ({len(df)/initial_count*100:.1f}%)")
    
    # Step 2: Keep only residential properties
    print("\n🔍 Step 2: Filtering for residential properties...")
    if 'type_local' in df.columns:
        residential_types = ['Appartement', 'Maison']
        residential_mask = df['type_local'].isin(residential_types)
        df = df[residential_mask].copy()
        print(f"  ✓ Kept {len(df):,} residential properties ({len(df)/initial_count*100:.1f}%)")
    
    # Step 3: Filter valid surface areas
    print("\n🔍 Step 3: Filtering valid surface areas...")
    if 'surface_reelle_bati' in df.columns:
        # Remove missing surfaces
        surface_not_null = df['surface_reelle_bati'].notna()
        df = df[surface_not_null].copy()
        
        # Remove unrealistic surfaces (too small or too large)
        # Minimum: 9m² (French legal minimum for habitation)
        # Maximum: 500m² (reasonable residential limit)
        surface_valid = (df['surface_reelle_bati'] >= 9) & (df['surface_reelle_bati'] <= 500)
        df = df[surface_valid].copy()
        print(f"  ✓ Kept {len(df):,} records with valid surfaces")
    
    # Step 4: Filter valid prices
    print("\n🔍 Step 4: Filtering valid prices...")
    if 'valeur_fonciere' in df.columns:
        # Remove missing prices
        price_not_null = df['valeur_fonciere'].notna()
        df = df[price_not_null].copy()
        
        # Remove zero or negative prices
        price_positive = df['valeur_fonciere'] > 0
        df = df[price_positive].copy()
        
        # Remove unrealistic prices (less than 10,000€ or more than 10,000,000€)
        price_realistic = (df['valeur_fonciere'] >= 10000) & (df['valeur_fonciere'] <= 10000000)
        df = df[price_realistic].copy()
        print(f"  ✓ Kept {len(df):,} records with valid prices")
    
    # Step 5: Calculate price per square meter
    print("\n🔍 Step 5: Calculating price per square meter...")
    if 'valeur_fonciere' in df.columns and 'surface_reelle_bati' in df.columns:
        df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
        
        # Remove extreme outliers (less than 100€/m² or more than 20,000€/m²)
        price_m2_valid = (df['prix_m2'] >= 100) & (df['prix_m2'] <= 20000)
        df = df[price_m2_valid].copy()
        print(f"  ✓ Calculated price/m² for {len(df):,} records")
    
    # Step 6: Remove statistical outliers by commune
    print("\n🔍 Step 6: Removing statistical outliers by commune...")
    if 'code_commune' in df.columns and 'prix_m2' in df.columns:
        initial_before_outliers = len(df)
        
        # Calculate mean and std by commune
        commune_stats = df.groupby('code_commune')['prix_m2'].agg(['mean', 'std']).reset_index()
        commune_stats.columns = ['code_commune', 'commune_mean', 'commune_std']
        
        # Merge stats back to main dataframe
        df = df.merge(commune_stats, on='code_commune', how='left')
        
        # Keep only records within 3 standard deviations
        df['z_score'] = (df['prix_m2'] - df['commune_mean']) / df['commune_std']
        outlier_mask = df['z_score'].abs() <= 3
        df = df[outlier_mask].copy()
        
        # Clean up temporary columns
        df = df.drop(columns=['commune_mean', 'commune_std', 'z_score'])
        
        outliers_removed = initial_before_outliers - len(df)
        print(f"  ✓ Removed {outliers_removed:,} outliers ({outliers_removed/initial_before_outliers*100:.1f}%)")
    
    # Summary
    final_count = len(df)
    print("\n" + "=" * 60)
    print("✅ CLEANING COMPLETE")
    print("=" * 60)
    print(f"📊 Records: {initial_count:,} → {final_count:,}")
    print(f"📊 Retention rate: {final_count/initial_count*100:.1f}%")
    print(f"📊 Records removed: {initial_count - final_count:,}")
    
    return df


def validate_cleaned_data(df: pd.DataFrame) -> None:
    """Validate the cleaned data quality."""
    
    print("\n" + "=" * 60)
    print("✅ DATA VALIDATION")
    print("=" * 60)
    
    # Check for remaining issues
    issues = []
    
    # Check for missing values in critical columns
    critical_cols = ['valeur_fonciere', 'surface_reelle_bati', 'prix_m2', 'type_local']
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                issues.append(f"Column '{col}' has {missing:,} missing values")
    
    # Check for duplicate transactions
    if 'id_mutation' in df.columns:
        duplicates = df.duplicated(subset=['id_mutation']).sum()
        if duplicates > 0:
            issues.append(f"Found {duplicates:,} duplicate mutation IDs")
    
    # Check price ranges
    if 'prix_m2' in df.columns:
        price_stats = df['prix_m2'].describe()
        print(f"\n💰 Price per m² Statistics:")
        print(f"  Mean:   {price_stats['mean']:,.0f} €/m²")
        print(f"  Median: {df['prix_m2'].median():,.0f} €/m²")
        print(f"  Std:    {price_stats['std']:,.0f} €/m²")
        print(f"  Min:    {price_stats['min']:,.0f} €/m²")
        print(f"  Max:    {price_stats['max']:,.0f} €/m²")
    
    # Check surface areas
    if 'surface_reelle_bati' in df.columns:
        surface_stats = df['surface_reelle_bati'].describe()
        print(f"\n📐 Surface Area Statistics:")
        print(f"  Mean:   {surface_stats['mean']:.1f} m²")
        print(f"  Median: {df['surface_reelle_bati'].median():.1f} m²")
        print(f"  Min:    {surface_stats['min']:.1f} m²")
        print(f"  Max:    {surface_stats['max']:.1f} m²")
    
    # Report issues
    if issues:
        print("\n⚠️  Data Quality Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No data quality issues found!")


def save_cleaned_data(df: pd.DataFrame) -> Path:
    """Save the cleaned data to a single canonical file."""
    clean_path = DATA_DIR / "dvf_clean.csv.gz"
    df.to_csv(clean_path, index=False, compression='gzip')
    file_size_mb = clean_path.stat().st_size / 1e6
    print(f"\n💾 Saved cleaned data to: {clean_path.name}")
    print(f"   File size: {file_size_mb:.1f} MB")
    return clean_path


def generate_cleaning_report(df_original: pd.DataFrame, df_cleaned: pd.DataFrame, 
                            report_path: Path) -> None:
    """Generate a cleaning report."""
    
    report = f"""
# Data Cleaning Report
Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Original records: {len(df_original):,}
- Cleaned records: {len(df_cleaned):,}
- Records removed: {len(df_original) - len(df_cleaned):,}
- Retention rate: {len(df_cleaned)/len(df_original)*100:.1f}%

## Cleaning Steps Applied
1. Filtered for sales transactions only (nature_mutation == 'Vente')
2. Kept only residential properties (Appartement, Maison)
3. Removed invalid surface areas (< 9m² or > 500m²)
4. Removed invalid prices (< 10,000€ or > 10,000,000€)
5. Calculated price per square meter
6. Removed statistical outliers (±3σ by commune)

## Key Statistics (Cleaned Data)
- Mean price/m²: {df_cleaned['prix_m2'].mean():,.0f} €/m²
- Median price/m²: {df_cleaned['prix_m2'].median():,.0f} €/m²
- Mean surface: {df_cleaned['surface_reelle_bati'].mean():.1f} m²
- Date range: {df_cleaned['date_mutation'].min()} to {df_cleaned['date_mutation'].max()}

## Property Type Distribution
{df_cleaned['type_local'].value_counts().to_string()}

## Files Generated
- Cleaned data: {report_path.parent.name}/{report_path.name.replace('_report.md', '_clean.csv.gz')}
"""
    
    report_path.write_text(report, encoding='utf-8')
    print(f"📝 Cleaning report saved to: {report_path.name}")


def main():
    """Main cleaning function."""
    
    print("🧹 French Real Estate Data Cleaner")
    print("=" * 60)
    print("Dataset: DVF (Demandes de Valeurs Foncières)")
    print("Source: data.gouv.fr")
    print()
    
    # Find data files (all départements × années)
    data_files = find_data_files()
    # Load and concatenate all files
    df_original = load_data(data_files)
    
    # Analyze raw data
    analyze_raw_data(df_original)
    
    # Clean data
    df_cleaned = clean_dvf_data(df_original)
    
    # Validate cleaned data
    validate_cleaned_data(df_cleaned)
    
    # Save cleaned data
    clean_path = save_cleaned_data(df_cleaned)
    
    # Generate report
    report_path = OUTPUT_DIR / "cleaning_report.md"
    generate_cleaning_report(df_original, df_cleaned, report_path)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ CLEANING PIPELINE COMPLETE")
    print("=" * 60)
    print("\n📋 Next Steps:")
    print("  1. Review the cleaning report in output/")
    print("  2. Run: python 04_analysis.py to analyze the cleaned data")
    print("  3. Or explore in notebooks/02_cleaning.ipynb")
    print("\n💡 Data Quality Notes:")
    print("  - The cleaning removed ~30-40% of records (this is normal)")
    print("  - Outlier removal ensures statistical validity")
    print("  - Price/m² calculation enables fair comparisons")


if __name__ == "__main__":
    main()
