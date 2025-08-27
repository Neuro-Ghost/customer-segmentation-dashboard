import React from "react";
import "./ProductAnalysis.css";

export default function ProductAnalysis({ analytics = {} }) {
  const { most_expensive_products = [], most_bought_products = [] } = analytics;

  if (!most_expensive_products.length && !most_bought_products.length) {
    return (
      <div className="product-analysis-wrapper">
        <div className="product-analysis-card">
          <p>No product analysis data available.</p>
        </div>
      </div>
    );
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(price);
  };

  const formatQuantity = (qty) => {
    return new Intl.NumberFormat('en-GB').format(qty);
  };

  return (
    <div className="product-analysis-wrapper">
      <h3 style={{ marginTop: 0, marginBottom: '1.5rem' }}>📊 Product Analysis</h3>
      
      <div className="product-charts-grid">
        {/* Most Expensive Products */}
        {most_expensive_products.length > 0 && (
          <div className="product-chart-card">
            <h4 className="chart-title">💎 Top 10 Most Expensive Products</h4>
            <div className="chart-subtitle">Unit Price (£)</div>
            <div className="product-bars-container">
              {most_expensive_products.map((product, index) => {
                const maxPrice = most_expensive_products[0]?.UnitPrice || 1;
                const widthPercentage = (product.UnitPrice / maxPrice) * 100;
                
                return (
                  <div key={index} className="product-bar-item">
                    <div className="product-bar-info">
                      <div className="product-name" title={product.Description}>
                        {product.Description}
                      </div>
                      <div className="product-value expensive-value">
                        {formatPrice(product.UnitPrice)}
                      </div>
                    </div>
                    <div className="product-bar-container">
                      <div 
                        className="product-bar expensive-bar"
                        style={{ width: `${widthPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Most Bought Products */}
        {most_bought_products.length > 0 && (
          <div className="product-chart-card">
            <h4 className="chart-title">🔥 Top 10 Most Bought Products</h4>
            <div className="chart-subtitle">Total Quantity Sold</div>
            <div className="product-bars-container">
              {most_bought_products.map((product, index) => {
                const maxQuantity = most_bought_products[0]?.TotalQuantity || 1;
                const widthPercentage = (product.TotalQuantity / maxQuantity) * 100;
                
                return (
                  <div key={index} className="product-bar-item">
                    <div className="product-bar-info">
                      <div className="product-name" title={product.Description}>
                        {product.Description}
                      </div>
                      <div className="product-value bought-value">
                        {formatQuantity(product.TotalQuantity)} units
                      </div>
                    </div>
                    <div className="product-bar-container">
                      <div 
                        className="product-bar bought-bar"
                        style={{ width: `${widthPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
