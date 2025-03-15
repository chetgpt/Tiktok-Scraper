# CHETGPT: It's a tool to get tiktok comments, the best result so far is 1-10% of the total comments for 1k above and around 50% for below 100 comments. The main problem for me is getting the rest of the comments. TIKTOK BOT COMMENT CONTINUE LATER.py seems promising, but right now i want to focus on extraction rather than insertion, hope you get my intention.

# BY CHATGPT

## 📌 Overview
**Combined1** is an advanced **TikTok comment scraper** that automates extracting comments from TikTok videos. It leverages **Playwright for browser automation**, **Microsoft Edge debugging**, and **JavaScript execution** to efficiently scrape user comments while handling scrolling, loading, and interaction delays.

## 🚀 Features
- **📝 Automated TikTok Comment Extraction**: Retrieves comments, usernames, and timestamps from multiple videos.
- **📡 Playwright CDP Integration**: Uses **Microsoft Edge’s** **Remote Debugging Protocol (CDP)** for seamless scraping.
- **🔄 Auto-Scroll & View More Clicks**: Ensures maximum comment extraction by handling dynamic loading.
- **📂 JSON Storage**: Saves extracted comments in structured JSON files.
- **🎥 Multi-Video Scraping**: Can scrape comments from multiple videos automatically.
- **🖥️ Edge Browser Automation**: Launches and controls **Microsoft Edge** to navigate TikTok.

## 📦 Dependencies
Make sure to install the required Python packages:
```bash
pip install playwright asyncio
```

Also, ensure **Microsoft Edge** is installed on your system.

## 🛠 How to Use
1. **Install Playwright Drivers**:
   ```bash
   playwright install
   ```
2. **Run the script**:
   ```bash
   python Combined1.py
   ```
3. **Watch the script launch Edge** and start scraping TikTok comments.
4. **Scraped comments** will be stored as JSON files (`scraped_comments_video_1.json`, `scraped_comments_video_2.json`, etc.).

## 🔑 Key Functionalities
### 🌐 **Automated Browser Control**
- Launches **Microsoft Edge** in debugging mode.
- Connects Playwright to the running browser instance.
- Navigates TikTok and extracts **usernames, comments, and timestamps**.

### 🔄 **Smart Scrolling & Click Handling**
- Detects and scrolls the comment section to load more comments.
- Clicks **“View more replies”** buttons to reveal nested comments.
- Clicks **next video buttons** to move to a new TikTok video.

### 📂 **Data Storage**
- Saves extracted comments to JSON files for further analysis.
- Structured format:
  ```json
  [
    {
      "username": "user1",
      "commentText": "This is a comment",
      "timeStamp": "2h ago"
    }
  ]
  ```

## 📌 Next Steps
- Expand support for **additional social media platforms**.
- Add **sentiment analysis** to classify comment tone.
- Implement **error handling improvements** for dynamic UI changes.

## 🤝 Contributing
Feel free to submit **issues or pull requests** to improve the functionality.

---
🚀 *Automate TikTok comment extraction with Playwright & Edge!*
