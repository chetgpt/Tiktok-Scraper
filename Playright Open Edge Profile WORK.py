import asyncio
import subprocess
import os
import time
from playwright.async_api import async_playwright

async def main():
    # Path to your profile folder (adjust if necessary)
    profile_path = r"C:\Users\DELL\AppData\Local\Microsoft\Edge\User Data\Profile 2"
    user_data_dir = os.path.dirname(profile_path)  # Parent folder of the profile
    profile_directory = os.path.basename(profile_path)

    # Locate msedge.exe from possible installation paths
    edge_exe_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = None
    for path in edge_exe_paths:
        if os.path.exists(path):
            edge_exe = path
            break
    if not edge_exe:
        print("Edge executable not found.")
        return

    # Launch Edge with your existing profile and enable remote debugging
    cmd = [
        edge_exe,
        f"--profile-directory={profile_directory}",
        f"--user-data-dir={user_data_dir}",
        "--remote-debugging-port=9222",
        "https://www.tiktok.com"
    ]
    print("Launching Edge with your existing profile...")
    proc = subprocess.Popen(cmd)
    print("Edge launched with PID:", proc.pid)
    # Wait for Edge to fully launch and load TikTok
    time.sleep(10)

    async with async_playwright() as p:
        try:
            # Connect to the running Edge instance via CDP
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            # Use the existing context/page from the connected browser
            contexts = browser.contexts
            if contexts:
                context = contexts[0]
            else:
                context = await browser.new_context()
            pages = context.pages
            if pages:
                page = pages[0]
            else:
                page = await context.new_page()

            print("Connected to Edge via CDP. Current URL:", page.url)
            # Wait until the page is fully loaded
            await page.wait_for_load_state("networkidle", timeout=15000)

            # Inject JavaScript to scroll and extract comments
            js_code = r"""
            async function scrollToBottom(container) {
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
                            case 'K':
                                count *= 1000;
                                break;
                            case 'M':
                                count *= 1000000;
                                break;
                            case 'B':
                                count *= 1000000000;
                                break;
                        }
                        likeCount = Math.round(count);
                    }
                } else {
                    const likeCountSpan = commentContainer.querySelector(".css-1nd5cw-DivLikeContainer span");
                    likeCount = likeCountSpan ? parseInt(likeCountSpan.textContent.replace(/[^0-9]/g, ''), 10) : 0;
                }
                return { username, commentText, timeStamp, likeCount };
            }
        
            async function getAllComments() {
                const commentContainer = document.querySelector(".css-7whb78-DivCommentListContainer");
                if (!commentContainer) {
                    console.error("Comment container not found!");
                    return [];
                }
        
                let allComments = [];
                let lastHeight = commentContainer.scrollHeight;
                let newHeight;
                const maxScrolls = 50;
                let scrollCount = 0;
        
                while (scrollCount < maxScrolls) {
                    await scrollToBottom(commentContainer);
                    newHeight = commentContainer.scrollHeight;
                    if (newHeight === lastHeight) {
                        break;
                    }
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
                return allComments;
            }
        
            return await getAllComments();
            """
            print("Injecting JavaScript to extract comments...")
            comments = await page.evaluate(js_code)
            print("Comments extracted:")
            for comment in comments:
                print(comment)
            await browser.close()
        except Exception as e:
            print("Error while connecting over CDP or injecting JS:", e)

if __name__ == "__main__":
    asyncio.run(main())
