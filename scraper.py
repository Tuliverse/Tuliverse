import cloudscraper
from bs4 import BeautifulSoup
import requests
import json
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
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

def scrape_show(show_key, category_url):
    try:
        res = scraper.get(category_url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Find latest episode post
            latest_post = soup.find('a', href=re.compile(r'https://desiruleztv\.net/.*'))
            
            # Find entry link
            posts = soup.find_all('article')
            post_url = None
            if posts:
                a_tag = posts[0].find('a', href=True)
                if a_tag:
                    post_url = a_tag['href']
            
            if not post_url and latest_post:
                post_url = latest_post['href']

            if post_url:
                print(f"Fetching post for {show_key}: {post_url}")
                post_res = scraper.get(post_url)
                post_soup = BeautifulSoup(post_res.text, 'html.parser')
                
                links = []
                
                # Extract iframe sources
                for iframe in post_soup.find_all('iframe'):
                    src = iframe.get('src') or iframe.get('data-src', '')
                    if src and src.startswith('http'):
                        links.append(src)
                
                # Extract regex match links inside post content
                content_text = str(post_soup)
                found_urls = re.findall(r'https?://[^\s\'"]+', content_text)
                for url in found_urls:
                    if any(server in url.lower() for server in ['streamwish', 'dood', 'filelions', 'voesx', 'mixdrop', 'vidsrc', 'embed', 'dailymotion']):
                        links.append(url)

                unique_links = list(dict.fromkeys(links))
                
                episodes = {}
                for idx, link in enumerate(unique_links, start=1):
                    episodes[f"ep_{idx}"] = {
                        "title": f"Episode Link {idx}",
                        "stream_link": link
                    }
                
                # Fallback if no specific player link found
                if not episodes:
                    episodes["ep_1"] = {
                        "title": "Watch Full Episode",
                        "stream_link": post_url
                    }

                patch_res = requests.patch(f"{FIREBASE_URL}/{show_key}.json", json={"episodes": episodes})
                print(f"Updated {show_key} -> Status Code: {patch_res.status_code}")
            else:
                print(f"No post found for {show_key}")
        else:
            print(f"Failed category fetch for {show_key}: {res.status_code}")

    except Exception as e:
        print(f"Error scraping {show_key}: {e}")

for show_key, url in SHOWS.items():
    scrape_show(show_key, url)
