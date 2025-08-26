"""
Enhanced Customer Segmentation API
=================================

This FastAPI application provides a comprehensive customer segmentation service
with support for custom column mappings, business-specific models, and advanced
analytics. It follows the exact methodology from the Jupyter notebook analysis.

Features:
- Column mapping and intelligent suggestions
- Business-specific model training and storage
- Comprehensive error handling and logging
- Performance monitoring
- Database persistence

Author: Customer Segmentation Team
Date: August 2025
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import io
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Import our custom modules
from .column_mapping import (
    ColumnMappingRequest, 
    ColumnMappingResponse, 
    suggest_column_mapping, 
    STANDARD_COLUMNS,
    ANALYSIS_MODES,
    validate_required_mappings
)
from .preprocessing_v2 import process_full_pipeline
from .database import BusinessModelDB
from .schemas import HealthResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Customer Segmentation API",
    description="""
    🎯 **Advanced Customer Segmentation with Column Mapping**
    
    This API provides intelligent customer segmentation using RFM analysis with:
    - **Smart Column Mapping**: Automatically detect and map your CSV columns
    - **Business-Specific Models**: Train and store models per business
    - **Advanced Analytics**: Comprehensive insights and visualizations
    - **Performance Tracking**: Monitor model performance over time
    
    **Supported Column Types:**
    - Required: InvoiceNo, CustomerID, Quantity, UnitPrice, InvoiceDate
    - Optional: StockCode, Description, Country
    """,
    version="2.0.0",
    contact={
        "name": "Customer Segmentation Team",
        "email": "support@customersegmentation.com"
    }
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5176",  # Added for current frontend port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5176"   # Added for current frontend port
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize database
try:
    db = BusinessModelDB()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    db = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API status.
    
    Returns:
        dict: Service health status and system information
    """
    try:
        # Check database connectivity
        db_status = "healthy" if db else "unavailable"
        
        # Get system stats if database is available
        stats = {}
        if db:
            try:
                stats = db.get_business_stats()
            except Exception as e:
                logger.warning(f"Could not retrieve database stats: {str(e)}")
                stats = {"error": "Could not retrieve stats"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database_status": db_status,
            "system_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.post("/analyze-columns", response_model=ColumnMappingResponse)
async def analyze_columns(file: UploadFile = File(...)):
    """
    Analyze uploaded CSV columns and provide intelligent mapping suggestions.
    
    This endpoint examines your CSV file and suggests how to map your columns
    to our standard format for optimal analysis results.
    
    Args:
        file: CSV file to analyze
        
    Returns:
        ColumnMappingResponse: Analysis results with suggestions
    """
    try:
        logger.info(f"Analyzing columns for file: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400, 
                detail="File must be a CSV (.csv extension required)"
            )
        
        # Read the CSV file
        content = await file.read()
        
        # Try different encodings
        for encoding in ['utf-8', 'iso-8859-1', 'cp1252']:
            try:
                df = pd.read_csv(io.StringIO(content.decode(encoding)))
                logger.info(f"Successfully read CSV with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise HTTPException(
                status_code=400,
                detail="Could not decode CSV file. Please ensure it's a valid CSV with UTF-8 or ISO-8859-1 encoding."
            )
        
        logger.info(f"CSV loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Get column information
        detected_columns = df.columns.tolist()
        suggestions = suggest_column_mapping(detected_columns)
        
        # Log the analysis results
        logger.info(f"Detected {len(detected_columns)} columns")
        logger.info(f"Generated {len(suggestions)} mapping suggestions")
        
        response = ColumnMappingResponse(
            core_required_columns=list(STANDARD_COLUMNS["core_required"].keys()),
            recommended_columns=list(STANDARD_COLUMNS["recommended"].keys()),
            optional_columns=list(STANDARD_COLUMNS["optional"].keys()),
            detected_columns=detected_columns,
            suggestions=suggestions,
            analysis_modes=ANALYSIS_MODES
        )
        
        logger.info("Column analysis completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing columns: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing file: {str(e)}"
        )

@app.post("/segment-with-mapping")
async def segment_with_mapping(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    business_name: str = Form(...),
    column_mappings: str = Form(...),
    retrain_model: bool = Form(default=True),
    notes: str = Form(default="")
):
    """
    🎯 **Main Segmentation Endpoint with Custom Column Mapping**
    
    Process customer segmentation with your custom column mappings.
    This endpoint follows the exact methodology from the notebook analysis.
    
    Args:
        file: CSV file with transaction data
        business_name: Unique identifier for your business
        column_mappings: JSON string mapping your columns to standard names
        retrain_model: Whether to retrain the model or use existing one
        notes: Optional notes about this analysis
        
    Returns:
        dict: Comprehensive segmentation results and analytics
    """
    try:
        logger.info("="*60)
        logger.info("STARTING SEGMENTATION WITH MAPPING")
        logger.info(f"Business: {business_name}")
        logger.info(f"File: {file.filename}")
        logger.info(f"Retrain Model: {retrain_model}")
        logger.info("="*60)
        
        # Validate inputs
        if not file.filename.lower().endswith(".csv"):
            raise HTTPException(
                status_code=400, 
                detail="File must be a CSV (.csv extension required)"
            )
        
        if not business_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Business name is required"
            )
        
        # Parse column mappings
        try:
            mappings = json.loads(column_mappings)
            logger.info(f"Parsed column mappings: {mappings}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in column_mappings: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid JSON in column_mappings: {str(e)}"
            )
        
        # Validate required columns are mapped and determine analysis mode
        validation_result = validate_required_mappings(mappings)
        if not validation_result["is_valid"]:
            error_details = {
                "message": validation_result.get("error_message", "Validation failed"),
                "missing_columns": validation_result.get("missing_columns", []),
                "available_columns": validation_result.get("available_columns", []),
                "possible_modes": validation_result.get("possible_modes", [])
            }
            logger.warning(f"Column validation failed: {error_details}")
            raise HTTPException(
                status_code=400, 
                detail=error_details
            )
        
        analysis_mode = validation_result["analysis_mode"]
        logger.info(f"Using analysis mode: {analysis_mode} - {validation_result.get('mode_description', '')}")
        
        # Log warnings if any
        for warning in validation_result.get("warnings", []):
            logger.warning(warning)
        
        # Read the CSV file
        try:
            content = await file.read()
            
            # Try different encodings
            for encoding in ['utf-8', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(io.StringIO(content.decode(encoding)))
                    logger.info(f"CSV loaded with {encoding}: {df.shape}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode CSV with any standard encoding")
                
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            raise HTTPException(
                status_code=400, 
                detail=f"Error reading CSV file: {str(e)}"
            )
        
        # Validate that mapped columns exist in the dataframe
        missing_columns = [col for col in mappings.keys() if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail=f"Mapped columns not found in CSV: {missing_columns}"
            )
        
        # Process the data through the complete pipeline
        try:
            logger.info("Starting data processing pipeline...")
            rfm_with_clusters, analytics = process_full_pipeline(
                df=df,
                column_mappings=mappings,
                business_name=business_name,
                analysis_mode=analysis_mode,
                retrain=retrain_model
            )
            
        except Exception as e:
            logger.error(f"Error in processing pipeline: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing data: {str(e)}"
            )
        
        # Save business model info to database (background task)
        if db:
            def save_model_info():
                try:
                    model_info = {
                        'model_path': f"models/{business_name}/kmeans_model.pkl",
                        'scaler_path': f"models/{business_name}/scaler.pkl",
                        'n_customers': len(rfm_with_clusters),
                        'n_transactions': len(df),
                        'performance_metrics': analytics.get('model_performance', {}),
                        'model_version': '2.0',
                        'notes': notes
                    }
                    
                    success = db.save_business_model(business_name, mappings, model_info)
                    if success:
                        logger.info(f"Business model saved to database: {business_name}")
                    else:
                        logger.warning(f"Failed to save business model: {business_name}")
                        
                except Exception as e:
                    logger.error(f"Error saving to database: {str(e)}")
            
            background_tasks.add_task(save_model_info)
        
        # Prepare response data
        preview_data = rfm_with_clusters.head(100).to_dict('records')
        
        response = {
            "success": True,
            "message": "Segmentation completed successfully",
            "analytics": analytics,
            "preview": preview_data,
            "business_name": business_name,
            "column_mappings_used": mappings,
            "model_retrained": retrain_model,
            "processing_summary": {
                "original_rows": len(df),
                "customers_segmented": len(rfm_with_clusters),
                "segments_identified": len(rfm_with_clusters['Cluster'].unique()),
                "processing_time": datetime.now().isoformat()
            }
        }
        
        logger.info("="*60)
        logger.info("SEGMENTATION COMPLETED SUCCESSFULLY")
        logger.info(f"Customers Segmented: {len(rfm_with_clusters)}")
        logger.info(f"Segments Created: {len(rfm_with_clusters['Cluster'].unique())}")
        logger.info("="*60)
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in segment_with_mapping: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/businesses")
async def list_businesses():
    """
    📋 **List All Businesses**
    
    Get a list of all businesses that have trained segmentation models.
    """
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )
        
        businesses = db.list_businesses()
        logger.info(f"Retrieved {len(businesses)} businesses")
        
        return {
            "success": True,
            "count": len(businesses),
            "businesses": businesses
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing businesses: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving businesses: {str(e)}"
        )

@app.get("/business/{business_name}")
async def get_business_info(business_name: str):
    """
    🏢 **Get Business Model Information**
    
    Retrieve detailed information about a specific business model.
    """
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )
        
        business_info = db.get_business_model(business_name)
        if not business_info:
            raise HTTPException(
                status_code=404, 
                detail=f"Business model not found: {business_name}"
            )
        
        logger.info(f"Retrieved business info for: {business_name}")
        return {
            "success": True,
            "business_info": business_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting business info for {business_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving business info: {str(e)}"
        )

@app.delete("/business/{business_name}")
async def delete_business_model(business_name: str):
    """
    🗑️ **Delete Business Model**
    
    Delete a business model and all associated data.
    """
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )
        
        success = db.delete_business_model(business_name)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Business model not found: {business_name}"
            )
        
        # TODO: Also delete model files from disk
        
        logger.info(f"Deleted business model: {business_name}")
        return {
            "success": True,
            "message": f"Business model '{business_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting business model {business_name}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting business model: {str(e)}"
        )

