"""
Generate App - Application de gestion des incidents
"""

__version__ = "0.1.0"

import os
import pathlib

def main():
    webapp_path = pathlib.Path(__file__).parent / "webapp.py"
    if not webapp_path.exists():
        raise FileNotFoundError(f"Cannot find {webapp_path}")
    os.system(f"streamlit run {webapp_path}")

if __name__ == '__main__':
    main()