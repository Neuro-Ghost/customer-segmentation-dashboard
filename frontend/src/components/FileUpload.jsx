import React, { useState, useRef } from "react";
import "./FileUpload.css";

export default function FileUpload({ onUpload, loading = false }) {
  const [file, setFile] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === 'text/csv') {
      handleFileSelect(files[0]);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileInputChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleUpload = () => {
    if (file && onUpload) {
      onUpload(file);
    }
  };

  const handleClear = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="upload-box">
      <div 
        className={`dropzone ${isDragOver ? 'drag-over' : ''} ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
          disabled={loading}
        />
        
        <div className="dropzone-content">
          {!file ? (
            <>
              <div className="upload-icon">📁</div>
              <div className="dropzone-text">
                <div className="title">Drag & Drop CSV File</div>
                <div className="subtitle">or click to browse</div>
              </div>
            </>
          ) : (
            <>
              <div className="file-icon">📄</div>
              <div className="file-info">
                <div className="file-name">{file.name}</div>
                <div className="file-size">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {file && (
        <div className="upload-controls">
          <button
            className="btn primary"
            onClick={handleUpload}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Processing...
              </>
            ) : (
              "🚀 Upload & Analyze"
            )}
          </button>
          <button
            className="btn secondary"
            onClick={handleClear}
            disabled={loading}
          >
            🗑️ Clear Selection
          </button>
        </div>
      )}

      <div className="upload-hint">
        <p>📋 Your CSV will be analyzed for intelligent column mapping</p>
        <p>✨ Supports flexible data structures - we'll adapt to your columns</p>
      </div>
    </div>
  );
}
