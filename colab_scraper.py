"""
Google Colab Torrent Scraper
-----------------------------
This script is designed to run inside Google Colab and push results to Telegram.

Setup Instructions for Google Colab:
1. Open a new Google Colab notebook (https://colab.research.google.com/)
2. Create a new Code cell and install the required dependencies:
   !pip install cloudscraper bs4 lxml requests

3. Upload this file `colab_scraper.py` to the Colab environment OR copy-paste the entire code into a cell.
   If uploading, create another Code cell and run the script like so:

   !python colab_scraper.py --query "batman" --start_year 2020 --end_year 2023 --pages 3 --bot_token "YOUR_TELEGRAM_BOT_TOKEN" --chat_id "YOUR_TELEGRAM_CHAT_ID"

Make sure to replace YOUR_TELEGRAM_BOT_TOKEN and YOUR_TELEGRAM_CHAT_ID with your actual credentials.
"""

import argparse
import requests
from bs4 import BeautifulSoup
import cloudscraper
import urllib.parse
import re
import datetime
import os
import time

def send_to_telegram(bot_token, chat_id, file_path):
    print(f"Sending {file_path} to Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    with open(file_path, 'rb') as f:
        response = requests.post(url, data={'chat_id': chat_id}, files={'document': f})
    if response.status_code == 200:
        print("Successfully sent to Telegram!")
    else:
        print(f"Failed to send to Telegram. Status: {response.status_code}, Response: {response.text}")

def get_tpb_trackers():
    trackers = [
        "udp://tracker.coppersurfer.tk:6969/announce",
        "udp://9.rarbg.to:2920/announce",
        "udp://tracker.opentrackr.org:1337",
        "udp://tracker.internetwarriors.net:1337/announce",
        "udp://tracker.leechers-paradise.org:6969/announce",
        "udp://tracker.pirateparty.gr:6969/announce",
        "udp://tracker.cyberia.is:6969/announce"
    ]
    return "".join(["&tr=" + urllib.parse.quote(t) for t in trackers])

def extract_quality(name):
    quality_match = re.search(r'(1080p|720p|480p|360p|2160p|4K|1080|720)', name, re.IGNORECASE)
    return quality_match.group(1).lower() if quality_match else "Unknown"

def fetch_tpb_api(q):
    url = f"https://apibay.org/q.php?q={urllib.parse.quote(str(q))}&cat=100,200,300,400,600"
    try:
        response = requests.get(url)
        data = response.json()
        if not data or data[0].get("name") == "No results returned":
            return []
        return data
    except Exception as e:
        print(f"Error fetching TPB: {e}")
        return []

def process_tpb_results(data, start_year, end_year):
    results = []
    for item in data:
        name = item.get("name", "")
        year_match = re.search(r'[\(\.\[\s](\d{4})[\)\.\]\s]', name)
        added = int(item.get("added", 0))
        item_year = None

        if year_match:
            item_year = int(year_match.group(1))
        elif added > 0:
            item_year = datetime.datetime.fromtimestamp(added).year

        if item_year is None or not (start_year <= item_year <= end_year):
            continue

        info_hash = item.get("info_hash")
        magnet = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(name)}{get_tpb_trackers()}"
        quality = extract_quality(name)

        results.append({
            "title": name,
            "magnet": magnet,
            "year": item_year,
            "quality": quality,
            "source": "ThePirateBay"
        })
    return results

def scrape_tpb(query, start_year, end_year, max_pages=1):
    results = []
    if query:
        print(f"Scraping ThePirateBay for '{query}'...")
        data = fetch_tpb_api(query)
        results.extend(process_tpb_results(data, start_year, end_year))
    else:
        print(f"No query provided. Scraping ThePirateBay for years {start_year} to {end_year}...")
        for y in range(start_year, end_year + 1):
            print(f"Fetching top results for year {y}...")
            data = fetch_tpb_api(str(y))
            results.extend(process_tpb_results(data, start_year, end_year))
            time.sleep(0.5)

    # Remove duplicates
    unique_results = {r['magnet']: r for r in results}.values()
    final_results = list(unique_results)
    print(f"Found {len(final_results)} valid results on ThePirateBay.")
    return final_results

