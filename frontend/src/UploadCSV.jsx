import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import Papa from "papaparse";

export default function UploadCSV({ setData }) {
  const [loading, setLoading] = useState(false);

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("http://localhost:8000/segment", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    setData(res.data);
    setLoading(false);
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <div {...getRootProps()} style={{ border: "2px dashed #aaa", padding: "20px" }}>
      <input {...getInputProps()} />
      {loading ? "Uploading..." : "Drag & drop a CSV file here, or click to select"}
    </div>
  );
}
