# --- bootstrap to ensure local package is importable in various hosts (Streamlit Cloud/HF Spaces) ---
import sys
from pathlib import Path as _Path
_REPO_ROOT = _Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
# -----------------------------------------------------------------------------------------------

from route_finder.data_loader import load_dataset
from route_finder.ui import main

if __name__ == "__main__":
    df = load_dataset('./east-java-cities-dataset.xlsx')
    main(df)
