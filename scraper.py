import requests
from bs4 import BeautifulSoup

FIREBASE_URL = "https://tuliverse-default-rtdb.firebaseio.com/shows"

SHOWS = {
    "bigg_boss": "https://desiruleztv.net/category/bigg-boss-season-20/",
    "bigg_boss_bangla": "https://desiruleztv.net/category/bigg-boss-bangla/",
    "splitsvilla": "https://desiruleztv.net/category/splitsvilla/",
    "roadies": "https://desiruleztv.net/category/roadies-rebirth/",
    "mtv_hustle": "https://desiruleztv.net/category/mtv-hustle-season-5/",
    "anupama": "https://desiruleztv.net/category/anupama/"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def scrape_show(show_key, category_url):
    try:
        res = requests.get(category_url, headers=headers)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            latest_post = soup.find('a', class_='entry-title-link')
            
            if latest_post:
                post_url = latest_post['href']
                post_res = requests.get(post_url, headers=headers)
                post_soup = BeautifulSoup(post_res.text, 'html.parser')
                
                episodes = {}
                count = 1
                for iframe in post_soup.find_all('iframe'):
                    src = iframe.get('src', '')
                    if any(server in src for server in ['streamwish', 'dood', 'filelions', 'voesx', 'mixdrop']):
                        episodes[f"ep_{count}"] = {
                            "title": f"Episode {count}",
                            "stream_link": src
                        }
                        count += 1
                
                if episodes:
                    requests.patch(f"{FIREBASE_URL}/{show_key}.json", json={"episodes": episodes})
                    print(f"Successfully scraped {show_key}")
    except Exception as e:
        print(f"Error scraping {show_key}: {e}")

for show_key, url in SHOWS.items():
    scrape_show(show_key, url)
