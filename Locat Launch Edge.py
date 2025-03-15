    # Locate Microsoft Edge executable
    msedge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        msedge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(msedge_path):
        print("Edge executable not found.")
        return

    # Specify the TikTok video URL (replace with your target URL)
    tiktok_video_url = "https://www.tiktok.com"

    # Command to launch Edge with debugging enabled
    cmd = [
        msedge_path,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "--remote-debugging-address=127.0.0.1",
        tiktok_video_url
    ]
    print("Launching Edge with your existing profile...")
    proc = subprocess.Popen(cmd)
    print("Edge launched with PID:", proc.pid)
    
    # Wait for Edge to fully launch
    time.sleep(20)
    
    # Check if the debugging port is available
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("Remote debugging port did not open in time.")
        return
    else:
        print("Remote debugging port is open.")
