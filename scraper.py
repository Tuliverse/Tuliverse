import cloudscraper
from bs4 import BeautifulSoup
import requests
import re

FIREBASE_URL = "https://tuliverse-default-rtdb.firebaseio.com/shows"

SHOWS = {
    "bigg_boss": "https://desiruleztv.net/category/bigg-boss-season-20/",
    "bigg_boss_bangla": "https://desiruleztv.net/category/bigg-boss-bangla/",
    "splitsvilla": "https://desiruleztv.net/category/splitsvilla/",
    "roadies": "https://desiruleztv.net/category/roadies-rebirth/",
    "mtv_hustle": "https://desiruleztv.net/category/mtv-hustle-season-5/",
    "anupama": "https://desiruleztv.net/category/anupama/"
}

scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
)

def scrape_show(show_key, category_url):
    try:
        res = scraper.get(category_url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            posts = soup.find_all('article')
            post_url = None
            if posts:
                a_tag = posts[0].find('a', href=True)
                if a_tag:
                    post_url = a_tag['href']

            if post_url:
                print(f"Scraping post for {show_key}: {post_url}")
                post_res = scraper.get(post_url)
                post_soup = BeautifulSoup(post_res.text, 'html.parser')
                
                links = []
                
                # 1. Look for valid video player links inside 'a' tags
                for a in post_soup.find_all('a', href=True):
                    href = a['href']
                    if any(server in href.lower() for server in ['streamwish', 'dood', 'filelions', 'voesx', 'mixdrop', 'vidsrc', 'dailymotion', 'vk.com', 'mbed']):
                        if 'wp-embed' not in href and 'desirulez' not in href:
                            links.append(href)

                # 2. Extract embedded iframe sources directly
                for iframe in post_soup.find_all('iframe'):
                    src = iframe.get('src') or iframe.get('data-src', '')
                    if src and src.startswith('http') and 'wp-embed' not in src and 'wp-includes' not in src:
                        links.append(src)

                # Fallback: if no stream hosts matched, use the direct post page link
                if not links:
                    links.append(post_url)

                unique_links = list(dict.fromkeys(links))
                
                episodes = {}
                for idx, link in enumerate(unique_links, start=1):
                    episodes[f"ep_{idx}"] = {
                        "title": f"Episode Link {idx}",
                        "stream_link": link
                    }

                patch_res = requests.patch(f"{FIREBASE_URL}/{show_key}.json", json={"episodes": episodes})
                print(f"Updated {show_key} successfully: {patch_res.status_code}")
                
    except Exception as e:
        print(f"Error scraping {show_key}: {e}")

for show_key, url in SHOWS.items():
    scrape_show(show_key, url)
