"""
Customer Segmentation API Server
===============================

Startup script for the customer segmentation dashboard backend.
Runs the FastAPI server with proper configuration.

Usage:
    python start_server.py

Author: Customer Segmentation Team
Date: August 2025
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

if __name__ == "__main__":
    print("🚀 Starting Customer Segmentation API Server...")
    print("📊 Backend: http://localhost:8050")
    print("📋 API Docs: http://localhost:8050/docs")
    print("🔄 Auto-reload enabled for development")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8050,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
