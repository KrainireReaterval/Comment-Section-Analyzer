import asyncio
from playwright import async_api
from playwright.async_api import expect

async def run_test():
    pw = None
    browser = None
    context = None
    
    try:
        # Start a Playwright session in asynchronous mode
        pw = await async_api.async_playwright().start()
        
        # Launch a Chromium browser in headless mode with custom arguments
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--window-size=1280,720",         # Set the browser window size
                "--disable-dev-shm-usage",        # Avoid using /dev/shm which can cause issues in containers
                "--ipc=host",                     # Use host-level IPC for better stability
                "--single-process"                # Run the browser in a single process mode
            ],
        )
        
        # Create a new browser context (like an incognito window)
        context = await browser.new_context()
        context.set_default_timeout(5000)
        
        # Open a new page in the browser context
        page = await context.new_page()
        
        # Navigate to your target URL and wait until the network request is committed
        await page.goto("http://localhost:8080", wait_until="commit", timeout=10000)
        
        # Wait for the main page to reach DOMContentLoaded state (optional for stability)
        try:
            await page.wait_for_load_state("domcontentloaded", timeout=3000)
        except async_api.Error:
            pass
        
        # Iterate through all iframes and wait for them to load as well
        for frame in page.frames:
            try:
                await frame.wait_for_load_state("domcontentloaded", timeout=3000)
            except async_api.Error:
                pass
        
        # Interact with the page elements to simulate user flow
        # -> Input an invalid URL string 'https://example.com/watch?v=abcdefghijk' into the YouTube Video URL field and attempt to start analysis to trigger validation.
        frame = context.pages[-1]
        # Input an invalid YouTube video URL into the YouTube Video URL field
        elem = frame.locator('xpath=html/body/div/div/main/div[2]/div/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('https://example.com/watch?v=abcdefghijk')
        

        frame = context.pages[-1]
        # Click the Start Analysis button to trigger validation
        elem = frame.locator('xpath=html/body/div/div/main/div[2]/div/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # -> Input a malformed URL 'not_a_url' into the YouTube Video URL field and attempt to start analysis to trigger validation.
        frame = context.pages[-1]
        # Input a malformed URL into the YouTube Video URL field
        elem = frame.locator('xpath=html/body/div/div/main/div[2]/div/div/input').nth(0)
        await page.wait_for_timeout(3000); await elem.fill('not_a_url')
        

        frame = context.pages[-1]
        # Click the Start Analysis button to trigger validation
        elem = frame.locator('xpath=html/body/div/div/main/div[2]/div/button').nth(0)
        await page.wait_for_timeout(3000); await elem.click(timeout=5000)
        

        # --> Assertions to verify final state
        frame = context.pages[-1]
        await expect(frame.locator('text=Please enter a valid YouTube URL').first).to_be_visible(timeout=30000)
        await asyncio.sleep(5)
    
    finally:
        if context:
            await context.close()
        if browser:
            await browser.close()
        if pw:
            await pw.stop()
            
asyncio.run(run_test())
    