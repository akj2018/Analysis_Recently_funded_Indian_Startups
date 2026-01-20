from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


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

        # Get header
        header_cells = target_table.find("thead").find_all("th")
        headers = [th.get_text(strip=True) for th in header_cells]
        
        # 3. Get  Rows
        rows = target_table.find("tbody").find_all("tr")

        for row in rows:
            cells = row.find_all("td")
            item = {header: cell.get_text(strip=True) for header, cell in zip(headers, cells)}
            scraped_data.append(item)

    print(scraped_data)





        
    

    # Close the page, then broswer to end the connection
    page.close()
    browser.close()

