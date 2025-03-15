        # JavaScript code to scrape comments from the page
        scrape_js = r"""
        (async () => {
            const delay = (ms) => new Promise(res => setTimeout(res, ms));

            // Find the comment container
            function getCommentContainer() {
                const selectors = [
                    ".css-7whb78-DivCommentListContainer",
                    ".css-1qp5gj2-DivCommentListContainer",
                    ".css-13wx63w-DivCommentObjectWrapper"
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return el;
                }
                return null;
            }

            // Scroll the comment container to load more comments
            async function scrollCommentContainer(container) {
                if (!container) return;
                let previousHeight = 0;
                for (let i = 0; i < 10; i++) {
                    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' });
                    await delay(3000 + Math.random() * 2000);
                    let currentHeight = container.scrollHeight;
                    if (currentHeight === previousHeight) break;
                    previousHeight = currentHeight;
                }
            }

            // Click "View more" buttons to expand replies
            async function clickViewMoreButtons(container) {
                if (!container) return;
                const viewMoreButtons = container.querySelectorAll('p, span, button, div');
                for (let btn of viewMoreButtons) {
                    let text = (btn.textContent || "").trim();
                    if (/(View|See|Load)\s+(more|all|\d+)\s+(replies|comments)/i.test(text)) {
                        btn.click();
                        await delay(2000 + Math.random() * 1000);
                    }
                }
            }

            // Extract all visible comments
            async function extractItems() {
                const container = getCommentContainer();
                if (!container) return [];

                const wrappers = container.querySelectorAll(".css-1gstnae-DivCommentItemWrapper");
                let items = [];
                for (let w of wrappers) {
                    const userEl = w.querySelector(".css-13x3qpp-DivUsernameContentWrapper a[href^='/@']");
                    const commentEl = w.querySelector("[data-e2e^='comment-level-']");
                    const timeEl = w.querySelector("[data-e2e^='comment-time-']");

                    const username = userEl ? userEl.textContent.trim() : null;
                    const commentText = commentEl ? commentEl.textContent.trim() : null;
                    const timeStamp = timeEl ? timeEl.textContent.trim() : null;

                    if (username && commentText) {
                        items.push({ username, commentText, timeStamp });
                    }
                }
                return items;
            }

            // Main scraping logic
            const container = getCommentContainer();
            if (container) {
                let previousCount = 0;
                let stableCount = 0;
                for (let attempt = 0; attempt < 20; attempt++) {
                    await scrollCommentContainer(container);
                    await clickViewMoreButtons(container);
                    const currentItems = await extractItems();
                    const currentCount = currentItems.length;
                    if (currentCount > previousCount) {
                        previousCount = currentCount;
                        stableCount = 0;
                    } else {
                        stableCount++;
                        if (stableCount >= 3) break;
                    }
                    await delay(5000 + Math.random() * 3000);
                }
            }
            const finalItems = await extractItems();
            return finalItems;
        })();
        """
