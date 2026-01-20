from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    # Select Chromium browser engine
    browser = p.chromium.launch(headless=False) # default is headless=True, headless=False for debugging
    
    # create context
    # using context we can define page properties like viewport dimensions
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080}
    )

    # create page aka browser tab which we'll be using to do everything
    page = browser.new_page() 

    # go to page and wait for first result to appear
    page.goto("https://playwright.dev") 
    # page.wait_for_selector("div[data-target=directory-first-item]")
    
    print(page.title())

    # Close the page, then broswer to end the connection
    page.close()
    browser.close()

