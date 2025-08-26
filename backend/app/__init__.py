"""
Customer Segmentation Backend Application
========================================

This package contains the FastAPI backend for customer segmentation analysis.
It provides intelligent RFM-based clustering with automatic segment naming
and comprehensive business insights.

Modules:
- main: FastAPI application and route definitions
- preprocessing_v2: Enhanced data processing with intelligent segmentation
- column_mapping: Flexible column mapping system
- database: Business model persistence
- find_optimal_clusters_fixed: Automatic cluster optimization
- config: Application configuration
- schemas: Pydantic models for API requests/responses
- utils: Utility functions and helpers

Author: Customer Segmentation Team
Date: August 2025
"""

__version__ = "2.0.0"
__author__ = "Customer Segmentation Team"
__email__ = "support@customersegmentation.com"

# Package metadata
__all__ = [
    "main",
    "preprocessing_v2", 
    "column_mapping",
    "database",
    "find_optimal_clusters_fixed",
    "config",
    "schemas",
    "utils"
]
