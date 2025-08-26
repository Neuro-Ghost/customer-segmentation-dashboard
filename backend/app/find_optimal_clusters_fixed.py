"""
Optimal Cluster Detection for Customer Segmentation
================================================

This module implements the elbow method and silhouette analysis
to automatically determine the optimal number of clusters for
customer segmentation using RFM analysis.

Features:
- Elbow method implementation
- Silhouette score analysis
- Automatic optimal cluster detection
- Performance visualization data
- Robust error handling

Author: Customer Segmentation Team
Date: August 2025
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_wcss(data, max_clusters=10):
    """
    Calculate Within-Cluster Sum of Squares (WCSS) for different cluster numbers.
    
    Args:
        data (np.ndarray): Scaled RFM data
        max_clusters (int): Maximum number of clusters to test
        
    Returns:
        list: WCSS values for each cluster number
    """
    wcss = []
    cluster_range = range(1, max_clusters + 1)
    
    logger.info(f"Calculating WCSS for clusters 1 to {max_clusters}")
    
    for k in cluster_range:
        try:
            kmeans = KMeans(
                n_clusters=k,
                init='k-means++',
                max_iter=300,
                n_init=10,
                random_state=42
            )
            kmeans.fit(data)
            wcss.append(kmeans.inertia_)
            
        except Exception as e:
            logger.error(f"Error calculating WCSS for k={k}: {str(e)}")
            wcss.append(float('inf'))
    
    return wcss

def calculate_silhouette_scores(data, max_clusters=10):
    """
    Calculate silhouette scores for different cluster numbers.
    
    Args:
        data (np.ndarray): Scaled RFM data
        max_clusters (int): Maximum number of clusters to test
        
    Returns:
        list: Silhouette scores for each cluster number (starting from k=2)
    """
    silhouette_scores = []
    cluster_range = range(2, max_clusters + 1)  # Silhouette needs at least 2 clusters
    
    logger.info(f"Calculating silhouette scores for clusters 2 to {max_clusters}")
    
    for k in cluster_range:
        try:
            kmeans = KMeans(
                n_clusters=k,
                init='k-means++',
                max_iter=300,
                n_init=10,
                random_state=42
            )
            cluster_labels = kmeans.fit_predict(data)
            silhouette_avg = silhouette_score(data, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            
        except Exception as e:
            logger.error(f"Error calculating silhouette score for k={k}: {str(e)}")
            silhouette_scores.append(-1.0)  # Invalid silhouette score
    
    return silhouette_scores

def find_elbow_point(wcss_values):
    """
    Find the elbow point using the elbow method.
    
    Args:
        wcss_values (list): WCSS values for different cluster numbers
        
    Returns:
        int: Optimal number of clusters based on elbow method
    """
    try:
        # Convert to numpy array for easier calculation
        wcss = np.array(wcss_values)
        
        # Calculate the differences
        differences = np.diff(wcss)
        second_differences = np.diff(differences)
        
        # Find the point with maximum second difference (elbow)
        elbow_index = np.argmax(second_differences) + 2  # +2 because we start from k=1 and took 2 diffs
        
        logger.info(f"Elbow method suggests {elbow_index} clusters")
        return elbow_index
        
    except Exception as e:
        logger.error(f"Error finding elbow point: {str(e)}")
        return 4  # Default fallback

def find_optimal_clusters(rfm_data, max_clusters=8, method='combined'):
    """
    Find the optimal number of clusters using multiple methods.
    
    Args:
        rfm_data (pd.DataFrame): RFM data with columns ['recency', 'frequency', 'monetary']
        max_clusters (int): Maximum number of clusters to consider
        method (str): Method to use ('elbow', 'silhouette', 'combined')
        
    Returns:
        dict: Results containing optimal clusters and analysis data
    """
    try:
        logger.info(f"Finding optimal clusters using {method} method")
        
        # Prepare and scale the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(rfm_data[['recency', 'frequency', 'monetary']])
        
        # Calculate WCSS values
        wcss_values = calculate_wcss(scaled_data, max_clusters)
        
        # Calculate silhouette scores
        silhouette_scores = calculate_silhouette_scores(scaled_data, max_clusters)
        
        # Find optimal clusters based on method
        if method == 'elbow':
            optimal_clusters = find_elbow_point(wcss_values)
            
        elif method == 'silhouette':
            # Find k with highest silhouette score (k starts from 2)
            max_silhouette_index = np.argmax(silhouette_scores)
            optimal_clusters = max_silhouette_index + 2  # +2 because silhouette starts from k=2
            
        else:  # combined method
            elbow_clusters = find_elbow_point(wcss_values)
            
            # Find best silhouette score
            max_silhouette_index = np.argmax(silhouette_scores)
            silhouette_clusters = max_silhouette_index + 2
            
            # Combine the results (prefer elbow if close, otherwise use silhouette)
            if abs(elbow_clusters - silhouette_clusters) <= 1:
                optimal_clusters = elbow_clusters
            else:
                # Choose based on silhouette score quality
                if max(silhouette_scores) > 0.5:  # Good silhouette score
                    optimal_clusters = silhouette_clusters
                else:
                    optimal_clusters = elbow_clusters
        
        # Ensure optimal clusters is within reasonable range
        optimal_clusters = max(2, min(optimal_clusters, max_clusters))
        
        # Prepare results
        results = {
            'optimal_clusters': optimal_clusters,
            'method_used': method,
            'wcss_values': wcss_values,
            'silhouette_scores': silhouette_scores,
            'cluster_range': list(range(1, max_clusters + 1)),
            'silhouette_range': list(range(2, max_clusters + 1)),
            'analysis_summary': {
                'elbow_suggestion': find_elbow_point(wcss_values),
                'best_silhouette': silhouette_clusters if silhouette_scores else None,
                'max_silhouette_score': max(silhouette_scores) if silhouette_scores else None,
                'recommendation_confidence': 'high' if max(silhouette_scores) > 0.5 else 'medium'
            }
        }
        
        logger.info(f"Optimal clusters determined: {optimal_clusters} using {method} method")
        return results
        
    except Exception as e:
        logger.error(f"Error finding optimal clusters: {str(e)}")
        return {
            'optimal_clusters': 4,  # Safe default
            'method_used': method,
            'error': str(e),
            'wcss_values': [],
            'silhouette_scores': [],
            'cluster_range': [],
            'silhouette_range': []
        }

def validate_cluster_quality(rfm_data, n_clusters):
    """
    Validate the quality of clustering with the given number of clusters.
    
    Args:
        rfm_data (pd.DataFrame): RFM data
        n_clusters (int): Number of clusters to validate
        
    Returns:
        dict: Validation metrics
    """
    try:
        logger.info(f"Validating cluster quality for {n_clusters} clusters")
        
        # Scale the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(rfm_data[['recency', 'frequency', 'monetary']])
        
        # Perform clustering
        kmeans = KMeans(
            n_clusters=n_clusters,
            init='k-means++',
            max_iter=300,
            n_init=10,
            random_state=42
        )
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Calculate quality metrics
        silhouette_avg = silhouette_score(scaled_data, cluster_labels)
        wcss = kmeans.inertia_
        
        # Calculate cluster sizes
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        cluster_sizes = dict(zip(unique_labels, counts))
        
        # Check for balanced clusters (no cluster should be too small)
        min_cluster_size = min(counts)
        min_cluster_percentage = (min_cluster_size / len(rfm_data)) * 100
        
        validation = {
            'silhouette_score': silhouette_avg,
            'wcss': wcss,
            'cluster_sizes': cluster_sizes,
            'min_cluster_size': min_cluster_size,
            'min_cluster_percentage': min_cluster_percentage,
            'is_balanced': min_cluster_percentage >= 5.0,  # At least 5% per cluster
            'quality_rating': 'excellent' if silhouette_avg > 0.7 else 
                            'good' if silhouette_avg > 0.5 else 
                            'fair' if silhouette_avg > 0.3 else 'poor'
        }
        
        logger.info(f"Cluster validation complete. Quality: {validation['quality_rating']}")
        return validation
        
    except Exception as e:
        logger.error(f"Error validating cluster quality: {str(e)}")
        return {
            'error': str(e),
            'silhouette_score': -1,
            'wcss': float('inf'),
            'cluster_sizes': {},
            'is_balanced': False,
            'quality_rating': 'error'
        }
