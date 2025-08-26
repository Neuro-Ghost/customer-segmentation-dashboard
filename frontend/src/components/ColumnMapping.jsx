/**
 * Column Mapping Component
 * =======================
 * 
 * This component allows users to map their CSV columns to our standard format.
 * It provides intelligent suggestions and validates required mappings.
 * 
 * Fea                  className={`mapping-dropdown ${
                    mappings[userCol] && [...coreRequiredColumns, ...recommendedColumns].includes(mappings[userCol])
                      ? 'required-mapped' 
                      : ''
                  }`}:
 * - Intelligent column suggestions
 * - Required/optional column validation
 * - Business name input
 * - Real-time mapping validation
 * - Comprehensive error handling
 * 
 * Author: Customer Segmentation Team
 * Date: August 2025
 */

import React, { useState, useEffect, useCallback } from 'react';
import './ColumnMapping.css';

const ColumnMapping = ({ 
  detectedColumns = [], 
  coreRequiredColumns = [], 
  recommendedColumns = [], 
  optionalColumns = [], 
  suggestions = {}, 
  analysisModes = {},
  onMappingComplete,
  loading = false 
}) => {
  // State management
  const [mappings, setMappings] = useState(suggestions || {});
  const [businessName, setBusinessName] = useState('');
  const [errors, setErrors] = useState([]);
  const [warnings, setWarnings] = useState([]);
  const [selectedMode, setSelectedMode] = useState('full_rfm');
  const [isValid, setIsValid] = useState(false);

  /**
   * Validate current mappings and business name with flexible requirements
   */
  const validateMappings = useCallback(() => {
    const newErrors = [];
    const newWarnings = [];

    // Check business name
    if (!businessName.trim()) {
      newErrors.push('Business name is required');
    }

    // Get mapped columns
    const mappedStandardCols = new Set(Object.values(mappings).filter(v => v !== ''));
    
    // Determine what's possible with current mappings
    let bestMode = 'basic_segmentation';
    let missingForFullRFM = [];
    let missingForFreqRecency = [];
    
    // Check for full RFM mode
    const fullRFMRequired = ['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice'];
    missingForFullRFM = fullRFMRequired.filter(col => !mappedStandardCols.has(col));
    
    // Check for frequency-recency mode
    const freqRecencyRequired = ['CustomerID', 'InvoiceDate'];
    missingForFreqRecency = freqRecencyRequired.filter(col => !mappedStandardCols.has(col));
    
    // Determine best available mode
    if (missingForFullRFM.length === 0) {
      bestMode = 'full_rfm';
    } else if (missingForFreqRecency.length === 0) {
      bestMode = 'frequency_recency';
      newWarnings.push(`Missing columns for full RFM analysis: ${missingForFullRFM.join(', ')}`);
    } else {
      newErrors.push(`Missing critical columns: ${missingForFreqRecency.join(', ')}`);
    }

    // Check core required columns
    const missingCore = coreRequiredColumns.filter(col => !mappedStandardCols.has(col));
    if (missingCore.length > 0) {
      newErrors.push(`Missing core required columns: ${missingCore.join(', ')}`);
    }

    // Check for duplicate mappings
    const mappedValues = Object.values(mappings).filter(v => v !== '');
    const duplicates = mappedValues.filter((value, index) => mappedValues.indexOf(value) !== index);
    
    if (duplicates.length > 0) {
      newErrors.push(`Duplicate mappings found: ${[...new Set(duplicates)].join(', ')}`);
    }

    setErrors(newErrors);
    setWarnings(newWarnings);
    setSelectedMode(bestMode);
    setIsValid(newErrors.length === 0 && businessName.trim() !== '');
  }, [mappings, businessName, coreRequiredColumns]);

  // Effect to validate mappings when they change
  useEffect(() => {
    validateMappings();
  }, [validateMappings]);

  /**
   * Handle mapping change for a specific column
   */
  const handleMappingChange = (userColumn, standardColumn) => {
    console.log(`Mapping '${userColumn}' to '${standardColumn}'`);
    
    setMappings(prev => ({
      ...prev,
      [userColumn]: standardColumn
    }));
  };

  /**
   * Handle business name input change
   */
  const handleBusinessNameChange = (e) => {
    setBusinessName(e.target.value);
  };

  /**
   * Submit the mapping configuration
   */
  const handleSubmit = () => {
    if (!isValid) {
      alert('Please fix the validation errors before proceeding.');
      return;
    }

    console.log('Submitting mapping configuration:', {
      businessName,
      mappings,
      totalMappings: Object.keys(mappings).filter(key => mappings[key] !== '').length
    });

    onMappingComplete(mappings, businessName);
  };

  /**
   * Reset all mappings
   */
  const resetMappings = () => {
    setMappings({});
    setBusinessName('');
    setErrors([]);
  };

  /**
   * Get description for a standard column
   */
  const getColumnDescription = (standardColumn) => {
    const descriptions = {
      'InvoiceNo': 'Unique transaction identifier (required for RFM analysis)',
      'CustomerID': 'Unique customer identifier (required for RFM analysis)', 
      'Quantity': 'Number of items purchased (required for RFM analysis)',
      'UnitPrice': 'Price per item (required for RFM analysis)',
      'InvoiceDate': 'Transaction date/time (required for RFM analysis)',
      'StockCode': 'Product code identifier (optional - enhances product analysis)',
      'Description': 'Product description (optional - enables product insights)',
      'Country': 'Customer location (optional - enables geographical analysis)'
    };
    return descriptions[standardColumn] || 'No description available';
  };

  // All available standard columns
  const allStandardColumns = [...coreRequiredColumns, ...recommendedColumns, ...optionalColumns];

  return (
    <div className="column-mapping">
      <div className="mapping-header">
        <h3>📋 Map Your CSV Columns</h3>
        <p>
          Map your dataset columns to our standard format for optimal analysis results.
          Required columns are marked with <span className="required-indicator">*</span>
        </p>
      </div>

      {/* Business Name Input */}
      <div className="business-name-section">
        <label className="business-label">
          🏢 Business Name <span className="required-indicator">*</span>
        </label>
        <input
          type="text"
          value={businessName}
          onChange={handleBusinessNameChange}
          placeholder="Enter your business or project name"
          className={`business-input ${!businessName.trim() && errors.length > 0 ? 'error' : ''}`}
          disabled={loading}
        />
        <div className="input-hint">
          This will be used to save and identify your segmentation model
        </div>
      </div>

      {/* Error Display */}
      {errors.length > 0 && (
        <div className="error-section">
          <h4>⚠️ Please fix these issues:</h4>
          <ul>
            {errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Column Mapping Grid */}
      <div className="mapping-section">
        <h4>Column Mappings</h4>
        
        <div className="mapping-grid">
          <div className="mapping-grid-header">
            <span>Your Column</span>
            <span>Maps To</span>
            <span>Description</span>
          </div>

          {detectedColumns.map(userCol => (
            <div key={userCol} className="mapping-row">
              <div className="user-column">
                <span className="column-name">{userCol}</span>
                <div className="column-sample">
                  {/* You could show sample data here if available */}
                </div>
              </div>
              
              <div className="mapping-select">
                <select
                  value={mappings[userCol] || ''}
                  onChange={(e) => handleMappingChange(userCol, e.target.value)}
                  className={`mapping-dropdown ${
                    mappings[userCol] && [...coreRequiredColumns, ...recommendedColumns].includes(mappings[userCol]) 
                      ? 'required-mapping' 
                      : ''
                  }`}
                  disabled={loading}
                >
                  <option value="">-- Skip this column --</option>
                  {allStandardColumns.map(stdCol => (
                    <option key={stdCol} value={stdCol}>
                      {stdCol} {[...coreRequiredColumns, ...recommendedColumns].includes(stdCol) ? '*' : ''}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="column-description">
                {mappings[userCol] && getColumnDescription(mappings[userCol])}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mapping Summary */}
      <div className="mapping-summary">
        <div className="summary-section">
          <h4>📊 Mapping Summary</h4>
          <div className="summary-stats">
            <div className="stat">
              <span className="stat-label">Required Columns:</span>
              <span className="stat-value">
                {[...coreRequiredColumns, ...recommendedColumns].filter(col => Object.values(mappings).includes(col)).length} / {[...coreRequiredColumns, ...recommendedColumns].length}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Optional Columns:</span>
              <span className="stat-value">
                {optionalColumns.filter(col => Object.values(mappings).includes(col)).length} / {optionalColumns.length}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Total Mapped:</span>
              <span className="stat-value">
                {Object.values(mappings).filter(v => v !== '').length} / {detectedColumns.length}
              </span>
            </div>
          </div>
        </div>

        <div className="column-requirements">
          <div className="requirement-section">
            <h5>📋 Core Required Columns (must be mapped)</h5>
            <ul className="column-list required">
              {coreRequiredColumns.map(col => (
                <li 
                  key={col} 
                  className={Object.values(mappings).includes(col) ? 'mapped' : 'unmapped'}
                >
                  <span className="column-name">{col}</span>
                  <span className="column-status">
                    {Object.values(mappings).includes(col) ? '✅' : '❌'}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="requirement-section">
            <h5>⭐ Recommended Columns (for better analysis)</h5>
            <ul className="column-list recommended">
              {recommendedColumns.map(col => (
                <li 
                  key={col} 
                  className={Object.values(mappings).includes(col) ? 'mapped' : 'unmapped'}
                >
                  <span className="column-icon">
                    {Object.values(mappings).includes(col) ? '✅' : '❌'}
                  </span>
                  {col}: {getColumnDescription(col)}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="requirement-section">
            <h5>🔧 Optional Columns (enhance analysis)</h5>
            <ul className="column-list optional">
              {optionalColumns.map(col => (
                <li 
                  key={col} 
                  className={Object.values(mappings).includes(col) ? 'mapped' : 'unmapped'}
                >
                  <span className="column-icon">
                    {Object.values(mappings).includes(col) ? '✅' : '⭕'}
                  </span>
                  {col}: {getColumnDescription(col)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-buttons">
        <button 
          onClick={resetMappings}
          className="reset-btn"
          disabled={loading}
        >
          🔄 Reset Mappings
        </button>
        
        <button 
          onClick={handleSubmit}
          className={`submit-btn ${isValid ? 'valid' : 'invalid'}`}
          disabled={!isValid || loading}
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Processing...
            </>
          ) : (
            <>
              🚀 Process Data with Mappings
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default ColumnMapping;
