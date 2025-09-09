from __future__ import annotations
import pandas as pd

# Loader mirrors the original preprocessing exactly.

def load_dataset(path: str = './east-java-cities-dataset.xlsx') -> pd.DataFrame:
    df = pd.read_excel(path)
    df = df.dropna()
    df['Latitude'] = df['Latitude'].astype(str).str.replace(',', '.')
    df['Longitude'] = df['Longitude'].astype(str).str.replace(',', '.')
    df['Latitude'] = pd.to_numeric(df['Latitude'])
    df['Longitude'] = pd.to_numeric(df['Longitude'])
    return df
