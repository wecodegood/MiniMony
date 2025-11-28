from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=False)
        
        # Create a new page
        page = browser.new_page()
        
        # Your code here
        print("Playwright initialized successfully!")
        print(f"Browser: {browser.browser_type().name}")
        
        # Example: Navigate to a page
        # page.goto('https://example.com')
        
        # Keep browser open for demonstration
        input("Press Enter to close the browser...")
        
        # Close browser
        browser.close()

if __name__ == "__main__":
    run()