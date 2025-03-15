def close_edge_tasks():
    """
    Terminates all running Microsoft Edge processes.
    """
    try:
        cmd = "taskkill /F /IM msedge.exe /T"
        subprocess.run(cmd, shell=True, check=True)
        print("All Microsoft Edge tasks have been terminated.")
    except Exception as e:
        print("Warning: Could not kill Edge tasks. Error:", e)
