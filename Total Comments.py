        # Extract total number of comments (C)
        C = await page.evaluate("""
        () => {
            const commentElements = Array.from(document.querySelectorAll('*'))
                .filter(el => /comments/i.test(el.textContent));
            if (commentElements.length > 0) {
                const text = commentElements[0].textContent;
                const match = text.match(/(\d+(?:\.\d+)?[KMB]?)\s*comments/i);
                if (match) {
                    let val = parseFloat(match[1]);
                    const suffix = match[1].match(/[KMB]/i);
                    if (suffix) {
                        switch (suffix[0].toUpperCase()) {
                            case 'K': val *= 1000; break;
                            case 'M': val *= 1000000; break;
                            case 'B': val *= 1000000000; break;
                        }
                    }
                    return Math.round(val);
                }
            }
            return 0;
        }
        """)
        print(f"Total comments on the video: {C}")

        # Calculate target number of comments to scrape (N)
        S = 1  # Scaling factor, adjustable if needed
        if C < 1000:
            temp = max(100, 0.1 * C)
        else:
            temp = max(300, 0.05 * C)
        N = min(2000, temp) * S
        if N > C:
            N = C
        print(f"Target number of comments to collect: {N}")
