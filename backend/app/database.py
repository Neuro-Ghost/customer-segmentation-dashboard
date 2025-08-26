"""
Database Management for Business Models
======================================

This module handles the storage and retrieval of business-specific customer
segmentation models. It uses SQLite for simplicity but can be easily extended
to other databases.

Features:
- Store business model metadata
- Track model performance metrics
- Manage column mappings
- Business model versioning
- Comprehensive error handling

Author: Customer Segmentation Team
Date: August 2025
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Optional, List, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BusinessModelDB:
    """
    Database manager for business-specific customer segmentation models.
    
    This class handles all database operations for storing and retrieving
    business model information, column mappings, and performance metrics.
    """
    
    def __init__(self, db_path: str = "business_models.db"):
        """
        Initialize the database connection and create tables if needed.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        logger.info(f"Initializing BusinessModelDB with database: {db_path}")
        
        try:
            self.init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def init_db(self):
        """
        Initialize the database with required tables.
        
        Creates the business_models table with all necessary fields
        for tracking business model information.
        """
        try:
            logger.info("Creating database tables...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create the main business models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS business_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT UNIQUE NOT NULL,
                    column_mappings TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    scaler_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    n_customers INTEGER DEFAULT 0,
                    n_transactions INTEGER DEFAULT 0,
                    performance_metrics TEXT,
                    model_version TEXT DEFAULT '1.0',
                    notes TEXT
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_business_name 
                ON business_models(business_name)
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_business_model(self, business_name: str, column_mappings: Dict[str, str], 
                          model_info: Dict[str, Any]) -> bool:
        """
        Save or update business model information in the database.
        
        Args:
            business_name (str): Unique business identifier
            column_mappings (Dict[str, str]): Column mapping configuration
            model_info (Dict[str, Any]): Model paths and performance metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Saving business model for: {business_name}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Prepare data for insertion
            current_time = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO business_models 
                (business_name, column_mappings, model_path, scaler_path, 
                 n_customers, n_transactions, performance_metrics, 
                 model_version, notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                business_name,
                json.dumps(column_mappings),
                model_info.get('model_path', ''),
                model_info.get('scaler_path', ''),
                model_info.get('n_customers', 0),
                model_info.get('n_transactions', 0),
                json.dumps(model_info.get('performance_metrics', {})),
                model_info.get('model_version', '1.0'),
                model_info.get('notes', ''),
                current_time
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Business model saved successfully: {business_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving business model for {business_name}: {str(e)}")
            return False
    
    def get_business_model(self, business_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve business model information from the database.
        
        Args:
            business_name (str): Business identifier to lookup
            
        Returns:
            Optional[Dict[str, Any]]: Business model data or None if not found
        """
        try:
            logger.info(f"Retrieving business model for: {business_name}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM business_models WHERE business_name = ?", 
                (business_name,)
            )
            result = cursor.fetchone()
            conn.close()
            
            if result:
                # Map database columns to dictionary
                columns = [
                    'id', 'business_name', 'column_mappings', 'model_path', 
                    'scaler_path', 'created_at', 'updated_at', 'n_customers', 
                    'n_transactions', 'performance_metrics', 'model_version', 'notes'
                ]
                business_data = dict(zip(columns, result))
                
                # Parse JSON fields
                try:
                    business_data['column_mappings'] = json.loads(business_data['column_mappings'])
                    business_data['performance_metrics'] = json.loads(business_data['performance_metrics'])
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing JSON for {business_name}: {str(e)}")
                    business_data['column_mappings'] = {}
                    business_data['performance_metrics'] = {}
                
                logger.info(f"Business model retrieved successfully: {business_name}")
                return business_data
            else:
                logger.info(f"No business model found for: {business_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving business model for {business_name}: {str(e)}")
            return None
    
    def list_businesses(self) -> List[Dict[str, Any]]:
        """
        List all businesses in the database.
        
        Returns:
            List[Dict[str, Any]]: List of business summaries
        """
        try:
            logger.info("Retrieving list of all businesses...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT business_name, created_at, updated_at, n_customers, 
                       n_transactions, model_version, notes 
                FROM business_models 
                ORDER BY updated_at DESC
            ''')
            results = cursor.fetchall()
            conn.close()
            
            businesses = []
            for row in results:
                businesses.append({
                    'business_name': row[0],
                    'created_at': row[1],
                    'updated_at': row[2],
                    'n_customers': row[3],
                    'n_transactions': row[4],
                    'model_version': row[5],
                    'notes': row[6]
                })
            
            logger.info(f"Retrieved {len(businesses)} businesses")
            return businesses
            
        except Exception as e:
            logger.error(f"Error listing businesses: {str(e)}")
            return []
    
    def delete_business_model(self, business_name: str) -> bool:
        """
        Delete a business model from the database.
        
        Args:
            business_name (str): Business to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Deleting business model: {business_name}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM business_models WHERE business_name = ?",
                (business_name,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Business model deleted successfully: {business_name}")
                return True
            else:
                logger.warning(f"No business model found to delete: {business_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting business model {business_name}: {str(e)}")
            return False
    
    def update_model_performance(self, business_name: str, 
                               performance_metrics: Dict[str, Any]) -> bool:
        """
        Update only the performance metrics for a business model.
        
        Args:
            business_name (str): Business identifier
            performance_metrics (Dict[str, Any]): Updated metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Updating performance metrics for: {business_name}")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE business_models 
                SET performance_metrics = ?, updated_at = ?
                WHERE business_name = ?
            ''', (
                json.dumps(performance_metrics),
                datetime.now().isoformat(),
                business_name
            ))
            
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if updated_count > 0:
                logger.info(f"Performance metrics updated successfully: {business_name}")
                return True
            else:
                logger.warning(f"No business model found to update: {business_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating performance metrics for {business_name}: {str(e)}")
            return False
    
    def get_business_stats(self) -> Dict[str, Any]:
        """
        Get overall statistics about stored business models.
        
        Returns:
            Dict[str, Any]: Database statistics
        """
        try:
            logger.info("Calculating business model statistics...")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic counts
            cursor.execute("SELECT COUNT(*) FROM business_models")
            total_businesses = cursor.fetchone()[0]
            
            # Get total customers across all businesses
            cursor.execute("SELECT SUM(n_customers) FROM business_models")
            total_customers = cursor.fetchone()[0] or 0
            
            # Get total transactions across all businesses
            cursor.execute("SELECT SUM(n_transactions) FROM business_models")
            total_transactions = cursor.fetchone()[0] or 0
            
            # Get most recent update
            cursor.execute("SELECT MAX(updated_at) FROM business_models")
            last_update = cursor.fetchone()[0]
            
            conn.close()
            
            stats = {
                'total_businesses': total_businesses,
                'total_customers': total_customers,
                'total_transactions': total_transactions,
                'last_update': last_update,
                'database_path': self.db_path,
                'database_size_mb': round(os.path.getsize(self.db_path) / (1024*1024), 2) if os.path.exists(self.db_path) else 0
            }
            
            logger.info("Statistics calculated successfully")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {
                'error': str(e),
                'total_businesses': 0,
                'total_customers': 0,
                'total_transactions': 0
            }
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create a backup of the database.
        
        Args:
            backup_path (str): Path for the backup file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"Creating database backup at: {backup_path}")
            
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info("Database backup created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating database backup: {str(e)}")
            return False
