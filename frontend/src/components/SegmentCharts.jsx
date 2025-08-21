import React from "react";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from "recharts";
import "./SegmentCharts.css";

const COLORS = ["#00C49F", "#FF8042", "#0088FE", "#FFBB28", "#A569BD"];

export default function SegmentCharts({ analytics = {} }) {
  const counts = analytics.cluster_counts || {};
  const revenue = analytics.revenue_by_segment || {};

  const pieData = Object.entries(counts).map(([name, value]) => ({ name, value }));
  const barData = Object.entries(revenue).map(([name, value]) => ({ name, revenue: Math.round(value) }));

  if (pieData.length === 0 && barData.length === 0) {
    return <div className="chart-card"><p>No chart data available.</p></div>;
  }

  return (
    <div className="charts-wrapper">
      <div className="chart-card">
        <h3 style={{ marginTop: 0 }}>Customer Distribution by Segment</h3>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                {pieData.map((entry, idx) => <Cell key={idx} fill={COLORS[idx % COLORS.length]} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="chart-card">
        <h3 style={{ marginTop: 0 }}>Revenue by Segment</h3>
        <div style={{ width: "100%", height: 280 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="revenue" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
