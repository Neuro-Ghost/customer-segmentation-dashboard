import React from "react";
import { Bar } from "react-chartjs-2";

export default function Charts({ data }) {
  const segments = data.map(d => d.segment);
  const counts = segments.reduce((acc, s) => ((acc[s] = (acc[s] || 0) + 1), acc), {});

  const chartData = {
    labels: Object.keys(counts),
    datasets: [{ label: "Customer Segments", data: Object.values(counts), backgroundColor: ["#36A2EB", "#FF6384", "#FFCE56"] }]
  };

  return <Bar data={chartData} />;
}
