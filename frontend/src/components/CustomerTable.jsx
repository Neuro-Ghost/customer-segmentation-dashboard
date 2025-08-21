import React, { useState } from "react";
import "./CustomerTable.css";

function downloadCSV(rows = [], filename = "customers_segmented.csv") {
  if (!rows.length) return;
  const keys = Object.keys(rows[0]);
  const csv = [
    keys.join(","),
    ...rows.map(r => keys.map(k => {
      let v = r[k];
      if (v === null || v === undefined) return "";
      return `"${String(v).replace(/"/g, '""')}"`;
    }).join(","))
  ].join("\n");

  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function CustomerTable({ preview = [] }) {
  const [rowsPerPage] = useState(50);
  const [page, setPage] = useState(0);

  if (!preview || preview.length === 0) {
    return <p>No customer segmentation data available.</p>;
  }

  const start = page * rowsPerPage;
  const paged = preview.slice(start, start + rowsPerPage);
  const headers = Object.keys(preview[0]);

  return (
    <div className="table-section">
      <div className="table-controls">
        <div>Showing {start + 1} - {Math.min(preview.length, start + rowsPerPage)} of {preview.length}</div>
        <div>
          <button className="btn small" onClick={() => downloadCSV(preview)}>Export CSV</button>
        </div>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              {headers.map(h => <th key={h}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {paged.map((r, idx) => (
              <tr key={idx}>
                {headers.map(h => <td key={h + idx}>{String(r[h])}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={() => setPage(p => Math.max(p-1,0))} className="btn small">&lt; Prev</button>
        <span>Page {page+1}</span>
        <button onClick={() => setPage(p => (p+1) * rowsPerPage < preview.length ? p+1 : p)} className="btn small">Next &gt;</button>
      </div>
    </div>
  );
}
