import requests

def search_posts(keyword):

    url=f"https://www.reddit.com/search.json?q={keyword}"

    r=requests.get(url,headers={"User-Agent":"Mozilla/5.0"})

    return r.json()
