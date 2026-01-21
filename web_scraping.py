import re

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from upload_raw_to_bigquery import upload_to_bigquery


with sync_playwright() as p:
    # 1. Select browser engine
    browser = p.chromium.launch(headless=False) # default is headless=True, headless=False for debugging
    context = browser.new_context( 
        viewport={"width": 1920, "height": 1080} # using context we can define page properties like viewport dimensions
    )
    page = browser.new_page() 

    # 2. go to page and wait for table to appear 
    page.goto("https://growthlist.co/india-startups") 

    #  Wait for the table wrapper to ensure the JS has rendered the table
    page.wait_for_selector('div[class*="ninja_table_wrapper"]')

    # 3. Interaction (DO THIS BEFORE SOUP)
    # Target the dropdown and select '100' to load more data into the DOM
    tfoot_locator = page.locator('div[class*="ninja_table_wrapper"]').locator("tfoot")
    dropdown = page.locator("select.nt_pager_selection")
    dropdown.select_option("100")

    # Wait a moment for the table to reload with 100 items
    page.wait_for_timeout(2000)

    # 4. Parsing (Capture the snapshot AFTER the interaction)
    page_content = page.content()
    soup = BeautifulSoup(page_content, 'html.parser')

    target_table = soup.select_one('table[data-unique_identifier^="ninja_table_unique_id_"]')
    scraped_data = []

    if target_table:

        # Adding date and time of scraped item in iso 8601 format
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        # Get header
        header_cells = target_table.find("thead").find_all("th")
        pattern = r'[^a-zA-Z0-9_\s]' # remove invalid characters from column name
        headers = [re.sub(pattern, "", th.get_text(strip=True)) for th in header_cells]
        
        # Get  Rows
        rows = target_table.find("tbody").find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            item = {header: cell.get_text(strip=True) for header, cell in zip(headers, cells)}
            item["scraped_at_utc"] = timestamp
            scraped_data.append(item)

    # Close the page, then broswer to end the connection
    page.close()
    browser.close()

if scraped_data:
    print(f'Found {len(scraped_data)} records. Upload to BigQuery')
    upload_to_bigquery(scraped_data)

    # Run transformation immediately after upload
    from transform_raw_data import run_transformations
    run_transformations()

else:
    print("No data found to upload via web scraping")

