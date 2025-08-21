import React, { useState } from "react";
import "./FileUpload.css";

export default function FileUpload({ onUpload, loading = false }) {
  const [file, setFile] = useState(null);

  return (
    <div className="upload-box">
      <label style={{ fontSize: 14 }}>Upload cleaned CSV</label>
      <div className="upload-controls">
        <input
          id="csv-input"
          type="file"
          accept=".csv"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <button
          className="btn"
          onClick={() => onUpload(file)}
          disabled={loading}
        >
          {loading ? "Processing..." : "Upload & Segment"}
        </button>
        <button
          className="btn secondary"
          onClick={() => {
            setFile(null);
            const el = document.getElementById("csv-input");
            if (el) el.value = "";
          }}
        >
          Clear
        </button>
      </div>
      <div className="hint" style={{ marginTop: 8 }}>
        CSV must contain exactly: InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
      </div>
    </div>
  );
}