def scrape_1337x(query, start_year, end_year, max_pages=1):
    scraper = cloudscraper.create_scraper()
    base_url = "https://1337xx.to"
    results = []

    # Determine the URLs to scrape
    url_patterns = []
    if query:
        print(f"Scraping 1337x for '{query}' up to {max_pages} pages...")
        url_patterns.append(f"{base_url}/search/{urllib.parse.quote(query)}/{{}}/")
    else:
        print(f"No query provided. Scraping 1337x Movies and TV categories up to {max_pages} pages...")
        url_patterns.append(f"{base_url}/cat/Movies/{{}}/")
        url_patterns.append(f"{base_url}/cat/TV/{{}}/")

    for pattern in url_patterns:
        for page in range(1, max_pages + 1):
            url = pattern.format(page)
            print(f"Fetching 1337x URL: {url}")
            try:
                response = scraper.get(url)
                if response.status_code != 200:
                    print(f"Failed to fetch {url}. Status: {response.status_code}")
                    break
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                break

            soup = BeautifulSoup(response.text, "lxml")
            rows = soup.select("tbody > tr")
            if not rows:
                print(f"No more results found at {url}.")
                break

            for tr in rows:
                a_tags = tr.select("td.coll-1 > a")
                if len(a_tags) < 2:
                    continue
                a = a_tags[1]
                name = a.text
                link = f"{base_url}{a['href']}"

                year_match = re.search(r'[\(\.\[\s](\d{4})[\)\.\]\s]', name)
                item_year = None
                if year_match:
                    item_year = int(year_match.group(1))
                else:
                    date_str = tr.select("td.coll-date")[0].text.strip()
                    date_str = re.sub(r'(st|nd|rd|th)', '', date_str)
                    try:
                        dt = datetime.datetime.strptime(date_str, "%b. %d '%y")
                        item_year = dt.year
                    except:
                        pass

                # If year isn't explicitly found in title or upload date, and we are just pulling ALL categories,
                # we might lose some items, but we only want items within start_year and end_year.
                if item_year is None or not (start_year <= item_year <= end_year):
                    continue

                quality = extract_quality(name)

                try:
                    res = scraper.get(link)
                    magnet_soup = BeautifulSoup(res.text, "lxml")
                    magnet_link = magnet_soup.select('ul.dropdown-menu > li > a')
                    if not magnet_link:
                        magnet_link = magnet_soup.select('a[href^="magnet:"]')

                    magnet = ""
                    for m in magnet_link:
                        if m.get('href', '').startswith('magnet:'):
                            magnet = m['href']
                            break

                    if magnet:
                        results.append({
                            "title": name,
                            "magnet": magnet,
                            "year": item_year,
                            "quality": quality,
                            "source": "1337x"
                        })
                except Exception as e:
                    print(f"Failed to extract magnet for {name}: {e}")
            time.sleep(1)

    print(f"Found {len(results)} valid results on 1337x.")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Torrents and Send to Telegram via Google Colab")
    parser.add_argument('--query', type=str, default='', help="Search query (e.g. 'Batman'). Leave empty to scrape categories.")
    parser.add_argument('--start_year', type=int, required=True, help="Start year for filtering (e.g. 2010)")
    parser.add_argument('--end_year', type=int, required=True, help="End year for filtering (e.g. 2020)")
    parser.add_argument('--pages', type=int, default=1, help="Number of pages to scrape on 1337x")
    parser.add_argument('--bot_token', type=str, required=True, help="Telegram Bot Token")
    parser.add_argument('--chat_id', type=str, required=True, help="Telegram Chat ID")

    args = parser.parse_args()

    print(f"Starting scrape for '{args.query}' from {args.start_year} to {args.end_year}...")

    tpb_results = scrape_tpb(args.query, args.start_year, args.end_year, args.pages)
    x1337_results = scrape_1337x(args.query, args.start_year, args.end_year, args.pages)

    all_results = tpb_results + x1337_results

    if not all_results:
        print("No results found matching your criteria.")
        exit(0)

    filename = f"torrents_{args.query.replace(' ', '_')}_{args.start_year}_{args.end_year}.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        for res in all_results:
            f.write(f"Title: {res['title']}\n")
            f.write(f"Quality: {res['quality']}\n")
            f.write(f"Year: {res['year']}\n")
            f.write(f"Source: {res['source']}\n")
            f.write(f"Magnet: {res['magnet']}\n")
            f.write("-" * 80 + "\n")

    print(f"Saved {len(all_results)} results to {filename}")
    send_to_telegram(args.bot_token, args.chat_id, filename)
