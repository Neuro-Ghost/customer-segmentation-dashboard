import React from "react";
import "./TopProducts.css";

export default function TopProducts({ topProducts = {} }) {
  if (!topProducts || Object.keys(topProducts).length === 0) {
    return <div className="top-products-wrapper"><div className="top-products-card"><p>No product data available.</p></div></div>;
  }

  return (
    <div className="top-products-wrapper">
      <h3 style={{ marginTop: 0 }}>Top products by segment</h3>
      <div className="top-products-grid">
        {Object.entries(topProducts).map(([segment, list], idx) => (
          <div className="top-products-card" key={idx}>
            <h4 style={{ marginBottom: 8 }}>{segment}</h4>
            <ol style={{ margin: 0, paddingLeft: 18 }}>
              {list.slice(0, 5).map((p, i) => (
                <li key={i} style={{ marginBottom: 8 }}>
                  <div className="prod-name">{p.Description}</div>
                  <div className="prod-meta" style={{ color: "#98a7b9", fontSize: 12 }}>
                    Qty: {p.total_quantity} • Rev: £{Math.round(p.total_revenue)}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        ))}
      </div>
    </div>
  );
}
