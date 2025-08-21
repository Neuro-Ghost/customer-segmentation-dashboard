from typing import Iterable, Dict, List
import pandas as pd

def validate_columns(df: pd.DataFrame, required: Iterable[str]) -> List[str]:
    """Return list of missing columns (empty if none)."""
    missing = [c for c in required if c not in df.columns]
    return missing

def compute_totalprice(df: pd.DataFrame) -> pd.DataFrame:
    """Add TotalPrice column to transactions dataframe."""
    df = df.copy()
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce").fillna(0.0)
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
    return df

def top_n_products_by_segment(df_raw_with_segment: pd.DataFrame, n: int = 5) -> Dict[str, List[Dict]]:
    """
    Compute top n products (by quantity sold) for each segment.
    Returns dict: { segment_name: [ {Description, StockCode, total_quantity, total_revenue}, ... ] }
    """
    result = {}
    # Ensure TotalPrice exists
    if "TotalPrice" not in df_raw_with_segment.columns:
        df_raw_with_segment = compute_totalprice(df_raw_with_segment)

    grouped = df_raw_with_segment.groupby(["Segment", "Description", "StockCode"]).agg(
        total_quantity=("Quantity", "sum"),
        total_revenue=("TotalPrice", "sum"),
    ).reset_index()

    for seg, seg_df in grouped.groupby("Segment"):
        top = seg_df.sort_values("total_quantity", ascending=False).head(n)
        result[str(seg)] = top[["Description", "StockCode", "total_quantity", "total_revenue"]].to_dict(orient="records")

    return result
