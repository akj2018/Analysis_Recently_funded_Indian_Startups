# Indian Startup Funding — Automated End-to-End ETL Pipeline

An automated **data engineering pipeline** that scrapes, cleans, stores, and visualizes real-time funding data for Indian startups.  
This project demonstrates how raw web data can be transformed into **analytics-ready insights** using a **Medallion Architecture** and modern cloud-native tooling.

---

## Technical Stack & Tools

| Layer | Technology |
|-----|-----------|
| **Extraction** | Python, Playwright (Headless Chromium) |
| **Orchestration** | GitHub Actions (CI/CD, CRON scheduling) |
| **Data Warehouse** | Google BigQuery (Serverless SQL) |
| **Analytics** | Power BI (Microsoft Fabric) |
| **Security** | GitHub Secrets, GCP Service Accounts |

---

## Key Engineering Concepts Applied

### Medallion Architecture
- **Bronze**: Raw scraped web data
- **Silver**: Cleaned & standardized staging layer
- **Gold**: Historical fact table for analytics

### Idempotent UPSERT (MERGE)
- Ensures **data integrity**
- Updates existing records and inserts new ones
- Composite key used: (Company, Country, Industry, Last Funding Date)

### ☁️ Cloud-to-Cloud Integration
- Direct integration between **Google BigQuery** and **Microsoft PowerBI**
- No local gateway required
- Fully automated using Scheduled Refresh

### 🤖 Headless Automation
- Browser-based scraping using **Playwright**
- Runs in a Linux environment inside GitHub Actions
- Handles dynamic & asynchronous web content

---

## 📂 Project Architecture & Data Flow

### 1️⃣ Extraction & Bronze Layer
- Python script uses **Playwright** to scrape startup funding data
- Handles JavaScript-rendered content missed by traditional scrapers
- Fully automated via GitHub Actions

**Schedule (CRON):**
30 18 * * 1
Runs every **Monday at 6:30 PM UTC**


### 2️⃣ Transformation — Silver Medallion
Data is cleaned and standardized directly inside **BigQuery** using SQL (ELT approach).

**Key Transformations:**
- Uppercasing company and country names
- Parsing strings into `DATE` formats
- Splitting and normalizing industry categories

**Output Table:**
stg_clean_latest

## 3️⃣ Historical Persistence — Gold Medallion
A **True UPSERT strategy** maintains historical funding records.

**Why?**
- Startups raise multiple funding rounds
- Company name alone is not a reliable key

**Matching Logic:**
- Company
- Industry
- Funding Date

**Behavior:**
- Existing round updated → record refreshed
- New funding round → new row inserted

**Final Table:**
fct_clean_history


---

## 📊 Data Modeling

### Logical Data Model
The diagram below represents the schema and enforced data types for the `fct_clean_history` table.

📌 _Insert BigQuery schema screenshot here_

---

### Dashboard Preview
A **Power BI dashboard** built on the Gold layer provides:
- Funding trends over time
- Industry-wise investment distribution
- Geographic insights

🔄 Automatically refreshes every **Tuesday morning** after the pipeline run.

📌 _Insert Power BI dashboard screenshot here_

---

## 🛠️ Installation & Local Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/repo-name.git
cd repo-name
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium --with-deps
```

### 3️⃣ Configure Credentials

1. Create a Google Cloud Service Account
2. Download the JSON key
3. Save it locally as:
```vbnet
bigquery-key.json
```
⚠️ This file is ignored via .gitignore

### 4️⃣ Run the Script Locally
```bash
python web_scraping.py
```

## 🚀 GitHub Actions Workflow Configuration

To enable full automation, add the following GitHub Secrets:
| Secret Name | Description |
|-----|-----------|
| **GCP_SA_KEY** | Entire contents of bigquery-key.json |

The workflow automatically:

- Installs Playwright browser binaries
- Sets up Python dependencies
- Authenticates with BigQuery
- Executes the ETL pipeline on schedule

## What This Project Demonstrates

- Real-world ETL pipeline design
- Cloud-native ELT best practices
- Idempotent data engineering logic
- CI/CD-driven automation
- Analytics-ready data modeling
	
## Future Enhancements

- Add data quality checks (Great Expectations)
- Implement incremental scraping logic
- Add alerting on pipeline failures
- Extend to additional startup ecosystems

## Introduction

## Project Overview

## Tech Stack

## Architecture Diagram

## Dataset Used

## Data Model used
