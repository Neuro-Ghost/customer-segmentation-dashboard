from pathlib import Path
import os
from typing import List

BASE_DIR = Path(__file__).resolve().parent

# Where the pre-trained model files are stored
MODEL_DIR = BASE_DIR / "models"

SCALER_FILENAME = "scaler.pkl"
KMEANS_FILENAME = "kmeans_model.pkl"

# Expected columns in the cleaned CSV uploaded by the frontend
REQUIRED_COLUMNS = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]

# CORS origins (comma separated in env, default to localhost for dev)
CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Cluster name mapping (adjust if your model uses different numbering)
CLUSTER_NAMES = {
    0: "Steady Customers",
    1: "Engaged Loyalists",
    2: "Occasional Shoppers",
    3: "At-Risk Customers",
}
