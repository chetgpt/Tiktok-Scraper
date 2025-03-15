import asyncio
import subprocess
import os
import time
from playwright.async_api import async_playwright

async def main():
    # Configure your profile details.
    profile_path = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Profile 2"
    user_data_dir = os.path.dirname(profile_path)  # Parent directory of your profile
    profile_directory = os.path.basename(profile_path)

    # Locate the full path to msedge.exe.
    msedge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        msedge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        print("Edge executable not found.")
        return

    # Launch Edge with your existing profile and enable remote debugging.
    cmd = [
        msedge_path,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "--remote-debugging-address=127.0.0.1",
        "https://www.tiktok.com"
    ]
    print("Launching Edge with your existing profile...")
    proc = subprocess.Popen(cmd)
    print("Edge launched with PID:", proc.pid)

    # Allow extra time for Edge to initialize.
    time.sleep(20)

    async with async_playwright() as p:
        try:
            # Connect to the running Edge instance using CDP (IPv4).
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        except Exception as e:
            print("Error connecting over CDP:", e)
            return

        # Use the first available context/page or create a new one.
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()
        print("Connected to Edge via CDP. Current URL:", page.url)


if __name__ == "__main__":
    asyncio.run(main())