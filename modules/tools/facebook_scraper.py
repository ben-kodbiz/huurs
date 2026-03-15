import requests
from bs4 import BeautifulSoup

def extract_image(url):

    headers = {"User-Agent":"Mozilla/5.0"}

    r = requests.get(url,headers=headers)

    soup = BeautifulSoup(r.text,"html.parser")

    tag = soup.find("meta",property="og:image")

    if tag:
        return tag["content"]
