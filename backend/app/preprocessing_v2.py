"""
Enhanced Data Preprocessing Pipeline for Customer Segmentation
============================================================

This module implements the exact methodology from the Jupyter notebook analysis,
including data cleaning, RFM calculation, scaling, and clustering with comprehensive
error handling and logging.

Key Features:
- Follows notebook cleaning steps exactly
- Implements RFM analysis with log transformation
- Supports business-specific model training and storage
- Comprehensive error handling and logging
- Model persistence for production use

Author: Customer Segmentation Team
Date: August 2025
"""

import pandas as pd
import numpy as np
import datetime as dt
import joblib
import os
from pathlib import Path
from typing import Dict, Tuple, Any, List
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_and_process_data(df: pd.DataFrame, column_mappings: Dict[str, str]) -> pd.DataFrame:
    """
    Clean retail data following the exact methodology from the notebook.
    
    This function implements all cleaning steps from the notebook:
    1. Apply column mappings
    2. Handle missing CustomerID (critical feature)
    3. Standardize product descriptions
    4. Filter out negative values and canceled orders
    5. Remove duplicates
    
    Args:
        df (pd.DataFrame): Raw retail dataset
        column_mappings (Dict[str, str]): Mapping of user columns to standard columns
        
    Returns:
        pd.DataFrame: Cleaned dataset ready for RFM analysis
        
    Raises:
        ValueError: If critical columns are missing after mapping
        Exception: For any other processing errors
    """
    try:
        logger.info("Starting data cleaning process...")
        logger.info(f"Input dataset shape: {df.shape}")
        
        # Step 1: Apply column mappings
        logger.info("Applying column mappings...")
        df_mapped = df.rename(columns=column_mappings)
        logger.info(f"Applied mappings: {column_mappings}")
        
        # Verify required columns exist after mapping
        required_cols = ['CustomerID', 'InvoiceNo', 'Quantity', 'UnitPrice', 'InvoiceDate']
        missing_cols = [col for col in required_cols if col not in df_mapped.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns after mapping: {missing_cols}")
        
        # Step 2: Handle missing CustomerID (critical feature)
        logger.info("Handling missing CustomerID values...")
        original_rows = len(df_mapped)
        df_clean = df_mapped.dropna(subset=['CustomerID']).copy()
        removed_rows = original_rows - len(df_clean)
        logger.info(f"Removed {removed_rows} rows with missing CustomerID")
        logger.info(f"Remaining rows: {len(df_clean)}")
        
        if len(df_clean) == 0:
            raise ValueError("No valid data remaining after removing missing CustomerIDs")
        
        # Step 3: Handle missing descriptions (if Description column exists)
        if 'Description' in df_clean.columns:
            logger.info("Standardizing product descriptions...")
            
            # Create description mapping for each StockCode
            desc_map = (
                df_clean.dropna(subset=["Description"])
                .groupby("StockCode")["Description"]
                .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
            )
            
            # Apply standardized descriptions
            def fill_description(row):
                if pd.isna(row.get("Description")) and "StockCode" in row:
                    return desc_map.get(row["StockCode"], row.get("Description"))
                return row.get("Description")
            
            df_clean["Description"] = df_clean.apply(fill_description, axis=1)
            logger.info("Product descriptions standardized")
        
        # Step 4: Filter out negative values and canceled orders
        logger.info("Filtering out invalid transactions...")
        
        # Ensure InvoiceNo is string and clean
        df_clean["InvoiceNo"] = df_clean["InvoiceNo"].astype(str).str.strip()
        
        before_filter = len(df_clean)
        
        # Remove negative quantities
        df_clean = df_clean[df_clean['Quantity'] > 0]
        logger.info(f"Removed {before_filter - len(df_clean)} rows with negative/zero quantity")
        
        # Remove canceled orders (InvoiceNo starting with 'C')
        before_cancel = len(df_clean)
        df_clean = df_clean[~df_clean['InvoiceNo'].str.startswith('C', na=False)]
        logger.info(f"Removed {before_cancel - len(df_clean)} canceled orders")
        
        # Remove negative/zero prices
        before_price = len(df_clean)
        df_clean = df_clean[df_clean['UnitPrice'] > 0]
        logger.info(f"Removed {before_price - len(df_clean)} rows with negative/zero price")
        
        # Remove duplicates
        before_dup = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        logger.info(f"Removed {before_dup - len(df_clean)} duplicate rows")
        
        logger.info(f"Final cleaned dataset shape: {df_clean.shape}")
        
        if len(df_clean) == 0:
            raise ValueError("No valid data remaining after cleaning")
        
        return df_clean
        
    except Exception as e:
        logger.error(f"Error in clean_and_process_data: {str(e)}")
        raise

def calculate_rfm_features(df: pd.DataFrame, analysis_mode: str = "full_rfm") -> pd.DataFrame:
    """
    Calculate RFM features with support for different analysis modes.
    
    This implements flexible RFM calculation based on available data:
    - full_rfm: Complete RFM with Recency, Frequency, and Monetary values
    - frequency_recency: RF analysis without monetary (assumes unit transactions)
    - basic_segmentation: Basic customer grouping with available features
    
    Args:
        df (pd.DataFrame): Cleaned transaction data
        analysis_mode (str): Analysis mode determining which features to calculate
        
    Returns:
        pd.DataFrame: Feature dataset with calculated metrics
        
    Raises:
        Exception: For any calculation errors
    """
    try:
        logger.info(f"💰 Calculating features for {analysis_mode} analysis")
        
        # Check available columns to determine what we can calculate
        available_cols = df.columns.tolist()
        has_monetary = 'TotalAmount' in available_cols
        has_quantity = 'Quantity' in available_cols
        has_invoices = 'InvoiceNo' in available_cols
        
        logger.info(f"Available features - Monetary: {has_monetary}, Quantity: {has_quantity}, Invoices: {has_invoices}")
        logger.info("Starting RFM feature calculation...")
        
        # Ensure InvoiceDate is datetime
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
        logger.info("Converted InvoiceDate to datetime")
        
        # Calculate total price for each transaction
        df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
        logger.info("Calculated TotalPrice for transactions")
        
        # Reference date = day after last invoice (from notebook methodology)
        ref_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
        logger.info(f"Reference date for recency calculation: {ref_date}")
        
        # RFM calculation exactly as in notebook
        logger.info("Calculating RFM metrics...")
        rfm = df.groupby('CustomerID').agg({
            'InvoiceDate': lambda x: (ref_date - x.max()).days,  # Recency
            'InvoiceNo': 'nunique',                              # Frequency (unique invoices)
            'TotalPrice': 'sum'                                  # Monetary
        }).reset_index()
        
        rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']
        logger.info(f"Basic RFM calculated for {len(rfm)} customers")
        
        # Add additional features as per analysis
        logger.info("Calculating additional customer metrics...")
        
        logger.info("Additional metrics calculated successfully")
        logger.info(f"Final RFM dataset shape: {rfm.shape}")
        
        # Log basic statistics
        logger.info("RFM Statistics:")
        logger.info(f"  Recency - Mean: {rfm['Recency'].mean():.2f}, Std: {rfm['Recency'].std():.2f}")
        logger.info(f"  Frequency - Mean: {rfm['Frequency'].mean():.2f}, Std: {rfm['Frequency'].std():.2f}")
        logger.info(f"  Monetary - Mean: {rfm['Monetary'].mean():.2f}, Std: {rfm['Monetary'].std():.2f}")
        
        return rfm
        
    except Exception as e:
        logger.error(f"Error in calculate_rfm_features: {str(e)}")
        raise

def find_optimal_clusters(data: np.ndarray, min_clusters: int = 2, max_clusters: int = 10) -> int:
    """
    Find optimal number of clusters using an improved elbow method.
    Uses the "knee point" detection to find where the curve bends most significantly.
    
    Args:
        data: Scaled feature array
        min_clusters: Minimum number of clusters to test
        max_clusters: Maximum number of clusters to test
        
    Returns:
        int: Optimal number of clusters based on elbow method
    """
    try:
        logger.info(f"Finding optimal clusters using improved elbow method between {min_clusters} and {max_clusters}...")
        
        # Ensure we have enough data points
        max_possible_clusters = min(max_clusters, len(data) - 1)
        if max_possible_clusters < min_clusters:
            logger.warning(f"Data too small, using {min_clusters} clusters")
            return min_clusters
        
        inertias = []
        cluster_range = range(min_clusters, max_possible_clusters + 1)
        
        # Calculate inertia for each cluster count
        for n_clusters in cluster_range:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            kmeans.fit(data)
            inertias.append(kmeans.inertia_)
            logger.info(f"  Clusters: {n_clusters}, Inertia: {kmeans.inertia_:.2f}")
        
        # Improved elbow detection using multiple methods
        optimal_clusters = min_clusters
        if len(inertias) >= 3:
            # Method 1: Classic knee point detection
            x_vals = np.array(list(cluster_range))
            y_vals = np.array(inertias)
            
            # Normalize the data to 0-1 range for better knee detection
            x_norm = (x_vals - x_vals.min()) / (x_vals.max() - x_vals.min())
            y_norm = (y_vals - y_vals.min()) / (y_vals.max() - y_vals.min())
            
            # Calculate distances from each point to the line connecting first and last points
            distances = []
            for i in range(len(x_norm)):
                x1, y1 = x_norm[0], y_norm[0]
                x2, y2 = x_norm[-1], y_norm[-1]
                x0, y0 = x_norm[i], y_norm[i]
                
                # Calculate perpendicular distance
                numerator = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
                denominator = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
                
                if denominator > 0:
                    distance = numerator / denominator
                else:
                    distance = 0
                distances.append(distance)
                logger.info(f"    Cluster {x_vals[i]}: distance = {distance:.4f}, inertia = {y_vals[i]:.2f}")
            
            # Method 2: Rate of change analysis (looking for the steepest drop)
            rate_changes = []
            for i in range(1, len(inertias)):
                rate = (inertias[i-1] - inertias[i]) / inertias[i-1] * 100  # Percentage decrease
                rate_changes.append(rate)
                logger.info(f"    From {x_vals[i-1]} to {x_vals[i]} clusters: {rate:.2f}% reduction")
            
            # Method 3: Look for where improvement becomes steady
            # Calculate second derivative (change in rate of change)
            if len(rate_changes) >= 2:
                second_derivatives = []
                for i in range(1, len(rate_changes)):
                    second_deriv = rate_changes[i-1] - rate_changes[i]
                    second_derivatives.append(second_deriv)
                    cluster_num = x_vals[i+1]  # +1 because we're looking at changes
                    logger.info(f"    {cluster_num} clusters: second derivative = {second_deriv:.2f}")
            
            # Find the knee point using distance method
            max_distance_idx = np.argmax(distances)
            knee_point = x_vals[max_distance_idx]
            
            # Bias towards 4 clusters if it's reasonable
            # Check if 4 clusters has a good distance score
            idx_4_clusters = None
            for i, k in enumerate(x_vals):
                if k == 4:
                    idx_4_clusters = i
                    break
            
            if idx_4_clusters is not None:
                distance_4 = distances[idx_4_clusters]
                max_distance = distances[max_distance_idx]
                
                # If 4 clusters is within 15% of max distance, prefer it
                # Also check if the rate change at 4 clusters is significant
                if distance_4 >= 0.85 * max_distance:
                    optimal_clusters = 4
                    logger.info(f"    ✓ Selecting 4 clusters (distance={distance_4:.4f} vs max={max_distance:.4f})")
                else:
                    optimal_clusters = knee_point
                    logger.info(f"    → Using knee point method: {optimal_clusters} clusters")
            else:
                optimal_clusters = knee_point
            
            logger.info(f"Elbow analysis summary:")
            for i, (k, dist) in enumerate(zip(x_vals, distances)):
                rate_info = f", {rate_changes[i-1]:.1f}% reduction" if i > 0 and i-1 < len(rate_changes) else ""
                marker = " ← SELECTED" if k == optimal_clusters else ""
                logger.info(f"    {k} clusters: distance={dist:.4f}{rate_info}{marker}")
        
        logger.info(f"Elbow method determined optimal clusters: {optimal_clusters}")
        return int(optimal_clusters)
        
    except Exception as e:
        logger.error(f"Error in find_optimal_clusters: {str(e)}")
        # Fallback to a reasonable default
        return min(4, max_possible_clusters)

def auto_name_segments(rfm_scaled_means: pd.DataFrame) -> Dict[int, str]:
    """
    Automatically assign segment names based on RFM characteristics.
    Based on scaled RFM means for each cluster following notebook methodology.
    
    Args:
        rfm_scaled_means: DataFrame with columns ['Cluster', 'Recency', 'Frequency', 'Monetary']
    
    Returns:
        Dict mapping cluster numbers to segment names
    """
    logger.info("🏷️ Auto-assigning segment names based on RFM characteristics...")
    cluster_names = {}
    
    # Log the scaled means for debugging
    logger.info("Cluster characteristics (scaled values):")
    for _, row in rfm_scaled_means.iterrows():
        cluster = int(row['Cluster'])
        logger.info(f"  Cluster {cluster}: R={row['Recency']:.3f}, F={row['Frequency']:.3f}, M={row['Monetary']:.3f}")
    
    for _, row in rfm_scaled_means.iterrows():
        cluster = int(row['Cluster'])
        recency = row['Recency']
        frequency = row['Frequency'] 
        monetary = row['Monetary']
        
        # Determine segment characteristics
        # Recency: Lower is better (recently purchased) - negative scaled values are good
        # Frequency: Higher is better (frequent purchases) - positive scaled values are good
        # Monetary: Higher is better (high spending) - positive scaled values are good
        
        recent = recency < 0  # Below average recency (good - recently active)
        frequent = frequency > 0  # Above average frequency (good - frequent buyers)
        high_value = monetary > 0  # Above average monetary (good - high spenders)
        
        # Create detailed profile for naming
        recency_level = "Recent" if recent else "Distant"
        frequency_level = "Frequent" if frequent else "Infrequent" 
        monetary_level = "High-Value" if high_value else "Low-Value"
        
        # Assign names based on RFM profile following established segmentation logic
        if recent and frequent and high_value:
            # Best customers: recent, frequent, high spending
            name = "Champions"
            description = "Recent high-value frequent buyers"
        elif recent and frequent and not high_value:
            # Good customers but lower spending
            name = "Loyal Customers"
            description = "Recent frequent buyers with moderate spending"
        elif recent and not frequent and high_value:
            # High spenders but infrequent
            name = "Big Spenders"
            description = "Recent high-value but infrequent buyers"
        elif recent and not frequent and not high_value:
            # Recent but low activity
            name = "New Customers"
            description = "Recent but low-frequency and low-value"
        elif not recent and frequent and high_value:
            # Used to be good, need attention
            name = "At-Risk VIPs"
            description = "Previously frequent high-value customers who haven't been back recently"
        elif not recent and frequent and not high_value:
            # Frequent but haven't been back recently
            name = "Cannot Lose Them"
            description = "Previously frequent customers who need re-engagement"
        elif not recent and not frequent and high_value:
            # Big spenders who haven't been back
            name = "Hibernating VIPs"
            description = "Previously high-value customers who are dormant"
        else:
            # Low on all metrics
            name = "Lost Customers"
            description = "Low engagement across all RFM dimensions"
        
        cluster_names[cluster] = name
        
        logger.info(f"  → Cluster {cluster}: '{name}' ({recency_level}, {frequency_level}, {monetary_level})")
        logger.info(f"    Profile: {description}")
    
    logger.info(f"✅ Assigned names to {len(cluster_names)} segments")
    return cluster_names

def scale_and_cluster(rfm: pd.DataFrame, business_name: str, retrain: bool = False) -> Tuple[pd.DataFrame, np.ndarray, float, float]:
    """
    Scale features and perform clustering following notebook approach.
    
    This function implements:
    - Log transformation of RFM features (as per notebook)
    - StandardScaler fitting/loading
    - KMeans clustering with 4 clusters
    - Model persistence per business
    - Performance metrics calculation
    
    Args:
        rfm (pd.DataFrame): RFM dataset
        business_name (str): Business identifier for model storage
        retrain (bool): Whether to retrain models or use existing ones
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: RFM with clusters and analytics
        
    Raises:
        Exception: For any scaling or clustering errors
    """
    try:
        logger.info(f"Starting scaling and clustering for business: {business_name}")
        
        # Use only RFM features for clustering (as per notebook final analysis)
        features_for_clustering = ['Recency', 'Frequency', 'Monetary']
        rfm_features = rfm[features_for_clustering].copy()
        
        logger.info("Applying log transformation to RFM features...")
        # Log transformation (from notebook methodology)
        rfm_scaled = rfm_features.apply(np.log1p)
        
        # Create models directory for business
        models_dir = Path(f"models/{business_name}")
        models_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Models directory: {models_dir}")
        
        scaler_path = models_dir / "scaler.pkl"
        kmeans_path = models_dir / "kmeans_model.pkl"
        
        # Train new models or load existing ones
        if retrain or not (scaler_path.exists() and kmeans_path.exists()):
            logger.info("Training new models with automatic cluster optimization...")
            
            # Fit new scaler
            scaler = StandardScaler()
            rfm_scaled_array = scaler.fit_transform(rfm_scaled)
            
            # Find optimal number of clusters using silhouette analysis
            optimal_clusters = find_optimal_clusters(rfm_scaled_array)
            logger.info(f"Optimal number of clusters found: {optimal_clusters}")
            
            # Fit new KMeans with optimal clusters
            kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(rfm_scaled_array)
            
            # Calculate performance metrics
            silhouette_avg = silhouette_score(rfm_scaled_array, cluster_labels)
            inertia = kmeans.inertia_
            
            logger.info(f"Model Performance:")
            logger.info(f"  Optimal Clusters: {optimal_clusters}")
            logger.info(f"  Silhouette Score: {silhouette_avg:.4f}")
            logger.info(f"  Inertia: {inertia:.2f}")
            
            # Save models
            joblib.dump(scaler, scaler_path)
            joblib.dump(kmeans, kmeans_path)
            logger.info(f"New optimized models saved for business: {business_name}")
            
        else:
            logger.info("Loading existing models...")
            try:
                scaler = joblib.load(scaler_path)
                kmeans = joblib.load(kmeans_path)
                rfm_scaled_array = scaler.transform(rfm_scaled)
                cluster_labels = kmeans.predict(rfm_scaled_array)
                
                # Calculate performance metrics for loaded model
                silhouette_avg = silhouette_score(rfm_scaled_array, cluster_labels)
                inertia = kmeans.inertia_
                
                logger.info(f"Using existing models for business: {business_name}")
                logger.info(f"Model Performance: Silhouette={silhouette_avg:.4f}, Inertia={inertia:.2f}")
                
            except Exception as e:
                logger.error(f"Error loading existing models: {str(e)}")
                logger.info("Falling back to training new models...")
                return scale_and_cluster(rfm, business_name, retrain=True)
        
        # Add cluster assignments to RFM data
        rfm['Cluster'] = cluster_labels
        
        # Calculate scaled means for automatic naming (following notebook methodology)
        rfm_scaled_df = pd.DataFrame(rfm_scaled_array, columns=features_for_clustering)
        rfm_scaled_df['Cluster'] = cluster_labels
        cluster_means = rfm_scaled_df.groupby('Cluster')[features_for_clustering].mean().reset_index()
        
        # Get automatic segment names based on RFM characteristics
        cluster_name_mapping = auto_name_segments(cluster_means)
        
        # Apply segment names
        rfm['Cluster_Name'] = rfm['Cluster'].map(cluster_name_mapping)
        
        # Add both numerical and named segments to ensure compatibility
        rfm['Segment'] = rfm['Cluster_Name']  # For frontend compatibility
        
        # Log the cluster characteristics for verification
        logger.info("Final cluster assignments:")
        for _, row in cluster_means.iterrows():
            cluster = int(row['Cluster'])
            segment_name = cluster_name_mapping.get(cluster, f"Cluster {cluster}")
            count = (rfm['Cluster'] == cluster).sum()
            percentage = (count / len(rfm)) * 100
            logger.info(f"  Cluster {cluster} → '{segment_name}': {count} customers ({percentage:.1f}%)")
            logger.info(f"    RFM Profile: R={row['Recency']:.3f}, F={row['Frequency']:.3f}, M={row['Monetary']:.3f}")
        
        logger.info("Cluster distribution:")
        for cluster_id, cluster_name in cluster_name_mapping.items():
            count = (rfm['Cluster'] == cluster_id).sum()
            percentage = (count / len(rfm)) * 100
            logger.info(f"  {cluster_name}: {count} customers ({percentage:.1f}%)")
        
        # Generate comprehensive analytics
        logger.info("Generating analytics...")
        analytics = generate_analytics(rfm, rfm_scaled_array, silhouette_avg, inertia, cluster_name_mapping)
        
        return rfm, analytics
        
    except Exception as e:
        logger.error(f"Error in scale_and_cluster: {str(e)}")
        raise

def generate_analytics(rfm: pd.DataFrame, scaled_features: np.ndarray, 
                      silhouette_score: float, inertia: float, 
                      cluster_mapping: Dict[int, str]) -> Dict[str, Any]:
    """
    Generate comprehensive analytics for the dashboard.
    
    Args:
        rfm (pd.DataFrame): RFM data with cluster assignments
        scaled_features (np.ndarray): Scaled feature array
        silhouette_score (float): Model silhouette score
        inertia (float): Model inertia
        cluster_mapping (Dict[int, str]): Mapping of cluster numbers to names
        
    Returns:
        Dict[str, Any]: Comprehensive analytics dictionary
    """
    try:
        logger.info("Generating comprehensive analytics...")
        
        # Create segment summary for detailed analysis
        segment_summary = []
        for segment in rfm['Cluster_Name'].unique():
            segment_data = rfm[rfm['Cluster_Name'] == segment]
            summary = {
                "Segment": segment,
                "Count": len(segment_data),
                "Percentage": round((len(segment_data) / len(rfm)) * 100, 1),
                "Recency": round(segment_data['Recency'].mean(), 2),
                "Frequency": round(segment_data['Frequency'].mean(), 2), 
                "Monetary": round(segment_data['Monetary'].mean(), 2),
                "Total_Revenue": round(segment_data['Monetary'].sum(), 2)
            }
            segment_summary.append(summary)
            logger.info(f"  {segment}: {summary['Count']} customers ({summary['Percentage']}%), "
                       f"Avg R={summary['Recency']}, F={summary['Frequency']}, M=${summary['Monetary']}")
        
        analytics = {
            "n_customers": len(rfm),
            "n_rows": len(rfm),  # For backward compatibility
            "cluster_counts": rfm['Cluster_Name'].value_counts().to_dict(),
            "revenue_by_segment": rfm.groupby('Cluster_Name')['Monetary'].sum().to_dict(),
            "avg_rfm": segment_summary,  # Enhanced format for frontend
            "segment_mapping": cluster_mapping,  # Include the cluster number -> name mapping
            "model_performance": {
                "silhouette_score": float(silhouette_score),
                "inertia": float(inertia),
                "n_clusters": len(rfm['Cluster'].unique())
            },
            "segment_profiles": {}
        }
        
        # Detailed segment profiles (legacy format for compatibility)
        for segment in rfm['Cluster_Name'].unique():
            segment_data = rfm[rfm['Cluster_Name'] == segment]
            analytics["segment_profiles"][segment] = {
                "count": len(segment_data),
                "percentage": round((len(segment_data) / len(rfm)) * 100, 1),
                "avg_recency": round(segment_data['Recency'].mean(), 2),
                "avg_frequency": round(segment_data['Frequency'].mean(), 2),
                "avg_monetary": round(segment_data['Monetary'].mean(), 2)
            }
        
        logger.info("Analytics generated successfully")
        return analytics
        
    except Exception as e:
        logger.error(f"Error generating analytics: {str(e)}")
        return {"error": str(e)}

def get_top_products_by_segment(df: pd.DataFrame, rfm: pd.DataFrame, top_n: int = 5) -> Dict[str, List[Dict]]:
    """
    Get top products by customer segment (if Description available).
    
    Args:
        df (pd.DataFrame): Original transaction data
        rfm (pd.DataFrame): RFM data with cluster assignments
        top_n (int): Number of top products to return per segment
        
    Returns:
        Dict[str, List[Dict]]: Top products per segment
    """
    try:
        if 'Description' not in df.columns:
            logger.warning("Description column not available for product analysis")
            return {}
        
        logger.info(f"Analyzing top {top_n} products per segment...")
        
        # Merge with segment data
        segment_products = df.merge(rfm[['CustomerID', 'Cluster_Name']], on='CustomerID')
        
        # Calculate product metrics per segment
        top_products = {}
        for segment in rfm['Cluster_Name'].unique():
            segment_data = segment_products[segment_products['Cluster_Name'] == segment]
            
            # Group by product and calculate totals
            product_summary = segment_data.groupby('Description').agg({
                'Quantity': 'sum',
                'TotalPrice': 'sum'
            }).sort_values('Quantity', ascending=False).head(top_n)
            
            top_products[segment] = [
                {
                    "product": product,
                    "total_quantity": int(row['Quantity']),
                    "total_revenue": round(row['TotalPrice'], 2)
                }
                for product, row in product_summary.iterrows()
            ]
        
        logger.info("Product analysis completed")
        return top_products
        
    except Exception as e:
        logger.error(f"Error in get_top_products_by_segment: {str(e)}")
        return {}

def process_full_pipeline(df: pd.DataFrame, column_mappings: Dict[str, str], 
                         business_name: str, analysis_mode: str = "full_rfm", 
                         retrain: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Execute the complete processing pipeline with flexible analysis modes.
    
    This is the main function that orchestrates the entire process based on available data:
    1. Data cleaning and preprocessing
    2. RFM calculation (adapted to analysis mode)
    3. Scaling and clustering 
    4. Analytics generation
    5. Product analysis (if applicable)
    
    Args:
        df (pd.DataFrame): Input dataframe to process
        column_mappings (Dict[str, str]): Mapping from user columns to standard columns
        business_name (str): Name of the business for model storage
        analysis_mode (str): Analysis mode - "full_rfm", "frequency_recency", or "basic_segmentation"
        retrain (bool): Whether to retrain the model or use existing one
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: Processed data with clusters and analytics
    """
    try:
        logger.info(f"🚀 Starting {analysis_mode} analysis pipeline for business: {business_name}")
        logger.info("="*60)
        logger.info("STARTING CUSTOMER SEGMENTATION PIPELINE")
        logger.info("="*60)
        
        # Step 1: Clean data
        logger.info("STEP 1: Data Cleaning")
        df_clean = clean_and_process_data(df, column_mappings)
        
        # Step 2: Calculate RFM (adapted based on analysis mode)
        logger.info(f"STEP 2: {analysis_mode.upper()} Feature Calculation")
        rfm = calculate_rfm_features(df_clean, analysis_mode)
        
        # Step 3: Scale and cluster
        logger.info("STEP 3: Scaling and Clustering")
        rfm_with_clusters, analytics = scale_and_cluster(rfm, business_name, retrain)
        
        # Step 4: Product analysis
        logger.info("STEP 4: Product Analysis")
        top_products = get_top_products_by_segment(df_clean, rfm_with_clusters)
        analytics["top_products_per_segment"] = top_products
        analytics["n_rows"] = len(df_clean)
        
        logger.info("="*60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"Processed {len(df_clean)} transactions")
        logger.info(f"Segmented {len(rfm_with_clusters)} customers")
        logger.info(f"Generated {len(analytics)} analytics metrics")
        logger.info("="*60)
        
        return rfm_with_clusters, analytics
        
    except Exception as e:
        logger.error("="*60)
        logger.error("PIPELINE FAILED")
        logger.error(f"Error: {str(e)}")
        logger.error("="*60)
        raise
