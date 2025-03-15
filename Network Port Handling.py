def wait_for_port(host, port, timeout=90):
    """
    Waits for a network port to become available.
    Returns True if the port is available within the timeout, False otherwise.
    """
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)
