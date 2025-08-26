"""
Column Mapping System for Customer Segmentation
==============================================

This module handles the automatic detection and mapping of user CSV columns
to our standardized column names. It provides intelligent suggestions based
on common naming patterns found in retail datasets.

Author: Customer Segmentation Team
Date: August 2025
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColumnMappingRequest(BaseModel):
    """Request model for column mapping operations"""
    business_name: str
    column_mappings: Dict[str, str]  # user_column_name -> standard_column_name

class ColumnMappingResponse(BaseModel):
    """Response model containing column analysis results"""
    core_required_columns: List[str]
    recommended_columns: List[str]
    optional_columns: List[str]
    detected_columns: List[str]
    suggestions: Dict[str, str]
    analysis_modes: Dict[str, Dict[str, Any]]  # Available analysis modes

# Standard column definitions based on retail analysis best practices
STANDARD_COLUMNS = {
    # CORE REQUIRED columns for basic RFM analysis (minimum viable dataset)
    "core_required": {
        "CustomerID": "Customer identifier - unique ID for each customer",
        "InvoiceDate": "Date and time when the transaction occurred"
    },
    # RECOMMENDED columns for enhanced analysis (will use defaults if missing)
    "recommended": {
        "InvoiceNo": "Invoice number - unique identifier for each transaction",
        "Quantity": "Quantity of products purchased in the transaction", 
        "UnitPrice": "Price per unit of the product"
    },
    # OPTIONAL columns that enhance the analysis further
    "optional": {
        "StockCode": "Product/stock code identifier for inventory tracking",
        "Description": "Product description for product analysis",
        "Country": "Customer's country for geographical segmentation"
    }
}

# Flexible column requirements based on data availability
ANALYSIS_MODES = {
    "full_rfm": {
        "required": ["CustomerID", "InvoiceDate", "Quantity", "UnitPrice"],
        "description": "Complete RFM analysis with Recency, Frequency, and Monetary values"
    },
    "frequency_recency": {
        "required": ["CustomerID", "InvoiceDate"],
        "description": "RF analysis focusing on purchase patterns and recency (assumes unit transactions)"
    },
    "basic_segmentation": {
        "required": ["CustomerID"],
        "description": "Basic customer grouping (requires additional data preprocessing)"
    }
}

def suggest_column_mapping(user_columns: List[str]) -> Dict[str, str]:
    """
    Intelligently suggest mappings based on column name similarity.
    
    This function uses pattern matching to suggest how user columns
    should map to our standard column names.
    
    Args:
        user_columns (List[str]): List of column names from user's CSV
        
    Returns:
        Dict[str, str]: Mapping of user_column -> suggested_standard_column
    """
    try:
        logger.info(f"Analyzing {len(user_columns)} user columns for mapping suggestions")
        
        suggestions = {}
        
        # Mapping patterns based on common variations found in retail datasets
        mapping_patterns = {
            "InvoiceNo": [
                "invoice", "invoice_no", "invoice_number", "invoiceno",
                "order_id", "order", "transaction_id", "trans_id", "receipt"
            ],
            "CustomerID": [
                "customer", "customer_id", "customerid", "cust_id", "custid",
                "user_id", "userid", "client_id", "clientid", "id"
            ],
            "Quantity": [
                "quantity", "qty", "amount", "count", "units", "pieces"
            ],
            "UnitPrice": [
                "price", "unit_price", "unitprice", "cost", "amount", 
                "value", "rate", "unit_cost"
            ],
            "InvoiceDate": [
                "date", "invoice_date", "invoicedate", "order_date", "orderdate",
                "transaction_date", "trans_date", "timestamp", "datetime"
            ],
            "StockCode": [
                "stock", "stock_code", "stockcode", "product_code", "productcode",
                "item_code", "itemcode", "sku", "product_id", "item_id"
            ],
            "Description": [
                "description", "desc", "product", "item", "product_name", 
                "productname", "item_name", "itemname", "product_description"
            ],
            "Country": [
                "country", "location", "region", "nation", "territory"
            ]
        }
        
        # Process each user column and find best match
        for user_col in user_columns:
            user_col_lower = user_col.lower().strip()
            logger.debug(f"Processing user column: {user_col}")
            
            # Try exact matches first, then partial matches
            for standard_col, patterns in mapping_patterns.items():
                for pattern in patterns:
                    if pattern in user_col_lower or user_col_lower in pattern:
                        suggestions[user_col] = standard_col
                        logger.debug(f"Mapped '{user_col}' -> '{standard_col}' (pattern: {pattern})")
                        break
                if user_col in suggestions:
                    break
        
        logger.info(f"Generated {len(suggestions)} mapping suggestions")
        return suggestions
        
    except Exception as e:
        logger.error(f"Error in suggest_column_mapping: {str(e)}")
        return {}

def validate_required_mappings(mappings: Dict[str, str]) -> Dict[str, any]:
    """
    Validate mappings and determine the best analysis mode based on available data.
    
    Args:
        mappings (Dict[str, str]): User's column mappings
        
    Returns:
        Dict containing validation results and recommended analysis mode
    """
    try:
        logger.info("Validating column mappings and determining analysis mode...")
        
        mapped_standard_cols = set(mappings.values())
        validation_result = {
            "is_valid": False,
            "analysis_mode": None,
            "missing_columns": [],
            "available_columns": list(mapped_standard_cols),
            "warnings": [],
            "recommendations": []
        }
        
        # Check which analysis modes are possible
        possible_modes = []
        for mode_name, mode_config in ANALYSIS_MODES.items():
            required_cols = set(mode_config["required"])
            if required_cols.issubset(mapped_standard_cols):
                possible_modes.append({
                    "mode": mode_name,
                    "description": mode_config["description"],
                    "missing": []
                })
            else:
                missing = list(required_cols - mapped_standard_cols)
                possible_modes.append({
                    "mode": mode_name,
                    "description": mode_config["description"],
                    "missing": missing
                })
        
        # Find the best available mode (prefer full analysis)
        available_modes = [mode for mode in possible_modes if not mode["missing"]]
        
        if available_modes:
            # Choose the most comprehensive mode available
            if any(mode["mode"] == "full_rfm" for mode in available_modes):
                best_mode = "full_rfm"
            elif any(mode["mode"] == "frequency_recency" for mode in available_modes):
                best_mode = "frequency_recency"
            else:
                best_mode = "basic_segmentation"
                
            validation_result.update({
                "is_valid": True,
                "analysis_mode": best_mode,
                "mode_description": ANALYSIS_MODES[best_mode]["description"]
            })
            
            logger.info(f"Selected analysis mode: {best_mode}")
            
            # Add recommendations for missing optional columns
            all_standard_cols = {**STANDARD_COLUMNS["core_required"], 
                               **STANDARD_COLUMNS["recommended"], 
                               **STANDARD_COLUMNS["optional"]}
            
            for col_name, description in all_standard_cols.items():
                if col_name not in mapped_standard_cols:
                    if col_name in STANDARD_COLUMNS["recommended"]:
                        validation_result["warnings"].append(
                            f"Missing recommended column '{col_name}': {description}"
                        )
                    elif col_name in STANDARD_COLUMNS["optional"]:
                        validation_result["recommendations"].append(
                            f"Optional column '{col_name}' could enhance analysis: {description}"
                        )
            
        else:
            # No valid analysis mode possible
            core_required = set(STANDARD_COLUMNS["core_required"].keys())
            missing_core = list(core_required - mapped_standard_cols)
            
            validation_result.update({
                "missing_columns": missing_core,
                "error_message": f"Cannot perform analysis. Missing critical columns: {', '.join(missing_core)}"
            })
            
            logger.warning(f"Validation failed. Missing core columns: {missing_core}")
        
        validation_result["possible_modes"] = possible_modes
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating required mappings: {str(e)}")
        return {
            "is_valid": False,
            "error_message": f"Validation error: {str(e)}",
            "missing_columns": list(STANDARD_COLUMNS["core_required"].keys()),
            "available_columns": [],
            "warnings": [],
            "recommendations": []
        }

def get_column_description(standard_column: str) -> str:
    """
    Get description for a standard column.
    
    Args:
        standard_column (str): Name of the standard column
        
    Returns:
        str: Description of the column
    """
    try:
        all_columns = {
            **STANDARD_COLUMNS["core_required"], 
            **STANDARD_COLUMNS["recommended"],
            **STANDARD_COLUMNS["optional"]
        }
        return all_columns.get(standard_column, "No description available")
    except Exception as e:
        logger.error(f"Error getting column description: {str(e)}")
        return "Error retrieving description"

def get_analysis_mode_info(mode: str) -> Dict[str, any]:
    """
    Get detailed information about an analysis mode.
    
    Args:
        mode (str): Analysis mode name
        
    Returns:
        Dict containing mode information
    """
    try:
        if mode in ANALYSIS_MODES:
            mode_info = ANALYSIS_MODES[mode].copy()
            mode_info["name"] = mode
            return mode_info
        else:
            logger.warning(f"Unknown analysis mode: {mode}")
            return {
                "name": mode,
                "required": [],
                "description": "Unknown analysis mode"
            }
    except Exception as e:
        logger.error(f"Error getting analysis mode info: {str(e)}")
        return {
            "name": mode,
            "required": [],
            "description": "Error retrieving mode information"
        }
