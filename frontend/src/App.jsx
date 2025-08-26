/**
 * Enhanced Customer Segmentation Dashboard
 * =======================================
 * 
 * Main application component with multi-step workflow:
 * 1. File Upload
 * 2. Column Mapping 
 * 3. Results Display
 * 
 * Features:
 * - Intelligent column mapping
 * - Business-specific model training
 * - Comprehensive error handling
 * - Real-time progress tracking
 * - Professional UI/UX
 * 
 * Author: Customer Segmentation Team
 * Date: August 2025
 */

import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import ColumnMapping from "./components/ColumnMapping";
import KPIs from "./components/KPIs";
import SegmentCharts from "./components/SegmentCharts";
import TopProducts from "./components/TopProducts";
import CustomerTable from "./components/CustomerTable";
import CustomVisualization from "./components/CustomVisualization";
import "./App.css";

// API base URL - adjust for your environment
const API_BASE_URL = "http://127.0.0.1:8050";

export default function App() {
  // Application state management
  const [step, setStep] = useState('upload'); // 'upload', 'mapping', 'results'
  const [columnAnalysis, setColumnAnalysis] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [processingStep, setProcessingStep] = useState('');
  const [activeTab, setActiveTab] = useState('overview'); // 'overview', 'custom', 'data'

  /**
   * Handle file selection and column analysis
   */
  const handleFileSelect = async (file) => {
    console.log("🔄 Starting file analysis for:", file.name);
    
    setLoading(true);
    setError(null);
    setUploadedFile(file);
    setProcessingStep('Analyzing CSV columns...');

    try {
      const formData = new FormData();
      formData.append('file', file);

      console.log("📤 Sending file to backend for analysis...");
      const response = await fetch(`${API_BASE_URL}/analyze-columns`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to analyze columns`);
      }

      const analysis = await response.json();
      console.log("✅ Column analysis completed:", analysis);

      setColumnAnalysis(analysis);
      setStep('mapping');
      setProcessingStep('');

    } catch (err) {
      console.error("❌ Error analyzing file:", err);
      setError(`Error analyzing file: ${err.message}`);
      setProcessingStep('');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle mapping completion and data processing
   */
  const handleMappingComplete = async (mappings, businessName) => {
    console.log("🔄 Starting data processing with mappings:", { businessName, mappings });
    
    setLoading(true);
    setError(null);
    setProcessingStep('Processing data with your mappings...');

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('business_name', businessName);
      formData.append('column_mappings', JSON.stringify(mappings));
      formData.append('retrain_model', 'true');
      formData.append('notes', `Analysis created on ${new Date().toISOString()}`);

      console.log("📤 Sending data for segmentation processing...");
      setProcessingStep('Cleaning and validating data...');

      const response = await fetch(`${API_BASE_URL}/segment-with-mapping`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP ${response.status}: Failed to process segmentation`);
      }

      setProcessingStep('Calculating RFM features...');
      const result = await response.json();
      
      setProcessingStep('Generating clusters and analytics...');
      console.log("✅ Segmentation completed successfully:", result);

      setData(result);
      setStep('results');
      setProcessingStep('');

    } catch (err) {
      console.error("❌ Error processing segmentation:", err);
      setError(`Error processing segmentation: ${err.message}`);
      setProcessingStep('');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Start over with new data
   */
  const handleStartOver = () => {
    console.log("🔄 Starting over - resetting application state");
    
    setStep('upload');
    setColumnAnalysis(null);
    setUploadedFile(null);
    setData(null);
    setError(null);
    setProcessingStep('');
    setLoading(false);
  };

  /**
   * Retry current step
   */
  const handleRetry = () => {
    setError(null);
    if (step === 'mapping' && uploadedFile) {
      handleFileSelect(uploadedFile);
    }
  };

  return (
    <div className="app">
      {/* Application Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🎯 Customer Segmentation Dashboard</h1>
          <p className="header-subtitle">
            Advanced RFM Analysis with Intelligent Column Mapping
          </p>
          
          {/* Progress Indicator */}
          <div className="progress-indicator">
            <div className={`progress-step ${step === 'upload' ? 'active' : step !== 'upload' ? 'completed' : ''}`}>
              <span className="step-number">1</span>
              <span className="step-label">Upload</span>
            </div>
            <div className="progress-line"></div>
            <div className={`progress-step ${step === 'mapping' ? 'active' : step === 'results' ? 'completed' : ''}`}>
              <span className="step-number">2</span>
              <span className="step-label">Mapping</span>
            </div>
            <div className="progress-line"></div>
            <div className={`progress-step ${step === 'results' ? 'active' : ''}`}>
              <span className="step-number">3</span>
              <span className="step-label">Results</span>
            </div>
          </div>
        </div>
      </header>

      <main className="app-main">
        {/* Loading Overlay */}
        {loading && (
          <div className="loading-overlay">
            <div className="loading-content">
              <div className="loading-spinner"></div>
              <h3>Processing Your Data</h3>
              <p>{processingStep || 'Please wait while we process your data...'}</p>
              <div className="loading-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-container">
            <div className="error-content">
              <h3>⚠️ Something went wrong</h3>
              <p className="error-message">{error}</p>
              <div className="error-actions">
                <button onClick={handleRetry} className="retry-btn">
                  🔄 Try Again
                </button>
                <button onClick={handleStartOver} className="start-over-btn">
                  🏠 Start Over
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 1: File Upload */}
        {step === 'upload' && !loading && !error && (
          <div className="step-container">
            <div className="step-header">
              <h2>📁 Upload Your Customer Data</h2>
              <p>
                Upload your CSV file containing customer transaction data. 
                We'll analyze your columns and help you map them to our standard format.
              </p>
            </div>
            <FileUpload onUpload={handleFileSelect} />
            
            <div className="requirements-info">
              <h3>📋 Data Requirements</h3>
              <div className="requirements-grid">
                <div className="requirement-column">
                  <h4>Required Columns</h4>
                  <ul>
                    <li><strong>Invoice/Transaction ID</strong> - Unique identifier for each purchase</li>
                    <li><strong>Customer ID</strong> - Unique identifier for each customer</li>
                    <li><strong>Quantity</strong> - Number of items purchased</li>
                    <li><strong>Unit Price</strong> - Price per item</li>
                    <li><strong>Date</strong> - Transaction date and time</li>
                  </ul>
                </div>
                <div className="requirement-column">
                  <h4>Optional Columns</h4>
                  <ul>
                    <li><strong>Product Code</strong> - SKU or product identifier</li>
                    <li><strong>Description</strong> - Product description</li>
                    <li><strong>Country</strong> - Customer location</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Column Mapping */}
        {step === 'mapping' && columnAnalysis && !loading && !error && (
          <div className="step-container">
            <div className="step-header">
              <h2>🔗 Map Your Columns</h2>
              <p>
                We've analyzed your CSV and provided smart suggestions. 
                Please review and adjust the mappings to ensure accurate analysis.
              </p>
            </div>
            <ColumnMapping
              detectedColumns={columnAnalysis.detected_columns}
              coreRequiredColumns={columnAnalysis.core_required_columns}
              recommendedColumns={columnAnalysis.recommended_columns}
              optionalColumns={columnAnalysis.optional_columns}
              suggestions={columnAnalysis.suggestions}
              analysisModes={columnAnalysis.analysis_modes}
              onMappingComplete={handleMappingComplete}
              loading={loading}
            />
          </div>
        )}

        {/* Step 3: Results Display */}
        {step === 'results' && data && !loading && !error && (
          <div className="results-container">
            <div className="results-header">
              <h2>📊 Segmentation Results</h2>
              <div className="results-summary">
                <span className="summary-item">
                  🏢 <strong>{data.business_name}</strong>
                </span>
                <span className="summary-item">
                  👥 <strong>{data.analytics.n_customers}</strong> customers segmented
                </span>
                <span className="summary-item">
                  📈 <strong>{Object.keys(data.analytics.cluster_counts).length}</strong> segments identified
                </span>
              </div>
              <button onClick={handleStartOver} className="new-analysis-btn">
                ➕ New Analysis
              </button>
            </div>

            {/* Model Performance Metrics */}
            {data.analytics.model_performance && (
              <div className="performance-metrics">
                <h3>🎯 Model Performance</h3>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <span className="metric-label">Silhouette Score</span>
                    <span className="metric-value">
                      {data.analytics.model_performance.silhouette_score?.toFixed(3)}
                    </span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-label">Clusters</span>
                    <span className="metric-value">
                      {data.analytics.model_performance.n_clusters}
                    </span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-label">Model Type</span>
                    <span className="metric-value">K-Means</span>
                  </div>
                </div>
              </div>
            )}

            {/* Tabbed Interface */}
            <div className="results-tabs">
              <div className="tab-navigation">
                <button 
                  className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  📊 Overview & Analytics
                </button>
                <button 
                  className={`tab-button ${activeTab === 'custom' ? 'active' : ''}`}
                  onClick={() => setActiveTab('custom')}
                >
                  🎨 Custom Visualizations
                </button>
                <button 
                  className={`tab-button ${activeTab === 'data' ? 'active' : ''}`}
                  onClick={() => setActiveTab('data')}
                >
                  📋 Customer Data
                </button>
              </div>

              <div className="tab-content">
                {/* Overview Tab */}
                {activeTab === 'overview' && (
                  <>
                    <KPIs analytics={data.analytics} />
                    
                    <div className="charts-section">
                      <SegmentCharts analytics={data.analytics} />
                      {data.analytics.top_products_per_segment && (
                        <TopProducts topProducts={data.analytics.top_products_per_segment} />
                      )}
                    </div>
                  </>
                )}

                {/* Custom Visualizations Tab */}
                {activeTab === 'custom' && (
                  <CustomVisualization data={data.preview} />
                )}

                {/* Data Tab */}
                {activeTab === 'data' && (
                  <div className="table-section">
                    <h3>📋 Customer Segmentation Data</h3>
                    <p>Sample of segmented customers with their RFM scores and cluster assignments</p>
                    <CustomerTable preview={data.preview} />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          🚀 Powered by Advanced RFM Analysis | 
          📊 {data ? `${data.analytics.n_customers} customers analyzed` : 'Ready to analyze your data'}
        </p>
      </footer>
    </div>
  );
}
