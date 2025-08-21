import React, { useState } from "react";
import FileUpload from "./components/FileUpload";
import KPIs from "./components/KPIs";
import SegmentCharts from "./components/SegmentCharts";
import TopProducts from "./components/TopProducts";
import CustomerTable from "./components/CustomerTable";
import "./App.css";

export default function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleUpload(file) {
    setError("");
    if (!file) { setError("No file selected"); return; }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("http://127.0.0.1:8000/segment", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server error: ${res.status} ${text}`);
      }
      const json = await res.json();
      console.log("Backend response:", json);
      setData(json);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>Customer Segmentation — Dashboard</h1>

      <FileUpload onUpload={handleUpload} loading={loading} />

      {error && <div className="error">{error}</div>}

      {data && (
        <>
          <KPIs analytics={data.analytics} />
          <div className="two-column">
            <SegmentCharts analytics={data.analytics} />
            <TopProducts topProducts={data.analytics.top_products_per_segment} />
          </div>

          <h2>Sample Customer List (preview)</h2>
          <CustomerTable preview={data.preview} />
        </>
      )}
    </div>
  );
}
