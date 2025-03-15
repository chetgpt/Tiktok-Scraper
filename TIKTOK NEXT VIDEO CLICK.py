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

async def attach_event_listeners(page):
    """
    Attaches event listeners that record:
      - Throttled mousemove events.
      - Click events that traverse the composed path, pick the first ancestor that is a button,
        and record its outerHTML, a DOM path, and a "robust selector" (using id if available,
        otherwise tag plus classes).
    """
    await page.evaluate("""
        (() => {
            if (!window.recordedEvents) {
                window.recordedEvents = [];
                
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
                
                function getRobustSelector(el) {
                    if (!el) return "";
                    if (el.id) return "#" + el.id;
                    let selector = el.tagName.toLowerCase();
                    if (el.classList.length > 0) {
                        selector += "." + Array.from(el.classList).join(".");
                    }
                    return selector;
                }
                
                document.addEventListener('mousemove', throttle(function(e) {
                    window.recordedEvents.push({
                        event: 'mousemove',
                        x: e.clientX,
                        y: e.clientY,
                        timestamp: Date.now()
                    });
                }, 100));
                
                document.addEventListener('click', function(e) {
                    let path = e.composedPath();
                    let targetElem = e.target;
                    // Traverse the composed path and pick the first ancestor that is a button.
                    for (let el of path) {
                        if (el.tagName && el.tagName.toLowerCase() === 'button') {
                            targetElem = el;
                            break;
                        }
                    }
                    let domPath = [];
                    let el = targetElem;
                    while (el) {
                        if (el.tagName) {
                            domPath.unshift(el.tagName);
                        }
                        el = el.parentElement;
                    }
                    let robustSelector = getRobustSelector(targetElem);
                    window.recordedEvents.push({
                        event: 'click',
                        targetHTML: targetElem.outerHTML,
                        domPath: domPath.join(" > "),
                        robustSelector: robustSelector,
                        timestamp: Date.now()
                    });
                }, true);
            }
        })();
    """)
    print("[INFO] Event listeners attached.")

async def open_browser_and_automate_clicks():
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

    # Launch Edge with remote debugging enabled.
    launch_url = "https://www.tiktok.com"
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

    # Wait for Edge and the remote debugging port.
    time.sleep(20)
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("[ERROR] Remote debugging port (9222) not open in time.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        await page.wait_for_load_state("networkidle", timeout=15000)
        print("[INFO] Connected to Edge. Current page URL =", page.url)

        # Attach event listeners to record interactions.
        await attach_event_listeners(page)
        
        # Optional: simulate a mouse move for demonstration.
        await page.mouse.move(500, 300)
        print("[INFO] Simulated mouse move to (500,300)")
        await asyncio.sleep(1)
        
        # Automatically click using the known robust selector.
        # Append :not([disabled]) to ensure we only select an enabled button.
        targetSelector = "button.TUXButton.TUXButton--capsule.TUXButton--medium.TUXButton--secondary.action-item.css-1egy55o:not([disabled])"
        print("[INFO] Automatically clicking on element with selector:", targetSelector)
        try:
            await page.click(targetSelector)
            print("[INFO] Automatic click executed.")
        except Exception as e:
            print("[ERROR] Failed to automatically click:", e)
        
        # Wait a few seconds to allow any events to be recorded.
        await asyncio.sleep(5)
        
        # Retrieve and display the recorded events for visual confirmation.
        events = await page.evaluate("window.recordedEvents")
        print("[INFO] Recorded events:")
        for event in events:
            print(event)
        
        await browser.close()
        print("[INFO] Browser closed; process complete.")

if __name__ == "__main__":
    asyncio.run(open_browser_and_automate_clicks())
