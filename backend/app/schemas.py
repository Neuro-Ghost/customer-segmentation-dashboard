from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class HealthResponse(BaseModel):
    status: str

class RFMRecord(BaseModel):
    CustomerID: Any  # CustomerID can be int or string depending on dataset
    Recency: float
    Frequency: float
    Monetary: float
    AOV: Optional[float] = None
    CustomerLifespan: Optional[float] = None
    CLV: Optional[float] = None
    Cluster: Optional[int] = None
    Segment: Optional[str] = None

class Analytics(BaseModel):
    n_customers: int
    n_rows: int
    cluster_counts: Dict[str, int]
    revenue_by_segment: Dict[str, float]
    avg_rfm: List[Dict[str, Any]]
    top_products_per_segment: Optional[Dict[str, List[Dict[str, Any]]]] = None

class SegmentResponse(BaseModel):
    analytics: Analytics
    preview: List[RFMRecord]
