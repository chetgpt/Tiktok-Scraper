from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options  # Import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests


def get_tiktok_explore_video_links_selenium(url):
    """
    Fetches video links from the TikTok explore page using Selenium.

    Args:
        url: The URL of the TikTok explore page.

    Returns:
        A list of video links, or None if an error occurs.
    """
    options = Options()
    options.add_argument("--headless=new")  # Run Chrome in headless mode (no GUI)
    # options.add_argument("--disable-gpu") # Sometimes necessary on Linux
    # options.add_argument("--no-sandbox") # Sometimes necessary on Linux

    # Use webdriver_manager to automatically handle ChromeDriver.  This is the BEST way.
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        print("Make sure you have Chrome installed, and that webdriver_manager can find it.")
        print("You may need to install Chrome: https://www.google.com/chrome/")
        return None

    try:
        driver.get(url)

        # Wait for the video links to appear. This is CRUCIAL.
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/video/')]"))
            )
        except TimeoutException:
            print("Timed out waiting for video links to load. Check the XPath and increase timeout.")
            #If using headless mode, you will not see the page. Remove '--headless' to see the page.
            return None

        time.sleep(2)  # Wait for all elements to load

        # Extract the links using Selenium's find_elements method.
        video_links = []
        elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/video/')]")
        for element in elements:
            link = element.get_attribute('href')
            if link and link.startswith("http"):  # Ensure it's a full URL
               video_links.append(link)

        if not video_links:
            print("No video links found after waiting. Check the XPath.")
            return None
        print(video_links)
        return video_links

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        driver.quit()  # IMPORTANT: Close the browser instance.


if __name__ == "__main__":
    explore_url = "https://www.tiktok.com/explore"
    video_links = get_tiktok_explore_video_links_selenium(explore_url)

    if video_links:
        print("TikTok Explore Page Video Links:")
        for link in video_links:
            print(link)
    else:
        print("No video links found or an error occurred.")