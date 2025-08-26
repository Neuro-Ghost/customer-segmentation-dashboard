/**
 * Custom Visualization Component
 * =============================
 * 
 * Allows users to create custom charts by selecting:
 * - Chart type (bar, pie, scatter, line)
 * - X-axis column
 * - Y-axis column (for applicable charts)
 * - Group by column
 * - Aggregation method
 * 
 * Features:
 * - Interactive chart builder
 * - Multiple chart types
 * - Real-time preview
 * - Export capabilities
 * 
 * Author: Customer Segmentation Team
 * Date: August 2025
 */

import React, { useState, useEffect } from 'react';
import './CustomVisualization.css';

const CustomVisualization = ({ data }) => {
  const [chartConfig, setChartConfig] = useState({
    type: 'bar',
    xAxis: '',
    yAxis: '',
    groupBy: '',
    aggregation: 'sum'
  });
  
  const [chartData, setChartData] = useState(null);
  const [availableColumns, setAvailableColumns] = useState([]);
  const [activeTemplate, setActiveTemplate] = useState(null);
  const [multiChartMode, setMultiChartMode] = useState(false);

  // Extract available columns from data
  useEffect(() => {
    if (data && data.length > 0) {
      const columns = Object.keys(data[0]).filter(col => 
        !['CustomerID'].includes(col) // Exclude non-chartable columns
      );
      setAvailableColumns(columns);
    }
  }, [data]);

  // Chart type options
  const chartTypes = [
    { value: 'bar', label: '📊 Bar Chart', description: 'Compare values across categories' },
    { value: 'pie', label: '🥧 Pie Chart', description: 'Show proportions of a whole' },
    { value: 'scatter', label: '📈 Scatter Plot', description: 'Show relationships between two variables' },
    { value: 'line', label: '📉 Line Chart', description: 'Show trends over time or sequences' },
    { value: 'histogram', label: '📋 Histogram', description: 'Show distribution of values' }
  ];

  // RFM-specific visualization templates
  const rfmTemplates = [
    {
      id: 'rfm_scatter',
      name: '🎯 RFM Scatter Matrix',
      description: 'Analyze relationships between R, F, M values',
      configs: [
        { type: 'scatter', xAxis: 'Recency', yAxis: 'Frequency', title: 'Recency vs Frequency' },
        { type: 'scatter', xAxis: 'Recency', yAxis: 'Monetary', title: 'Recency vs Monetary' },
        { type: 'scatter', xAxis: 'Frequency', yAxis: 'Monetary', title: 'Frequency vs Monetary' }
      ]
    },
    {
      id: 'segment_analysis',
      name: '📊 Segment Distribution',
      description: 'Analyze customer segments and clusters',
      configs: [
        { type: 'pie', groupBy: 'Segment', title: 'Customer Segments Distribution' },
        { type: 'bar', groupBy: 'Cluster', yAxis: 'Monetary', aggregation: 'mean', title: 'Average Monetary by Cluster' },
        { type: 'bar', groupBy: 'Segment', yAxis: 'Frequency', aggregation: 'mean', title: 'Average Frequency by Segment' }
      ]
    },
    {
      id: 'rfm_distributions',
      name: '📈 RFM Distributions',
      description: 'Understand the distribution of RFM values',
      configs: [
        { type: 'histogram', xAxis: 'Recency', title: 'Recency Distribution' },
        { type: 'histogram', xAxis: 'Frequency', title: 'Frequency Distribution' },
        { type: 'histogram', xAxis: 'Monetary', title: 'Monetary Distribution' }
      ]
    },
    {
      id: 'cluster_comparison',
      name: '🔍 Cluster Comparison',
      description: 'Compare RFM values across different clusters',
      configs: [
        { type: 'bar', groupBy: 'Cluster', yAxis: 'Recency', aggregation: 'mean', title: 'Average Recency by Cluster' },
        { type: 'bar', groupBy: 'Cluster', yAxis: 'Frequency', aggregation: 'mean', title: 'Average Frequency by Cluster' },
        { type: 'bar', groupBy: 'Cluster', yAxis: 'Monetary', aggregation: 'mean', title: 'Average Monetary by Cluster' }
      ]
    }
  ];

  // Aggregation options
  const aggregationTypes = [
    { value: 'sum', label: 'Sum' },
    { value: 'mean', label: 'Average' },
    { value: 'count', label: 'Count' },
    { value: 'min', label: 'Minimum' },
    { value: 'max', label: 'Maximum' }
  ];

  // Generate chart data based on configuration
  const generateChartData = React.useCallback(() => {
    if (!data || !chartConfig.xAxis) return null;

    try {
      let processedData = [];

      if (chartConfig.type === 'histogram') {
        // For histogram, create bins
        const values = data.map(row => parseFloat(row[chartConfig.xAxis])).filter(v => !isNaN(v));
        const bins = createHistogramBins(values, 10);
        processedData = bins.map(bin => ({
          label: `${bin.min.toFixed(1)}-${bin.max.toFixed(1)}`,
          value: bin.count
        }));
      } else if (chartConfig.groupBy) {
        // Group data and aggregate
        const grouped = {};
        data.forEach(row => {
          const groupKey = row[chartConfig.groupBy];
          if (!grouped[groupKey]) {
            grouped[groupKey] = [];
          }
          grouped[groupKey].push(row);
        });

        processedData = Object.entries(grouped).map(([group, rows]) => {
          let value;
          if (chartConfig.aggregation === 'count') {
            value = rows.length;
          } else {
            const values = rows.map(row => parseFloat(row[chartConfig.yAxis])).filter(v => !isNaN(v));
            switch (chartConfig.aggregation) {
              case 'sum':
                value = values.reduce((a, b) => a + b, 0);
                break;
              case 'mean':
                value = values.reduce((a, b) => a + b, 0) / values.length;
                break;
              case 'min':
                value = Math.min(...values);
                break;
              case 'max':
                value = Math.max(...values);
                break;
              default:
                value = values.reduce((a, b) => a + b, 0);
            }
          }
          return { label: group, value: isNaN(value) ? 0 : value };
        });
      } else {
        // Simple x-y mapping
        processedData = data.slice(0, 50).map(row => ({ // Limit to 50 points for performance
          label: row[chartConfig.xAxis],
          value: chartConfig.yAxis ? parseFloat(row[chartConfig.yAxis]) : 1,
          x: chartConfig.type === 'scatter' ? parseFloat(row[chartConfig.xAxis]) : undefined,
          y: chartConfig.type === 'scatter' ? parseFloat(row[chartConfig.yAxis]) : undefined
        }));
      }

      return processedData;
    } catch (error) {
      console.error('Error generating chart data:', error);
      return null;
    }
  }, [data, chartConfig]);

  // Create histogram bins
  const createHistogramBins = (values, binCount) => {
    const min = Math.min(...values);
    const max = Math.max(...values);
    const binSize = (max - min) / binCount;
    
    const bins = [];
    for (let i = 0; i < binCount; i++) {
      bins.push({
        min: min + i * binSize,
        max: min + (i + 1) * binSize,
        count: 0
      });
    }
    
    values.forEach(value => {
      const binIndex = Math.min(Math.floor((value - min) / binSize), binCount - 1);
      bins[binIndex].count++;
    });
    
    return bins;
  };

  // Update chart data when configuration changes
  useEffect(() => {
    const newChartData = generateChartData();
    setChartData(newChartData);
  }, [generateChartData]);

  // Handle configuration changes
  const handleConfigChange = (field, value) => {
    setChartConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Apply RFM template
  const applyTemplate = (template) => {
    setActiveTemplate(template);
    setMultiChartMode(true);
    
    // Reset single chart mode
    setChartConfig({
      type: 'bar',
      xAxis: '',
      yAxis: '',
      groupBy: '',
      aggregation: 'sum'
    });
  };

  // Reset to single chart mode
  const resetToSingleChart = () => {
    setActiveTemplate(null);
    setMultiChartMode(false);
  };

  // Generate chart data for a specific configuration
  const generateChartDataForConfig = (config) => {
    if (!data || !config.xAxis) return null;

    try {
      let processedData = [];

      if (config.type === 'histogram') {
        const values = data.map(row => parseFloat(row[config.xAxis])).filter(v => !isNaN(v));
        const bins = createHistogramBins(values, 10);
        processedData = bins.map(bin => ({
          label: `${bin.min.toFixed(1)}-${bin.max.toFixed(1)}`,
          value: bin.count
        }));
      } else if (config.groupBy) {
        const grouped = {};
        data.forEach(row => {
          const groupKey = row[config.groupBy];
          if (!grouped[groupKey]) {
            grouped[groupKey] = [];
          }
          grouped[groupKey].push(row);
        });

        processedData = Object.entries(grouped).map(([group, rows]) => {
          let value;
          if (config.aggregation === 'count') {
            value = rows.length;
          } else {
            const values = rows.map(row => parseFloat(row[config.yAxis])).filter(v => !isNaN(v));
            switch (config.aggregation) {
              case 'sum':
                value = values.reduce((a, b) => a + b, 0);
                break;
              case 'mean':
                value = values.reduce((a, b) => a + b, 0) / values.length;
                break;
              case 'min':
                value = Math.min(...values);
                break;
              case 'max':
                value = Math.max(...values);
                break;
              default:
                value = values.reduce((a, b) => a + b, 0);
            }
          }
          return { label: group, value: isNaN(value) ? 0 : value };
        });
      } else {
        processedData = data.slice(0, 50).map(row => ({
          label: row[config.xAxis],
          value: config.yAxis ? parseFloat(row[config.yAxis]) : 1,
          x: config.type === 'scatter' ? parseFloat(row[config.xAxis]) : undefined,
          y: config.type === 'scatter' ? parseFloat(row[config.yAxis]) : undefined
        }));
      }

      return processedData;
    } catch (error) {
      console.error('Error generating chart data:', error);
      return null;
    }
  };

  // Render chart with given configuration and data
  const renderChart = (config, chartData, title) => {
    if (!chartData || chartData.length === 0) {
      return <div className="no-data">No data to display for {title}</div>;
    }

    const maxValue = Math.max(...chartData.map(d => d.value));

    if (config.type === 'bar' || config.type === 'histogram') {
      return (
        <div className="chart-wrapper">
          <h5 className="chart-title">{title}</h5>
          <div className="simple-bar-chart">
            {chartData.map((item, index) => (
              <div key={index} className="bar-item">
                <div 
                  className="bar"
                  style={{ 
                    height: `${(item.value / maxValue) * 150}px`,
                    backgroundColor: `hsl(${(index * 137.5) % 360}, 70%, 50%)`
                  }}
                ></div>
                <div className="bar-label">{String(item.label).substring(0, 8)}</div>
                <div className="bar-value">{item.value.toFixed(1)}</div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (config.type === 'pie') {
      const total = chartData.reduce((sum, item) => sum + item.value, 0);
      let currentAngle = 0;
      
      return (
        <div className="chart-wrapper">
          <h5 className="chart-title">{title}</h5>
          <div className="simple-pie-chart">
            <svg width="250" height="250" viewBox="0 0 250 250">
              {chartData.map((item, index) => {
                const angle = (item.value / total) * 360;
                const x1 = 125 + 80 * Math.cos((currentAngle - 90) * Math.PI / 180);
                const y1 = 125 + 80 * Math.sin((currentAngle - 90) * Math.PI / 180);
                const x2 = 125 + 80 * Math.cos((currentAngle + angle - 90) * Math.PI / 180);
                const y2 = 125 + 80 * Math.sin((currentAngle + angle - 90) * Math.PI / 180);
                
                const largeArcFlag = angle > 180 ? 1 : 0;
                const pathData = `M 125 125 L ${x1} ${y1} A 80 80 0 ${largeArcFlag} 1 ${x2} ${y2} Z`;
                
                currentAngle += angle;
                
                return (
                  <path
                    key={index}
                    d={pathData}
                    fill={`hsl(${(index * 137.5) % 360}, 70%, 50%)`}
                    stroke="#fff"
                    strokeWidth="2"
                  />
                );
              })}
            </svg>
            <div className="pie-legend">
              {chartData.slice(0, 6).map((item, index) => (
                <div key={index} className="legend-item">
                  <div 
                    className="legend-color"
                    style={{ backgroundColor: `hsl(${(index * 137.5) % 360}, 70%, 50%)` }}
                  ></div>
                  <span>{item.label}: {item.value.toFixed(1)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    }

    if (config.type === 'scatter') {
      return (
        <div className="chart-wrapper">
          <h5 className="chart-title">{title}</h5>
          <div className="simple-scatter-chart">
            <svg width="300" height="200" viewBox="0 0 300 200">
              {chartData.map((item, index) => (
                <circle
                  key={index}
                  cx={30 + (item.x / Math.max(...chartData.map(d => d.x))) * 240}
                  cy={170 - (item.y / Math.max(...chartData.map(d => d.y))) * 140}
                  r="3"
                  fill={`hsl(${(index * 137.5) % 360}, 70%, 50%)`}
                />
              ))}
            </svg>
          </div>
        </div>
      );
    }

    return <div className="simple-chart">Chart type not implemented yet</div>;
  };

  return (
    <div className="custom-visualization">
      <div className="viz-header">
        <h3>🎨 Custom Visualization Builder</h3>
        <p>Create custom charts to explore your segmentation data</p>
      </div>

      <div className="viz-content">
        {/* RFM Template Section */}
        <div className="template-section">
          <h4>🎯 RFM Analysis Templates</h4>
          <p>Quick start with common RFM visualizations</p>
          
          <div className="template-grid">
            {rfmTemplates.map(template => (
              <div
                key={template.id}
                className={`template-card ${activeTemplate?.id === template.id ? 'active' : ''}`}
                onClick={() => applyTemplate(template)}
              >
                <h5>{template.name}</h5>
                <p>{template.description}</p>
                <div className="template-charts">
                  {template.configs.length} charts
                </div>
              </div>
            ))}
          </div>

          {activeTemplate && (
            <div className="template-active">
              <div className="template-header">
                <h4>📊 {activeTemplate.name}</h4>
                <button onClick={resetToSingleChart} className="reset-btn">
                  ← Back to Custom
                </button>
              </div>
              
              <div className="multi-chart-grid">
                {activeTemplate.configs.map((config, index) => {
                  const templateChartData = generateChartDataForConfig(config);
                  return (
                    <div key={index} className="template-chart">
                      {renderChart(config, templateChartData, config.title)}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Custom Chart Builder */}
        {!multiChartMode && (
          <div className="viz-controls">
            <div className="control-section">
              <h4>🛠️ Custom Chart Builder</h4>
              
              {/* Chart Type Selection */}
              <div className="control-group">
                <label>Chart Type</label>
                <div className="chart-type-grid">
                  {chartTypes.map(type => (
                    <div
                      key={type.value}
                      className={`chart-type-option ${chartConfig.type === type.value ? 'selected' : ''}`}
                      onClick={() => handleConfigChange('type', type.value)}
                    >
                      <div className="chart-type-label">{type.label}</div>
                      <div className="chart-type-desc">{type.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Column Selection */}
              <div className="control-group">
                <label>X-Axis Column</label>
                <select
                  value={chartConfig.xAxis}
                  onChange={(e) => handleConfigChange('xAxis', e.target.value)}
                  className="control-select"
                >
                  <option value="">Select column...</option>
                  {availableColumns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              {(['bar', 'scatter', 'line'].includes(chartConfig.type)) && (
                <div className="control-group">
                  <label>Y-Axis Column</label>
                  <select
                    value={chartConfig.yAxis}
                    onChange={(e) => handleConfigChange('yAxis', e.target.value)}
                    className="control-select"
                  >
                    <option value="">Select column...</option>
                    {availableColumns.filter(col => col !== chartConfig.xAxis).map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}

              {chartConfig.type !== 'histogram' && (
                <div className="control-group">
                  <label>Group By (Optional)</label>
                  <select
                    value={chartConfig.groupBy}
                    onChange={(e) => handleConfigChange('groupBy', e.target.value)}
                    className="control-select"
                  >
                    <option value="">No grouping</option>
                    {availableColumns.map(col => (
                      <option key={col} value={col}>{col}</option>
                    ))}
                  </select>
                </div>
              )}

              {chartConfig.groupBy && chartConfig.yAxis && (
                <div className="control-group">
                  <label>Aggregation</label>
                  <select
                    value={chartConfig.aggregation}
                    onChange={(e) => handleConfigChange('aggregation', e.target.value)}
                    className="control-select"
                  >
                    {aggregationTypes.map(agg => (
                      <option key={agg.value} value={agg.value}>{agg.label}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div className="viz-display">
              <div className="chart-container">
                <h4>
                  {chartConfig.type.charAt(0).toUpperCase() + chartConfig.type.slice(1)} Chart
                  {chartConfig.xAxis && ` - ${chartConfig.xAxis}`}
                  {chartConfig.yAxis && ` vs ${chartConfig.yAxis}`}
                </h4>
                {chartData ? renderChart(chartConfig, chartData, 'Custom Chart') : (
                  <div className="no-data">Configure your chart to see visualization</div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomVisualization;
