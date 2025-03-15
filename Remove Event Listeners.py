async def remove_event_listeners(page):
    """
    Removes the event listeners previously attached to the page.
    """
    await page.evaluate("""
        (() => {
            if (window.mousemoveListener) {
                document.removeEventListener('mousemove', window.mousemoveListener);
                window.mousemoveListener = null;
            }
            if (window.clickListener) {
                document.removeEventListener('click', window.clickListener, true);
                window.clickListener = null;
            }
        })();
    """)
    print("[INFO] Event listeners removed.")
