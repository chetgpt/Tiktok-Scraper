async def open_browser_and_automate_clicks():
    """
    Launches Microsoft Edge, connects via Playwright, performs automation tasks,
    removes listeners, and clicks the 'next video' button multiple times.
    """
    # Close any running Edge processes
    close_edge_tasks()
    time.sleep(2)

    # Specify your Edge profile path (update this path as needed)
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

    # Launch Edge with remote debugging enabled
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

    # Wait for Edge and the remote debugging port
    time.sleep(20)  # Initial wait for Edge to start
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("[ERROR] Remote debugging port (9222) not open in time.")
        proc.terminate()
        return

    async with async_playwright() as p:
        # Connect to the running Edge instance
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        contexts = browser.contexts
        context = contexts[0] if contexts else await browser.new_context()
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        # Wait for the page to load
        await page.wait_for_load_state("networkidle", timeout=15000)
        print("[INFO] Connected to Edge. Current page URL =", page.url)

        # Attach event listeners to record initial interactions
        await attach_event_listeners(page)
        
        # Simulate a mouse move (optional, for demonstration)
        await page.mouse.move(500, 300)
        print("[INFO] Simulated mouse move to (500,300)")
        await asyncio.sleep(1)
        
        # Define the selector for the "next video" button
        target_selector = "button.TUXButton.TUXButton--capsule.TUXButton--medium.TUXButton--secondary.action-item.css-1egy55o:not([disabled])"
        print("[INFO] Automatically clicking on element with selector:", target_selector)
        
        # Perform the initial automated click
        try:
            await page.click(target_selector)
            print("[INFO] Automatic click executed.")
        except Exception as e:
            print("[ERROR] Failed to automatically click:", e)
        
        # Wait to allow events to be recorded
        await asyncio.sleep(5)
        
        # Retrieve and display recorded events
        events = await page.evaluate("window.recordedEvents")
        print("[INFO] Recorded events:")
        for event in events:
            print(event)
        
        # Remove event listeners before additional clicks
        await remove_event_listeners(page)
        
        # Perform multiple clicks on the "next video" button
        num_clicks = 3  # Number of additional clicks (configurable)
        for i in range(num_clicks):
            print(f"[INFO] Performing click {i+1} of {num_clicks}")
            try:
                await page.click(target_selector)
                print(f"[INFO] Click {i+1} executed.")
            except Exception as e:
                print(f"[ERROR] Failed to click on attempt {i+1}:", e)
            await asyncio.sleep(2)  # Wait 2 seconds between clicks
        
        # Clean up
        await browser.close()
        print("[INFO] Browser closed; process complete.")
    
    # Ensure the Edge process is terminated
    proc.terminate()
