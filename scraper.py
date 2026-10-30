import cloudscraper
from bs4 import BeautifulSoup
import requests
import re

FIREBASE_URL = "https://tuliverse-default-rtdb.firebaseio.com/shows"

# আপনার দেওয়া ক্যাটাগরি লিংকসমূহ
SHOWS = {
    "star_plus": "https://desiruleztv.net/category/star-plus/",
    "colors_tv": "https://desiruleztv.net/category/colors-tv/",
    "zee_tv": "https://desiruleztv.net/category/zeetv/",
    "sony_tv": "https://desiruleztv.net/category/sony-tv/",
    "mtv_india": "https://desiruleztv.net/category/mtv-india/",
    "netflix": "https://desiruleztv.net/category/netflix/",
    "prime_video": "https://desiruleztv.net/category/prime-video/",
    "bigg_boss": "https://desiruleztv.net/category/bigg-boss-season-20/",
    "splitsvilla": "https://desiruleztv.net/category/splitsvilla/",
    "roadies": "https://desiruleztv.net/category/mtv-roadies/",
    "mtv_hustle": "https://desiruleztv.net/category/mtv-hustle/",
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
            
            # ক্যাটাগরি পেজের সব পোস্ট লিংক বের করা
            posts = soup.find_all('article')
            post_urls = []
            
            for post in posts:
                a_tag = post.find('a', href=True)
                if a_tag and a_tag['href'] not in post_urls:
                    post_urls.append(a_tag['href'])

            # নির্দিষ্ট পোস্ট না পেলে লিংকের সাধারণ ফিল্টারিং
            if not post_urls:
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if 'watch-video-episode-online' in href or 'episode' in href:
                        post_urls.append(href)

            if post_urls:
                # সর্বশেষ ২-৩টি পোস্ট থেকে ভিডিও স্ক্র্যাপ করা
                links = []
                for post_url in post_urls[:3]:
                    print(f"Scraping post for {show_key}: {post_url}")
                    post_res = scraper.get(post_url)
                    post_soup = BeautifulSoup(post_res.text, 'html.parser')
                    
                    # ১. হোস্টিং সার্ভারের ডায়নামিক এম্বেড লিংক ফিল্টার করা
                    for a in post_soup.find_all('a', href=True):
                        href = a['href']
                        if any(server in href.lower() for server in ['streamwish', 'dood', 'filelions', 'voesx', 'mixdrop', 'vidsrc', 'dailymotion', 'vk.com', 'mbed']):
                            if 'wp-embed' not in href and 'desirulez' not in href:
                                links.append(href)

                    # ২. iframe লিংক ফিল্টার করা (WordPress script বাদ দিয়ে)
                    for iframe in post_soup.find_all('iframe'):
                        src = iframe.get('src') or iframe.get('data-src', '')
                        if src and src.startswith('http') and 'wp-embed' not in src and 'wp-includes' not in src:
                            links.append(src)

                unique_links = list(dict.fromkeys(links))
                
                # যদি কোনো সার্ভার লিংক না পাওয়া যায়, তবে ব্যাকআপ হিসেবে পোস্ট ইউআরএল রাখা
                if not unique_links and post_urls:
                    unique_links = [post_urls[0]]

                episodes = {}
                for idx, link in enumerate(unique_links, start=1):
                    episodes[f"ep_{idx}"] = {
                        "title": f"Episode Link {idx}",
                        "stream_link": link
                    }

                patch_res = requests.patch(f"{FIREBASE_URL}/{show_key}.json", json={"episodes": episodes})
                print(f"Updated {show_key} successfully: Status {patch_res.status_code}")
            else:
                print(f"No posts found for {show_key}")
                
    except Exception as e:
        print(f"Error scraping {show_key}: {e}")

for show_key, url in SHOWS.items():
    scrape_show(show_key, url)
