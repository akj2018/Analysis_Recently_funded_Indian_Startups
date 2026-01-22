from google.cloud import bigquery
import os

# 1. Official env variable name for the key
os.environ["GOOGLE_APPLICATION_CREDENTIAL"] = "bigquery-key.json"

def run_transformations():
    # Query for Staging Table for fresh transformed data (Silver Medallion)
    # CREATE OR REPLACE to ensure the 'Latest' table is always fresh
    query_add_cleaned_data_to_staging_table = """
    CREATE OR REPLACE TABLE `startup-data-analysis.transformed_data.stg_clean_latest` AS
    SELECT
      UPPER(Name) AS `Company Name`,
      UPPER(Country) AS `Country`,
      Website,
      UPPER(`Industry Type`) AS `Industry Type`,
      `Funding Amount USD`,
      UPPER(`Funding Type`) AS `Funding Type`,
      PARSE_DATE('%b %Y',`Last Funding Date`) AS `Last Funding Date`,
      SAFE_CAST(SPLIT(FORMAT_DATETIME('%Y-%m-%d %H:%M:%S',scraped_at_utc), " ")[SAFE_OFFSET(0)] AS DATE) AS `Scraped Date`,
      SAFE_CAST(SPLIT(FORMAT_DATETIME('%Y-%m-%d %H:%M:%S',scraped_at_utc), " ")[SAFE_OFFSET(1)] AS TIME) AS `Scraped Time UTC`
    FROM `startup-data-analysis.raw_data.stg_raw_latest`,
      UNNEST(SPLIT(Industry)) AS `Industry Type`
    """

    # Logic to create History Table if not exists, using schema of stg_clean_latest
    query_check_history_table_exists = """
    CREATE TABLE IF NOT EXISTS `startup-data-analysis.transformed_data.fct_clean_history` AS 
    SELECT * FROM `startup-data-analysis.transformed_data.stg_clean_latest` LIMIT 0
    """

    # MERGE logic: Keep only unique records based on Name, Country, Industry, and Date
    query_upsert_into_history_table = """
    MERGE `startup-data-analysis.transformed_data.fct_clean_history` T
    USING `startup-data-analysis.transformed_data.stg_clean_latest` S
        ON T.`Company Name` = S.`Company Name` 
        AND T.Country = S.Country
        AND T.`Industry Type` = S.`Industry Type`
        AND T.`Last Funding Date` = S.`Last Funding Date`

    WHEN MATCHED THEN
            UPDATE SET 
                T.Website = S.Website,
                T.`Funding Amount USD` = S.`Funding Amount USD`,
                T.`Funding Type` = S.`Funding Type`,
                T.`Scraped Date` = S.`Scraped Date`,
                T.`Scraped Time UTC` = S.`Scraped Time UTC`

    WHEN NOT MATCHED THEN
        INSERT (
            `Company Name`, Country, Website, `Industry Type`, 
            `Funding Amount USD`, `Funding Type`, `Last Funding Date`, 
            `Scraped Date`, `Scraped Time UTC`
        )
        VALUES (
            S.`Company Name`, S.Country, S.Website, S.`Industry Type`, 
            S.`Funding Amount USD`, S.`Funding Type`, S.`Last Funding Date`, 
            S.`Scraped Date`, S.`Scraped Time UTC`
        );
    """

    print("Starting transformations...")
    client = bigquery.Client(location='asia-south2') # must be same as location of dataset

    client.query_and_wait(query_add_cleaned_data_to_staging_table)
    print("Successfully transformed raw data from stg_raw_lastest and loaded to stg_clean_latest Table")

    client.query_and_wait(query_check_history_table_exists)
    print("Checked if fct_clean_history table exists or not")

    client.query_and_wait(query_upsert_into_history_table)
    print("Successfully loaded to fct_clean_history Table")

if __name__ == "__main__":
    run_transformations()



