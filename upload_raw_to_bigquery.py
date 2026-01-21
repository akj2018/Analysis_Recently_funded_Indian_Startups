from google.cloud import bigquery
import os

# 1. Tell python script where key is to allow talking to cloud
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "bigquery-key.json"

def upload_to_bigquery(data_list):

    # 2. Initialize client
    client = bigquery.Client()

    # 3. Define Table IDs (Project.Dataset.Table)
    latest_table_id = "startup-data-analysis.raw_data.stg_raw_latest"
    history_table_id = "startup-data-analysis.raw_data.fct_raw_history"

    # 4. Create job configuration for 'Latest' job (WRITE_TRUNCATE)
    # Wipe the table data before adding 100 rows
    latest_job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
        autodetect=True
    )

    # Create job configuration for 'History' job (WRITE_APPEND)
    # Append rows at end of table 
    history_job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        autodetect=True
    )

    # 5. Send list of object to load into table
    client.load_table_from_json(json_rows=data_list, 
                                destination=latest_table_id, 
                                job_config=latest_job_config).result()
    
    client.load_table_from_json(json_rows=data_list,
                                destination=history_table_id,
                                job_config=history_job_config).result()
    
    print("Success: Data uploaded to both Staging and History!")