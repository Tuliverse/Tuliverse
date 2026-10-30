import cloudscraper
from bs4 import BeautifulSoup
import requests

FIREBASE_URL = "https://tuliverse-default-rtdb.firebaseio.com/shows"

SHOWS = {
    "mtv_india": "https://desiruleztv.net/category/mtv-india/",
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
            
            latest_post = soup.find('a', class_='entry-title-link') or soup.find('h2', class_='entry-title')
            
            if latest_post:
                post_url = latest_post['href'] if latest_post.name == 'a' else latest_post.find('a')['href']
                print(f"Fetching post: {post_url}")
                
                post_res = scraper.get(post_url)
                post_soup = BeautifulSoup(post_res.text, 'html.parser')
                
                links = []
                
                for iframe in post_soup.find_all('iframe'):
                    src = iframe.get('src', '')
                    if src and src.startswith('http'):
                        links.append(src)
                
                for a in post_soup.find_all('a', href=True):
                    href = a['href']
                    if any(server in href.lower() for server in ['streamwish', 'dood', 'filelions', 'voesx', 'mixdrop', 'vidsrc', 'embed']):
                        links.append(href)
                
                unique_links = list(dict.fromkeys(links))
                
                episodes = {}
                for idx, link in enumerate(unique_links, start=1):
                    episodes[f"ep_{idx}"] = {
                        "title": f"Episode Link {idx}",
                        "stream_link": link
                    }
                
                if episodes:
                    patch_res = scraper.patch(f"{FIREBASE_URL}/{show_key}.json", json={"episodes": episodes})
                    print(f"Successfully updated {show_key}: Status {patch_res.status_code}")
                else:
                    print(f"No video links found for {show_key}")
            else:
                print(f"No posts found for category {show_key}")
        else:
            print(f"Failed to access {category_url}: Status {res.status_code}")
            
    except Exception as e:
        print(f"Error scraping {show_key}: {e}")

for show_key, url in SHOWS.items():
    scrape_show(show_key, url)
