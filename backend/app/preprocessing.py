import pandas as pd
import joblib
from pathlib import Path
from typing import Tuple, Dict, Any
from . import config
from .utils import compute_totalprice, top_n_products_by_segment

# Load scaler and kmeans once
_MODEL_DIR = Path(config.MODEL_DIR)
_SCALER_PATH = _MODEL_DIR / config.SCALER_FILENAME
_KMEANS_PATH = _MODEL_DIR / config.KMEANS_FILENAME

try:
    SCALER = joblib.load(_SCALER_PATH)
except Exception as e:
    raise RuntimeError(f"Could not load scaler from {_SCALER_PATH}: {e}")

try:
    KMEANS = joblib.load(_KMEANS_PATH)
except Exception as e:
    raise RuntimeError(f"Could not load kmeans from {_KMEANS_PATH}: {e}")

def clean_raw(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning:
    - Trim and standardize types
    - Drop rows without CustomerID, UnitPrice or Quantity
    - Remove cancellations (InvoiceNo starting with 'C')
    - Add TotalPrice
    """
    df = df.copy()

    # Normalize column types/strings
    df["InvoiceNo"] = df["InvoiceNo"].astype(str).str.strip()
    # Convert CustomerID to string to preserve any leading zeros, then back to numeric if needed
    # We will keep it consistent: attempt numeric, else keep as string
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

    # InvoiceDate -> datetime
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

    # Remove rows with missing critical fields
    df = df.dropna(subset=["CustomerID", "InvoiceDate"])

    # Remove negative or zero quantity/price
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").fillna(0)
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce").fillna(0.0)
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    # Remove cancelled invoices (InvoiceNo starting with 'C')
    df = df[~df["InvoiceNo"].str.startswith("C", na=False)]

    # Drop duplicates
    df = df.drop_duplicates()

    # Compute TotalPrice
    df = compute_totalprice(df)

    return df

def calculate_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the RFM table for each CustomerID.
    Output columns: CustomerID, Recency, Frequency, Monetary, AOV, CustomerLifespan, CLV
    """
    df = df.copy()
    # Snapshot date: one day after the last invoice in data
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    # Frequency: number of unique invoices per customer
    # Recency: days since last invoice
    # Monetary: sum of TotalPrice
    agg = df.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("TotalPrice", "sum"),
    ).reset_index()

    # Calculate AOV (Average Order Value)
    agg["AOV"] = (agg["Monetary"] / agg["Frequency"]).replace([float("inf"), float("-inf")], 0).fillna(0)

    # Lifespan: difference between first and last purchase in days
    first = df.groupby("CustomerID")["InvoiceDate"].min()
    last = df.groupby("CustomerID")["InvoiceDate"].max()
    lifespan = (last - first).dt.days.fillna(0)
    agg["CustomerLifespan"] = agg["CustomerID"].map(lifespan).fillna(0)

    # CLV proxy
    agg["CLV"] = agg["AOV"] * agg["Frequency"] * agg["CustomerLifespan"]

    return agg

def scale_and_cluster(rfm: pd.DataFrame) -> pd.DataFrame:
    """
    Scale [Recency, Frequency, Monetary] using preloaded SCALER and predict cluster with KMEANS.
    Adds 'Cluster' and 'Segment' columns to the returned DataFrame.
    """
    rfm = rfm.copy()
    features = ["Recency", "Frequency", "Monetary"]
    # Ensure the features exist
    if not all(col in rfm.columns for col in features):
        raise ValueError(f"RFM is missing required columns: {features}")

    # scaler expects numeric 2D array
    X = rfm[features].astype(float).values
    X_scaled = SCALER.transform(X)
    clusters = KMEANS.predict(X_scaled)

    rfm["Cluster"] = clusters
    # Map cluster to friendly name (falls back to "Cluster {i}" if mapping missing)
    rfm["Segment"] = rfm["Cluster"].map(config.CLUSTER_NAMES).fillna(rfm["Cluster"].apply(lambda x: f"Cluster {x}"))

    return rfm

def summarize_segments(rfm_clustered: pd.DataFrame, raw_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Create analytics summary for dashboard:
    - n_customers, n_rows
    - cluster_counts
    - revenue_by_segment
    - avg_rfm per segment
    - top_products_per_segment (top 5)
    """
    analytics = {}
    analytics["n_customers"] = int(rfm_clustered.shape[0])
    analytics["n_rows"] = int(raw_df.shape[0])

    # Cluster counts
    cluster_counts = rfm_clustered["Segment"].value_counts().to_dict()
    analytics["cluster_counts"] = {str(k): int(v) for k, v in cluster_counts.items()}

    # Revenue by segment: merge totalprice from raw transactions
    merged = raw_df.copy()
    # Ensure TotalPrice exists
    if "TotalPrice" not in merged.columns:
        merged = compute_totalprice(merged)
    seg_map = rfm_clustered.set_index("CustomerID")["Segment"].to_dict()
    merged["Segment"] = merged["CustomerID"].map(seg_map)
    revenue = merged.groupby("Segment")["TotalPrice"].sum().to_dict()
    analytics["revenue_by_segment"] = {str(k): float(v) for k, v in revenue.items()}

    # Average RFM by segment
    avg_rfm = rfm_clustered.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean().round(2).reset_index()
    analytics["avg_rfm"] = avg_rfm.to_dict(orient="records")

    # Top products per segment
    analytics["top_products_per_segment"] = top_n_products_by_segment(merged, n=5)

    return analytics

def preprocess_raw_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Full pipeline:
    - validate and clean raw df
    - compute RFM
    - scale & cluster
    - produce analytics summary
    Returns (rfm_clustered_df, analytics_dict)
    """
    # Clean
    df_clean = clean_raw(df)

    # Calculate RFM
    rfm = calculate_rfm(df_clean)

    # Scale & cluster
    rfm_clustered = scale_and_cluster(rfm)

    # Analytics
    analytics = summarize_segments(rfm_clustered, df_clean)

    return rfm_clustered, analytics