@app.get("/stats")
async def get_system_stats():
    """
    📊 **System Statistics**
    
    Get overall system statistics and performance metrics.
    """
    try:
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )
        
        stats = db.get_business_stats()
        
        return {
            "success": True,
            "stats": stats,
            "api_version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting system stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )

@app.post("/test-segmentation")
async def test_segmentation():
    """
    🧪 Test endpoint for debugging segmentation issues
    """
    try:
        # Create sample data
        sample_data = {
            "success": True,
            "message": "Test segmentation completed successfully",
            "analytics": {
                "n_customers": 100,
                "n_rows": 500,
                "cluster_counts": {
                    "Champions": 25,
                    "Loyal Customers": 30,
                    "At-Risk VIPs": 20,
                    "Lost Customers": 25
                },
                "revenue_by_segment": {
                    "Champions": 50000.0,
                    "Loyal Customers": 35000.0,
                    "At-Risk VIPs": 15000.0,
                    "Lost Customers": 5000.0
                },
                "avg_rfm": [
                    {"Segment": "Champions", "Recency": 15.5, "Frequency": 8.2, "Monetary": 2000.0},
                    {"Segment": "Loyal Customers", "Recency": 25.3, "Frequency": 6.1, "Monetary": 1200.0},
                    {"Segment": "At-Risk VIPs", "Recency": 85.7, "Frequency": 4.5, "Monetary": 750.0},
                    {"Segment": "Lost Customers", "Recency": 180.2, "Frequency": 2.1, "Monetary": 200.0}
                ],
                "model_performance": {
                    "silhouette_score": 0.65,
                    "n_clusters": 4,
                    "inertia": 1250.5
                }
            },
            "preview": [
                {"CustomerID": 12345, "Recency": 15, "Frequency": 8, "Monetary": 2000, "Cluster": 0, "Segment": "Champions"},
                {"CustomerID": 12346, "Recency": 25, "Frequency": 6, "Monetary": 1200, "Cluster": 1, "Segment": "Loyal Customers"},
                {"CustomerID": 12347, "Recency": 85, "Frequency": 4, "Monetary": 750, "Cluster": 2, "Segment": "At-Risk VIPs"},
                {"CustomerID": 12348, "Recency": 180, "Frequency": 2, "Monetary": 200, "Cluster": 3, "Segment": "Lost Customers"}
            ],
            "business_name": "test_business",
            "processing_summary": {
                "original_rows": 500,
                "customers_segmented": 100,
                "segments_identified": 4
            }
        }
        
        logger.info("Test segmentation endpoint called - returning sample data")
        return JSONResponse(content=sample_data)
        
    except Exception as e:
        logger.error(f"Error in test endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# For standalone execution
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Customer Segmentation API server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
