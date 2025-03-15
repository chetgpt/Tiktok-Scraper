import subprocess
import os
import time
import pyautogui
import json
import pyperclip  # Import pyperclip


def open_edge_with_profile(profile_path, initial_url="https://www.tiktok.com"):
    """Opens Microsoft Edge with a specified user profile and navigates to TikTok."""
    try:
        edge_paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ]
        edge_exe = None
        for path in edge_paths:
            if os.path.exists(path):
                edge_exe = path
                break

        if edge_exe is None:
            raise FileNotFoundError("Microsoft Edge executable (msedge.exe) not found.")

        command = [
            edge_exe,
            "--profile-directory=" + os.path.basename(profile_path),
            initial_url
        ]
        # Use shell=False for security and to avoid issues with spaces in paths
        process = subprocess.Popen(command, cwd=os.path.dirname(profile_path), shell=False,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        time.sleep(5)  # Give Edge time to start
        return process

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error launching Edge: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def inject_and_run_js(js_code):
    """Injects and runs JavaScript code in the Edge DevTools console."""
    try:
        # Open DevTools (F12)
        pyautogui.press('f12')
        time.sleep(2)  # Wait for DevTools to open

        # Go to Console tab.  This is now more robust.
        pyautogui.hotkey('ctrl', 'shift', 'j')  # Works on most systems
        time.sleep(1)

        # Paste the JavaScript code
        pyautogui.write(js_code)
        time.sleep(0.5) #give time to paste

        # Press Enter to execute the code
        pyautogui.press('enter')
        time.sleep(5)  # Wait for the script to finish.  Adjust as needed.

        # Copy console output to clipboard (Ctrl+A, Ctrl+C)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.5)

        # Close DevTools (F12)
        pyautogui.press('f12')
        time.sleep(1)

    except Exception as e:
        print(f"Error injecting JavaScript: {e}")

def save_comments_to_file(comments, filename="tiktok_comments.json"):
    """Saves the extracted comments to a JSON file."""
    try:
        with open(filename, "a", encoding="utf-8") as f:  # Append mode ("a")
            json.dump(comments, f, ensure_ascii=False, indent=4)
            f.write("\n") # Add a newline for separation between runs
        print(f"Comments saved to {filename}")
    except Exception as e:
        print(f"Error saving comments to file: {e}")


def simulate_tiktok_viewing(duration_per_video, num_videos, profile_path, js_code):
    """Main function to simulate TikTok viewing and extract comments."""

    edge_process = open_edge_with_profile(profile_path)
    if not edge_process:
        return

    for i in range(num_videos):
        print(f"Simulating viewing of video {i + 1} of {num_videos}")
        try:
            # Simulate watching a video
            simulate_tiktok_viewing_single(duration_per_video)

            # Extract and save comments
            inject_and_run_js(js_code)
            # --- Use pyperclip here ---
            comments_str = pyperclip.paste()
            try:
                comments = json.loads(comments_str)
                save_comments_to_file(comments)
            except json.JSONDecodeError:
                print("Error: Could not decode JSON from clipboard.  The clipboard content might not be valid JSON.")
                print(f"Clipboard content: {comments_str}")

            # Navigate to the next video (Down arrow key)
            pyautogui.press('down')
            time.sleep(2)  # Wait for the next video to load


        except pyautogui.FailSafeException:
            print("Simulation stopped by user (failsafe triggered).")
            break
        except Exception as e:
            print(f"An error occurred during video {i + 1}: {e}")
            break

    if edge_process:
        edge_process.terminate()  # Cleanly close Edge
        try:
            edge_process.wait(timeout=5)  # Give it a few seconds to close
        except subprocess.TimeoutExpired:
            edge_process.kill()  # Force kill if it doesn't close
        print("Microsoft Edge closed.")


def simulate_tiktok_viewing_single(duration_seconds):
    """Simulates viewing a single TikTok video."""
    start_time = time.time()
    print(f"Simulating viewing. Will wait for {duration_seconds} seconds.")
    print("Move your mouse to a corner of the screen to stop.")
    while time.time() - start_time < duration_seconds:
        time.sleep(10)  # Check every 10 seconds
        pyautogui.move(1, 1)  # Prevent screen saver.
        pyautogui.move(-1, -1)

# --- Example Usage ---
if __name__ == "__main__":
    profile_path = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Profile 2"  # Your profile path
    duration_per_video = 30  # Simulate watching each video for 30 seconds
    num_videos = 5  # Simulate watching 5 videos

    # Load the JavaScript code from a file (best practice)
    with open(r"C:\Users\DELL\Downloads\tiktok_comment_scraper.js", "r", encoding="utf-8") as js_file:
        js_code = js_file.read()

    simulate_tiktok_viewing(duration_per_video, num_videos, profile_path, js_code)