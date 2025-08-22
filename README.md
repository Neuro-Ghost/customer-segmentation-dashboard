# Customer Segmentation Dashboard

A full-stack project for **customer segmentation** using **RFM analysis**. This project processes transactional data, performs segmentation, and visualizes customer groups in an interactive dashboard. Perfect for marketing insights and customer retention strategies.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Technologies Used](#technologies-used)  
3. [Project Workflow](#project-workflow)  
4. [Installation](#installation)  
5. [Running the Project](#running-the-project)  
6. [Folder Structure](#folder-structure)  
7. [Segmentation Methodology](#segmentation-methodology)  
8. [Dashboard Features](#dashboard-features)  
9. [Future Improvements](#future-improvements)  

---

## Project Overview

This project demonstrates a complete **customer segmentation pipeline**:

1. **Data Preprocessing** – Clean raw transactional data, handle missing values, and ensure robust date and customer ID parsing.  
2. **RFM Analysis** – Compute **Recency, Frequency, and Monetary** metrics per customer.  
3. **Segmentation** – Classify customers into segments such as `At Risk`, `Engaged`, and `Steady`.  
4. **Visualization** – Build an interactive **dashboard** using React and Recharts for insights visualization.  

---

## Technologies Used

- **Python** – Pandas, NumPy, Matplotlib/Seaborn (data analysis & preprocessing)  
- **Jupyter / Google Colab** – Initial data exploration and preprocessing  
- **JavaScript / React** – Frontend dashboard  
- **Recharts** – Charts & visualizations  
- **Vite** – React build tool  
- **Node.js / Express (Optional)** – Backend API for serving analytics data  

---

## Project Workflow

### 1. Data Exploration & Cleaning

- Use the **UK Online Retail dataset**.  
- Handle missing or inconsistent `CustomerID` and `InvoiceDate`.  
- Parse dates robustly (handle mixed formats and timezones).  
- Check for duplicates and anomalies in transaction data.  

### 2. RFM Calculation

- **Recency**: Days since last purchase per customer.  
- **Frequency**: Number of transactions per customer.  
- **Monetary**: Total revenue per customer.  
- Normalize metrics to assign **RFM scores**.  

### 3. Customer Segmentation

- Classify customers into actionable segments:  
  - `At Risk` – High recency, low engagement  
  - `Engaged` – Frequent, recent customers  
  - `Steady` – Average activity, consistent buyers  

### 4. Dashboard Creation

- **Frontend** in React using **Recharts** for charts.  
- **Backend** serves RFM metrics (or static JSON if no backend).  
- Visualize metrics with **Pie, Bar, and Line charts**.  
- Professional, clean UI with responsive design.  

---

## Installation

1. Clone the repo:

```bash
git clone https://github.com/YOUR_USERNAME/customer-segmentation-dashboard.git
cd customer-segmentation-dashboard
