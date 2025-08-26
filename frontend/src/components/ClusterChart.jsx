import React from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8", "#82CA9D"];

function ClusterChart({ clusterCounts }) {
  console.log("ClusterChart received clusterCounts:", clusterCounts);
  
  if (!clusterCounts || Object.keys(clusterCounts).length === 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Customer Segments Distribution</h3>
        <div className="text-gray-500 text-center py-8">
          No segmentation data available
        </div>
      </div>
    );
  }

  const data = Object.entries(clusterCounts).map(([name, value]) => ({
    name,
    value: parseInt(value),
  }));

  console.log("Processed data for chart:", data);

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-semibold mb-4">Customer Segments Distribution</h3>
      <ResponsiveContainer width="100%" height={400}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            outerRadius={120}
            fill="#8884d8"
            label={({ name, value, percent }) => 
              `${name}: ${value} (${(percent * 100).toFixed(1)}%)`
            }
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export default ClusterChart;
