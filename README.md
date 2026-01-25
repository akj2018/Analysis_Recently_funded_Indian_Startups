# Indian Startup Funding — Automated End-to-End ETL Pipeline

## Overview

This project is a **fully automated, ELT pipeline** that collects, processes, and visualizes funding data for 100 recently funded Indian startups.

Goal of the project is to demonstrate **how raw, unstructured web data can be transformed into a reliable, analytics-ready dataset** using modern data engineering principles.

Final output is a [**Power BI dashboard**](https://app.fabric.microsoft.com/view?r=eyJrIjoiOTU5ZTY4ZTQtNjVkZS00MzExLWJmOTEtYTEzZTcwNGNlNzFmIiwidCI6IjlkZGFhY2ExLTM4OWYtNGNiMS1hMTEzLTA4MWJlNmNjMjVmYyIsImMiOjZ9) that refreshes periodically.

## Problem Statement

Public startup funding data is often:
- Un-structured
- Spread out across different websites
- Updated randomly 

Traditional scraping tools fail on such sources, and one-time data pulls do not support **historical analysis**.

## Solution 

I built end-to-end ELT pipeline that:

- Scrapes GrowthList weekly to get raw data for 100 most recently funded Indian startups, using a headless browser.
- Build ETL pipeline to load raw and historical data safely in BigQuery (SQL-based data warehouse)
- Clean and transform data using SQL
- Connect BigQuery dataset to Power BI for creating reports
- Automate entire process via Github Actions and Scheduled Refresh

## Technical Stack & Tools

| Layer | Technology |
|-----|-----------|
| **Extraction** | Python, Playwright (Headless Chromium) |
| **Orchestration** | GitHub Actions (CI/CD, CRON scheduling) |
| **Data Warehouse** | Google BigQuery (Serverless SQL) |
| **Analytics** | Power BI (Microsoft Fabric) |
| **Security** | GitHub Secrets, GCP Service Accounts |


## High-Level Architecture

This pipeline follows a **cloud-native ELT design**, where raw data is loaded first and transformed later inside the warehouse.

<img width="1856" height="862" alt="Architecture" src="https://github.com/user-attachments/assets/3c605f48-4e6d-46fd-89ae-b18345884476" />


## Design Principles & Key Decisions

### 1. Headless Browser Scraping
[Source website](https://growthlist.co/india-startups/) loads data dynamically and requires user-like interaction (clicking a button to reveal data) to ensure full list is visible on the page. Below is the comparison b/w different tools for this purpose

| Feature                 | BeautifulSoup4   | Scrapy              | Selenium  | **Playwright (Recommended)**    |
| ----------------------- | ---------------- | ------------------- | --------- | ------------------------------- |
| **Can click buttons?**  | ❌ No             | ❌ No (not natively) | ✅ **Yes** | 🟢 **Yes**                      |
| **Handles JavaScript?** | ❌ No             | ❌ No                | ✅ **Yes** | 🟢 **Yes (Best-in-class)**      |
| **Speed**               | ⚡ **Very Fast**  | ⚡ Fast (Async)      | 🐢 Slow   | 🟢 **Fast**                     |
| **Learning Curve**      | 🟢 **Very Easy** | 🔴 Hard             | 🟡 Medium | 🟡 Medium                       |
| **Headless Mode**       | N/A              | N/A                 | ✅ Yes     | 🟢 **Yes (Native & optimized)** |

Playwright was chosen over BeautifulSoup, Scrapy, and Selenium because of:

1. Web Interaction: Because I want to interact with the browser (move to button and click it) BeautifulSoup and Scrapy are disqualified.
   
2. Auto-Waiting: Unlike Selenium, Playwright "waits" for elements to be visible/clickable before interacting. This prevents the script from crashing if page takes 2 seconds to load.
```python
 page.locator(".btn").click() #  auto-waits for button to appear before clicking
```

4. Headless mode: Runs web broswer in background without GUI. Runs faster and uses fewer resources.

### 2. Medallion Architecture (Bronze / Silver / Gold)

The warehouse is structured using a Medallion pattern to clearly separate data responsibilities.

<img width="663" height="364" alt="image" src="https://github.com/user-attachments/assets/91c3b12b-5ecb-43c0-ac7a-78d7d64eecbb" />

| Layer | Purpose |
|-----|--------|
| Bronze | Preserve raw data exactly as scraped. Acts as safety net, if transformation logic has a bug later or requirements change later, we still have original data without needing to re-scrape website. |
| Silver | Clean and standardize fresh data |
| Gold | Maintain historical, analytics-ready facts. This is the table we connect to Power BI for vizualization |

---

#### Bronze Layer (Raw Data)

| Table | Description |
|-----|------------|
| `stg_raw_latest` | Holds only the latest scrape (truncate & load) |
| `fct_raw_history` | Append-only table storing all raw records |

**Why two raw tables?**
- `stg_raw_latest` keeps transformations fast and cheap
- `fct_raw_history` preserves historical row data collected over time

---

#### Silver Layer (Clean data)

| Table | Description |
|-----|------------|
| `stg_clean_latest` | Cleaned version of the latest scrape |

Transformations include:
- Uppercasing categorical fields
- Parsing funding dates
- Normalizing multi-valued industries using `UNNEST`
- Splitting timestamp into date and time (UTC)

---

#### Gold Layer (Analytics)

| Table | Description |
|-----|------------|
| `fct_clean_history` | Historical fact table for reporting |

This table is populated using a **MERGE (UPSERT)** strategy to ensure:
- No duplicate funding events
- Existing records are updated if source data changes

The diagram below represents the schema and enforced data types for the `fct_clean_history` table.

### 3. Idempotent UPSERT Logic

A funding record is considered unique based on:

- Company Name  
- Country  
- Industry Type  
- Last Funding Date  

**Why this matters:**
- Startups raise multiple funding rounds
- Company name alone is not a stable identifier

**Behavior:**
- If a matching record exists → update non-key fields
- If no match exists → insert a new row

This ensures the Gold table always reflects the **most accurate version** of each funding event.

### 4. Cloud-to-Cloud Integration
- Direct integration between **Google BigQuery** and **Microsoft PowerBI**
- No local gateway required
- Fully automated using Scheduled Refresh


## Automation & Orchestration

The entire pipeline is orchestrated using **GitHub Actions**

### GitHub Actions Workflow Configuration

To enable full automation, we need to add the following GitHub Secrets:
| Secret Name | Description |
|-----|-----------|
| **GCP_SA_KEY** | Entire contents of bigquery-key.json |

### Workflow automatically:

- Installs Playwright browser binaries
- Sets up Python dependencies
- Authenticates with BigQuery
- Executes the ETL pipeline on schedule.

### Schedule (CRON)
30 18 * * 0
Runs every **Sunday at 6:30 PM UTC** (or Monday at 12:00 AM IST)

### Why GitHub Actions ?
- Works directly with Github 
- Free of cost 
- Easy CI/CD-style reproducibility


## Analytics & Visualization

### Data Connectivity

Gold table (`fct_clean_history`) is connected directly to **Power BI** via Import Data Connectivity Mode.

### Data Modelling

#### Logical Data Model
<img width="2888" height="1529" alt="Logical Model" src="https://github.com/user-attachments/assets/e53af8af-3b5d-4f6e-9277-aace33f20e67" />

#### Conceptial Data Model
<img width="3203" height="1849" alt="Conceptual Model" src="https://github.com/user-attachments/assets/bfc4fa56-2abf-498e-8d1b-393fba6fa8b7" />

#### Semantic Data Model
<img width="1062" height="607" alt="Data Model " src="https://github.com/user-attachments/assets/4fa9362b-be85-4d31-a862-d146bf7469aa" />


### Dashboard Features
- Where all the funding goes ?
- Industry-wise funding distribution
- Funding stage analysis

<img width="1325" height="698" alt="Report Screenshot" src="https://github.com/user-attachments/assets/bf854366-a43f-4ea3-aa16-fc91e613c503" />
<img width="1476" height="827" alt="image" src="https://github.com/user-attachments/assets/f8f1e4a9-42d6-4547-bbeb-e25f2013a76d" />


## What This Project Demonstrates

This project mirrors how **modern data platforms** are built in production environments using techniques like

- Headless browser-based data extraction
- Medallion (Bronze / Silver / Gold) architecture
- Cloud-native ELT pipelines
- Idempotent data loading using MERGE (UPSERT)
- CI/CD-based orchestration
- Direct cloud-to-cloud BI integration
	
## Future Enhancements

- Add data quality checks (Great Expectations)
- Add alerting on pipeline failures
- Extend to additional startup ecosystems
