import asyncio
import subprocess
import os
import time
import socket
from playwright.async_api import async_playwright

def wait_for_port(host, port, timeout=90):
    """Wait until a TCP port is open on the given host."""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                return True
        except Exception:
            if time.time() - start_time > timeout:
                return False
            time.sleep(1)

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
    
    # Wait until port 9222 is open on 127.0.0.1.
    if not wait_for_port("127.0.0.1", 9222, timeout=90):
        print("Remote debugging port did not open in time. Please avoid interacting with the browser until it initializes.")
        return
    else:
        print("Remote debugging port is open.")

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
        await page.wait_for_load_state("networkidle", timeout=15000)

        # Inline JavaScript code wrapped in an IIFE.
        js_code = r"""
        (async () => {
            async function getAllComments() {
                function scrollToBottom(container) {
                    return new Promise(resolve => {
                        container.scrollTo({
                            top: container.scrollHeight,
                            behavior: 'smooth'
                        });
                        const observer = new IntersectionObserver((entries) => {
                            entries.forEach(entry => {
                                if (entry.isIntersecting) {
                                    observer.disconnect();
                                    resolve();
                                }
                            });
                        }, {
                            root: container,
                            threshold: 0.1,
                        });
                        const lastComment = container.querySelector(".css-1gstnae-DivCommentItemWrapper:last-child");
                        if (lastComment) {
                            observer.observe(lastComment);
                        } else {
                            resolve();
                        }
                    });
                }
        
                async function extractCommentData(commentContainer) {
                    const usernameElement = commentContainer.querySelector(".css-13x3qpp-DivUsernameContentWrapper a[href^='/@']");
                    const username = usernameElement ? usernameElement.textContent.trim() : null;
                    const commentTextElement = commentContainer.querySelector("[data-e2e^='comment-level-']");
                    const commentText = commentTextElement ? commentTextElement.textContent.trim() : null;
                    const timestampElement = commentContainer.querySelector("[data-e2e^='comment-level-'] + div > span:first-child");
                    const timeStamp = timestampElement ? timestampElement.textContent.trim() : null;
                    const likeCountElement = commentContainer.querySelector("[aria-label^='Like video']");
                    let likeCount = 0;
                    if (likeCountElement) {
                        const likeCountMatch = likeCountElement.getAttribute('aria-label').match(/(\d+(\.\d+)?)[KMB]?/);
                        if (likeCountMatch) {
                            let count = parseFloat(likeCountMatch[1]);
                            const multiplierChar = likeCountElement.getAttribute('aria-label').match(/[KMB]/);
                            const multiplier = multiplierChar ? multiplierChar[0] : '';
                            switch (multiplier) {
                                case 'K': count *= 1000; break;
                                case 'M': count *= 1000000; break;
                                case 'B': count *= 1000000000; break;
                            }
                            likeCount = Math.round(count);
                        }
                    } else {
                        const likeCountSpan = commentContainer.querySelector(".css-1nd5cw-DivLikeContainer span");
                        likeCount = likeCountSpan ? parseInt(likeCountSpan.textContent.replace(/[^0-9]/g, ''), 10) : 0;
                    }
                    return { username, commentText, timeStamp, likeCount };
                }
        
                const commentContainer = document.querySelector(".css-7whb78-DivCommentListContainer");
                if (!commentContainer) {
                    console.error("Comment container not found!");
                    return [];
                }
        
                let allComments = [];
                let lastHeight = commentContainer.scrollHeight;
                let newHeight;
                let maxScrolls = 50;
                let scrollCount = 0;
        
                while (scrollCount < maxScrolls) {
                    await scrollToBottom(commentContainer);
                    newHeight = commentContainer.scrollHeight;
                    if (newHeight === lastHeight) break;
                    lastHeight = newHeight;
                    scrollCount++;
                }
        
                const commentContainers = commentContainer.querySelectorAll(".css-1gstnae-DivCommentItemWrapper");
                for (const container of commentContainers) {
                    const commentData = await extractCommentData(container);
                    if (commentData.username && commentData.commentText) {
                        allComments.push(commentData);
                    }
                    const repliesContainer = container.querySelector(".css-9kgp5o-DivReplyContainer");
                    if (repliesContainer) {
                        const replyContainers = repliesContainer.querySelectorAll(".css-1gstnae-DivCommentItemWrapper");
                        for (const replyContainer of replyContainers) {
                            const replyData = await extractCommentData(replyContainer);
                            if (replyData.username && replyData.commentText) {
                                allComments.push(replyData);
                            }
                        }
                    }
                }
                console.log(allComments);
                return allComments;
            }
            return await getAllComments();
        })();
        """

        print("Injecting inline JavaScript code...")
        try:
            comments = await page.evaluate(js_code)
        except Exception as e:
            print("Error during JavaScript evaluation:", e)
            return
        
        print("Comments extracted:")
        for comment in comments:
            print(comment)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
