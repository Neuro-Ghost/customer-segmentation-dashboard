# 🏷 Customer Segmentation Dashboard
![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![Node.js](https://img.shields.io/badge/Node.js-18%2B-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

**Advanced Customer Segmentation Dashboard** with intelligent column mapping, RFM analysis, business-specific model training, and interactive visualizations.

## Features
- Multi-step workflow: Upload → Column Mapping → Results  
- Automatic column detection and mapping suggestions  
- Business-specific model training and clustering  
- Interactive visualizations of customer segments  
- Downloadable insights and top products analysis  

## Quick Start
**Clone the repository:**  
```bash
git clone https://github.com/Neuro-Ghost/customer-segmentation-dashboard.git
cd customer-segmentation-dashboard
```
## Backend Setup (Python/FastAPI):
 Windows PowerShell

```
python -m venv venv
.\venv\Scripts\activate
```

 macOS/Linux
```
source venv/bin/activate
pip install -r requirements.txt
```
Run the backened
```
uvicorn app.main:app --reload
```
