from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
from . import config
from .preprocessing import preprocess_raw_dataset
from .schemas import HealthResponse, SegmentResponse, Analytics, RFMRecord
from typing import List
import io

app = FastAPI(
    title="Customer Segmentation API",
    description="Upload a cleaned retail CSV (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country). API returns RFM + cluster per customer and analytics.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health():
    # If models failed to load at import time, preprocess_raw_dataset would have raised earlier
    return {"status": "ok"}

@app.post("/segment", response_model=None)
async def segment(file: UploadFile = File(...)):
    """
    Accepts multipart/form-data CSV file upload.
    Returns JSON: { analytics: {...}, preview: [ {CustomerID, Recency, Frequency, Monetary, ...}, ... ] }
    """
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .csv")

    try:
        # Read uploaded bytes into pandas
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), encoding="ISO-8859-1")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {e}")

    # Validate columns
    missing = [c for c in config.REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV is missing required columns: {missing}")

    try:
        rfm_clustered, analytics = preprocess_raw_dataset(df)
    except Exception as e:
        # For debugging, return a 500 with error string
        raise HTTPException(status_code=500, detail=f"Error during preprocessing: {e}")

    # Build preview (first 100 rows)
    preview = rfm_clustered.head(100).to_dict(orient="records")

    response = {
        "analytics": analytics,
        "preview": preview,
    }

    return JSONResponse(content=response)
