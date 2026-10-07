#!/usr/bin/env python3
"""
Quick Setup Script for French Real Estate Analysis Project
==========================================================

This script automates the setup process:
1. Creates virtual environment
2. Installs dependencies
3. Downloads sample data
4. Runs initial exploration

Run with: python setup.py
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is sufficient."""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required!")
        print(f"Current version: {sys.version}")
        print("Please install Python 3.9+ from https://python.org")
        return False
    
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True


def create_virtual_environment():
    """Create Python virtual environment."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command(
        f"{sys.executable} -m venv .venv",
        "Creating virtual environment"
    )


def install_dependencies():
    """Install Python dependencies."""
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = ".venv\\Scripts\\pip"
    else:  # macOS/Linux
        pip_cmd = ".venv/bin/pip"
    
    return run_command(
        f"{pip_cmd} install -r requirements.txt",
        "Installing dependencies"
    )


def download_sample_data():
    """Download sample data."""
    print("\n📥 Downloading sample data...")
    print("This will download DVF data for department 69 (Rhône/Lyon area)")
    print("File size: ~15 MB")
    
    response = input("\nDownload sample data? (y/n): ").strip().lower()
    
    if response in ['y', 'yes', '']:
        # Run download script
        if os.name == 'nt':  # Windows
            python_cmd = ".venv\\Scripts\\python"
        else:  # macOS/Linux
            python_cmd = ".venv/bin/python"
        
        return run_command(
            f'{python_cmd} -c "from 01_data_download import *; download_dvf_department(\'69\')"',
            "Downloading sample data"
        )
    else:
        print("⏭️  Skipping data download")
        print("You can download data later with: python 01_data_download.py")
        return True


def run_initial_exploration():
    """Run initial data exploration."""
    print("\n🔍 Running initial data exploration...")
    
    response = input("Run data exploration? (y/n): ").strip().lower()
    
    if response in ['y', 'yes', '']:
        # Run exploration script
        if os.name == 'nt':  # Windows
            python_cmd = ".venv\\Scripts\\python"
        else:  # macOS/Linux
            python_cmd = ".venv/bin/python"
        
        return run_command(
            f"{python_cmd} 02_data_exploration.py",
            "Running data exploration"
        )
    else:
        print("⏭️  Skipping data exploration")
        print("You can explore data later with: python 02_data_exploration.py")
        return True


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("-" * 40)
    
    # Activation command
    if os.name == 'nt':  # Windows
        activate_cmd = ".venv\\Scripts\\activate"
    else:  # macOS/Linux
        activate_cmd = "source .venv/bin/activate"
    
    print(f"\n1. Activate virtual environment:")
    print(f"   {activate_cmd}")
    
    print(f"\n2. Download data (if not done already):")
    print(f"   python 01_data_download.py")
    
    print(f"\n3. Run the complete analysis pipeline:")
    print(f"   python 02_data_exploration.py")
    print(f"   python 03_data_cleaning.py")
    print(f"   python 04_analysis.py")
    print(f"   python 05_visualization.py")
    
    print(f"\n4. Launch interactive dashboard:")
    print(f"   streamlit run 06_dashboard.py")
    
    print(f"\n5. View generated files:")
    print(f"   output/          - Charts and reports")
    print(f"   data/            - Data files")
    
    print("\n📚 Documentation:")
    print("-" * 40)
    print("  README.md        - Project overview")
    print("  QUICKSTART.md    - Step-by-step guide")
    print("  requirements.txt - Python dependencies")
    
    print("\n💡 Tips:")
    print("-" * 40)
    print("  • Each script has detailed comments explaining the code")
    print("  • Check the output/ folder for generated charts")
    print("  • Use the dashboard to explore data interactively")
    print("  • Customize visualizations for your portfolio style")
    
    print("\n🚀 Ready to impress Malt.fr clients!")
    print("=" * 60)


def main():
    """Main setup function."""
    
    print("🏠 French Real Estate Analysis - Project Setup")
    print("=" * 60)
    print("This script will set up your development environment")
    print("and prepare everything for data analysis.\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        print("\n❌ Setup failed at virtual environment creation")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed at dependency installation")
        sys.exit(1)
    
    # Download sample data
    if not download_sample_data():
        print("\n⚠️  Data download failed, but setup can continue")
        print("You can download data manually later")
    
    # Run initial exploration
    if not run_initial_exploration():
        print("\n⚠️  Exploration failed, but setup can continue")
        print("You can run exploration manually later")
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
