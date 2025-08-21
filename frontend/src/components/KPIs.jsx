import React from "react";
import "./KPIs.css";

function prettyNum(n) {
  if (n === undefined || n === null) return "-";
  return Intl.NumberFormat().format(Math.round(n));
}

export default function KPIs({ analytics = {} }) {
  const totalCustomers = analytics.n_customers ?? 0;
  const totalRows = analytics.n_rows ?? 0;
  const revenueSum = Object.values(analytics.revenue_by_segment || {}).reduce((a,b)=>a+(b||0),0);

  return (
    <div className="kpi-row" style={{ marginTop: 16 }}>
      <div className="kpi-card">
        <div className="kpi-title">Customers</div>
        <div className="kpi-value">{prettyNum(totalCustomers)}</div>
        <div className="kpi-sub">Rows: {prettyNum(totalRows)}</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-title">Total Revenue</div>
        <div className="kpi-value">£{Intl.NumberFormat().format(Math.round(revenueSum))}</div>
        <div className="kpi-sub">By segment</div>
      </div>

      <div className="kpi-card">
        <div className="kpi-title">Segments</div>
        <div className="kpi-value">{Object.keys(analytics.cluster_counts || {}).length}</div>
        <div className="kpi-sub">Unique segments</div>
      </div>
    </div>
  );
}
