    # Start Playwright and connect to the browser
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        except Exception as e:
            print("Error connecting over CDP:", e)
            return

        # Access the browser context and page
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        print("Connected to Edge via CDP. Current URL:", page.url)
        await page.wait_for_load_state("networkidle", timeout=15000)
