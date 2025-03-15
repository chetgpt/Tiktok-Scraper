import asyncio
import subprocess
import os
import time
import socket
import json
from playwright.async_api import async_playwright

# -----------------------------
# Utility Functions
# -----------------------------

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

def store_comments_to_json(comments, filename="scraped_comments.json"):
    """Saves the scraped comments to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)
        print(f"Comments saved to {filename}.")
    except Exception as e:
        print(f"Failed to save comments to {filename}. Error:", e)

# -----------------------------
# JavaScript for Scraping Comments
# -----------------------------

scrape_js = r"""
(async () => {
    const delay = (ms) => new Promise(res => setTimeout(res, ms));

    // Find the comment container using several potential selectors
    function getCommentContainer() {
        const selectors = [
            ".css-7whb78-DivCommentListContainer",
            ".css-1qp5gj2-DivCommentListContainer",
            ".css-13wx63w-DivCommentObjectWrapper"
        ];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) return el;
        }
        return null;
    }

    // Scroll the comment container to load more comments
    async function scrollCommentContainer(container) {
        if (!container) return;
        let previousHeight = 0;
        for (let i = 0; i < 10; i++) {
            container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
            await delay(3000 + Math.random() * 2000);
            let currentHeight = container.scrollHeight;
            if (currentHeight === previousHeight) break;
            previousHeight = currentHeight;
        }
    }

    // Click "View more" buttons to expand replies
    async function clickViewMoreButtons(container) {
        if (!container) return;
        const viewMoreButtons = container.querySelectorAll('p, span, button, div');
        for (let btn of viewMoreButtons) {
            let text = (btn.textContent || "").trim();
            if (/(View|See|Load)\s+(more|all|\d+)\s+(replies|comments)/i.test(text)) {
                btn.click();
                await delay(2000 + Math.random() * 1000);
            }
        }
    }

    // Extract all visible comments from the container
    async function extractItems() {
        const container = getCommentContainer();
        if (!container) return [];

        const wrappers = container.querySelectorAll(".css-1gstnae-DivCommentItemWrapper");
        let items = [];
        for (let w of wrappers) {
            const userEl = w.querySelector(".css-13x3qpp-DivUsernameContentWrapper a[href^='/@']");
            const commentEl = w.querySelector("[data-e2e^='comment-level-']");
            const timeEl = w.querySelector("[data-e2e^='comment-time-']");

            const username = userEl ? userEl.textContent.trim() : null;
            const commentText = commentEl ? commentEl.textContent.trim() : null;
            const timeStamp = timeEl ? timeEl.textContent.trim() : null;

            if (username && commentText) {
                items.push({ username, commentText, timeStamp });
            }
        }
        return items;
    }

    // Main scraping logic: iteratively scroll and click until no more new comments load
    const container = getCommentContainer();
    if (container) {
        let previousCount = 0;
        let stableCount = 0;
        for (let attempt = 0; attempt < 20; attempt++) {
            await scrollCommentContainer(container);
            await clickViewMoreButtons(container);
            const currentItems = await extractItems();
            const currentCount = currentItems.length;
            if (currentCount > previousCount) {
                previousCount = currentCount;
                stableCount = 0;
            } else {
                stableCount++;
                if (stableCount >= 3) break;
            }
            await delay(5000 + Math.random() * 3000);
        }
    }
    const finalItems = await extractItems();
    return finalItems;
})();
"""

# -----------------------------
# Main Asynchronous Function
# -----------------------------

async def main():
    # Close any running Edge instances
    close_edge_tasks()
    time.sleep(2)

    # Define your Edge profile path (adjust this to your system)
    profile_path = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Profile 2"
    user_data_dir = os.path.dirname(profile_path)
    profile_directory = os.path.basename(profile_path)

    # Locate the Edge executable (update paths if necessary)
    msedge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        msedge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        print("[ERROR] Edge executable not found on system.")
        return

    # Specify the initial TikTok video URL (replace with your target URL)
    tiktok_video_url = "https://www.tiktok.com"

    # Command to launch Edge with remote debugging enabled
    cmd = [
        msedge_path,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "--remote-debugging-address=127.0.0.1",
        tiktok_video_url
    ]
    print("[INFO] Launching Edge with your existing profile...")
    proc = subprocess.Popen(cmd)
    print("Edge launched with PID:", proc.pid)

    # Wait for Edge to fully launch and the debugging port to open
    time.sleep(20)
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("[ERROR] Remote debugging port did not open in time.")
        proc.terminate()
        return
    else:
        print("[INFO] Remote debugging port is open.")

    # Start Playwright and connect to the running Edge instance
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        except Exception as e:
            print("[ERROR] Error connecting over CDP:", e)
            return

        # Access the browser context and page
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        await page.wait_for_load_state("networkidle", timeout=15000)
        print("[INFO] Connected to Edge via CDP. Current URL =", page.url)

        # Define the selector for the "next video" button.
        # (This selector may need adjustment based on TikTok’s actual layout.)
        next_video_selector = "button.TUXButton.TUXButton--capsule.TUXButton--medium.TUXButton--secondary.action-item.css-1egy55o:not([disabled])"

        # Loop to repeatedly scrape comments and then click next video
        num_videos = 5  # Set the number of videos to process
        for i in range(num_videos):
            print(f"\n[INFO] Processing video {i+1} of {num_videos}")

            # Ensure the page is fully loaded before scraping
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Execute the scraping script to extract comments
            comments = await page.evaluate(scrape_js)
            print(f"[INFO] Scraped {len(comments)} comments from video {i+1}")

            # Save the scraped comments to a JSON file (each video gets its own file)
            json_filename = f"scraped_comments_video_{i+1}.json"
            store_comments_to_json(comments, json_filename)

            # Attempt to click the "next video" button
            try:
                await page.click(next_video_selector)
                print(f"[INFO] Clicked next video button for video {i+1}")
            except Exception as e:
                print(f"[ERROR] Failed to click next video button on video {i+1}: {e}")
                break

            # Wait for the new video to load
            await asyncio.sleep(5)

        # Clean up: close the browser and terminate the Edge process
        await browser.close()
        print("[INFO] Browser closed; process complete.")
    proc.terminate()

# -----------------------------
# Main Execution
# -----------------------------

if __name__ == "__main__":
    asyncio.run(main())
