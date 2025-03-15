        # Execute the scraping script and retrieve comments
        items = await page.evaluate(scrape_js)
        print(f"Scraped {len(items)} comments")

        # Save the scraped comments to a JSON file
        store_comments_to_json(items, "scraped_comments.json")

        # Close the browser
        await browser.close()
