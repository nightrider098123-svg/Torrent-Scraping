# Torrent Scraper for Google Colab & Telegram

This repository provides a powerful torrent scraper designed specifically to run inside **Google Colab** and automatically send the results to you via **Telegram**.

It searches for your desired term (e.g., movies or series), filters the results by release year, and combines the found torrents and Magnet Links into a clean `.txt` file, which is then sent directly to your Telegram bot.

Supported sites:
- **ThePirateBay**
- **1337x**

## Features
- **Cloudflare Bypass:** Uses `cloudscraper` to bypass 1337x's bot protections.
- **Direct API:** Uses Apibay for extremely fast PirateBay results.
- **Year Filtering:** Only returns results that match the year range you specify.
- **Automated Delivery:** Sends the final list of Magnet links directly to your Telegram.

---

## 🚀 How to Use in Google Colab

The easiest way to use this scraper at scale is through Google Colab.

### 1. Setup Telegram Bot
Before you begin, you need a Telegram Bot and your Chat ID:
1. Open Telegram and search for **@BotFather**.
2. Send `/newbot` and follow the prompts to create a bot.
3. Save the **Bot Token** (it looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
4. Search for **@userinfobot** in Telegram and send a message to get your **Chat ID** (a number like `123456789`).
5. Open a chat with your newly created bot and send a message (like "hello") to initiate the conversation.

### 2. Setup Google Colab
1. Go to [Google Colab](https://colab.research.google.com/) and create a **New Notebook**.
2. Copy the entire contents of `colab_scraper.py` into a new code cell, or upload the file to your Colab session.
3. In a **new code cell**, install the required dependencies by running:
   ```bash
   !pip install cloudscraper bs4 lxml requests
   ```

### 3. Run the Scraper
In another code cell, execute the script with your desired parameters.

**Example usage:**
```bash
!python colab_scraper.py \
  --query "batman" \
  --start_year 2020 \
  --end_year 2023 \
  --pages 3 \
  --bot_token "YOUR_TELEGRAM_BOT_TOKEN" \
  --chat_id "YOUR_TELEGRAM_CHAT_ID"
```

*Make sure to replace `"YOUR_TELEGRAM_BOT_TOKEN"` and `"YOUR_TELEGRAM_CHAT_ID"` with the credentials you got in step 1.*

---

## 🛠 Parameters List

| Parameter | Required | Description |
| :--- | :--- | :--- |
| `--query` | **Yes** | The search term you are looking for (e.g., "The Matrix"). Wrap in quotes if it has spaces. |
| `--start_year` | **Yes** | The earliest release year to include (e.g., `1999`). |
| `--end_year` | **Yes** | The latest release year to include (e.g., `2003`). |
| `--pages` | No | The number of pages to scrape on 1337x (Default is `1`). Increase for larger scale scraping. |
| `--bot_token` | **Yes** | Your Telegram Bot Token from @BotFather. |
| `--chat_id` | **Yes** | Your personal Telegram Chat ID. |

---

## Example Output

The bot will send a `.txt` file to your Telegram chat containing data formatted like this:

```
Title: The Matrix (1999) 1080p BluRay x264
Year: 1999
Source: ThePirateBay
Magnet: magnet:?xt=urn:btih:ABC123DEF456...
--------------------------------------------------------------------------------
Title: The Matrix Reloaded (2003) 720p
Year: 2003
Source: 1337x
Magnet: magnet:?xt=urn:btih:DEF456ABC123...
--------------------------------------------------------------------------------
```

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
