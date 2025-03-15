import subprocess
import os
import time
import socket
import asyncio
from playwright.async_api import async_playwright

def close_edge_tasks():
    """Terminates all running Microsoft Edge processes."""
    try:
        cmd = "taskkill /F /IM msedge.exe /T"
        subprocess.run(cmd, shell=True, check=True)
        print("All Microsoft Edge tasks have been terminated.")
    except Exception as e:
        print("Warning: Could not kill Edge tasks. Error:", e)

def wait_for_port(host, port, timeout=90):
    """Waits for a network port to become available."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)

async def attach_scroll_listener(page):
    """
    Waits for the comment container (assumed to have the class
    'css-7whb78-DivCommentListContainer') to appear and attaches
    a scroll listener that records scroll events.
    """
    # Wait for the scrollable comment container to appear.
    await page.wait_for_selector('.css-7whb78-DivCommentListContainer', timeout=15000)
    await page.evaluate("""
        (() => {
            const container = document.querySelector('.css-7whb78-DivCommentListContainer');
            if (!container) {
                console.warn("Comment container not found");
                return;
            }
            if (!window.scrollEvents) {
                window.scrollEvents = [];
            }
            function throttle(callback, delay) {
                let last;
                return function() {
                    const now = Date.now();
                    if (!last || now - last >= delay) {
                        last = now;
                        callback.apply(this, arguments);
                    }
                }
            }
            const recordScroll = throttle(() => {
                window.scrollEvents.push({
                    scrollTop: container.scrollTop,
                    scrollLeft: container.scrollLeft,
                    timestamp: Date.now()
                });
            }, 100);
            container.addEventListener('scroll', recordScroll);
        })();
    """)
    print("[INFO] Scroll listener attached to the comment container.")

async def open_browser_with_profile_and_record_scroll():
    # Close any running Edge processes.
    close_edge_tasks()
    time.sleep(2)
    
    # Specify your logged-in profile path.
    profile_path = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Profile 2"
    user_data_dir = os.path.dirname(profile_path)
    profile_directory = os.path.basename(profile_path)
    
    # Locate the Edge executable.
    msedge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        msedge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        print("[ERROR] Edge executable not found on system.")
        return
    
    # URL to launch (adjust as needed).
    launch_url = "https://www.tiktok.com"
    
    # Launch Edge with the specified user profile and remote debugging enabled.
    cmd = [
        msedge_path,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "--remote-debugging-address=127.0.0.1",
        launch_url
    ]
    print("[INFO] Launching Edge with your existing profile...")
    proc = subprocess.Popen(cmd)
    print("Edge launched with PID:", proc.pid)
    
    # Wait for Edge to open and remote debugging to be available.
    time.sleep(20)
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("[ERROR] Remote debugging port (9222) not open in time.")
        return
    
    # Connect to Edge using Playwright.
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        
        # Wait until the page is fully loaded.
        await page.wait_for_load_state("networkidle", timeout=15000)
        print("[INFO] Connected to Edge. Current page URL =", page.url)
        
        # Attach the scroll listener to the comment container.
        await attach_scroll_listener(page)
        
        print("[INFO] Recording scroll events for 30 seconds...")
        await asyncio.sleep(30)
        
        # Retrieve and display the recorded scroll events.
        scroll_events = await page.evaluate("window.scrollEvents")
        print("[INFO] Recorded scroll events:")
        if scroll_events:
            for event in scroll_events:
                print(event)
        else:
            print("No scroll events recorded.")
        
        await browser.close()
        print("[INFO] Browser closed; process complete.")

if __name__ == "__main__":
    asyncio.run(open_browser_with_profile_and_record_scroll())
