import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
}

def extract_image(url):
    """
    Extract image URL from Facebook post.
    
    Note: Facebook requires login for most content. 
    For public pages, try using mbasic.facebook.com or m.facebook.com URLs.
    """
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        
        soup = BeautifulSoup(r.text, "html.parser")
        
        # Try og:image first
        tag = soup.find("meta", property="og:image")
        if tag and tag.get("content"):
            return tag["content"]
        
        # Try meta property="og:image:secure_url"
        tag = soup.find("meta", property="og:image:secure_url")
        if tag and tag.get("content"):
            return tag["content"]
        
        # Try finding image tags directly
        img = soup.find("img", class_=lambda x: x and "scaled" in x.lower())
        if img and img.get("src"):
            return img["src"]
        
        print(f"Warning: Could not extract image from {url}")
        return None
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
