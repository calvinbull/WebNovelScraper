#!/usr/bin/env python
import requests
import os
from bs4 import BeautifulSoup

# URL = "https://free-webnovel.com/freewebnovel/super-gene/chapter-1"
URL = input("Input URL to first desired chapter: ").strip()

# Dictionary of HTTP headers
headers = {'User-Agent': 'helloworld'}

# Initialize nextchapter for loop
nextchapter = "temp"


while(nextchapter != ""):
    # Pull page
    response = requests.get(URL, headers=headers)
    # Raise exception if unsuccessful
    response.raise_for_status()

    # Turn text response into soup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parse chapter soup
    nextchapter = soup.find("a", {"id": "next_chap"}).get("href")
    titlename = soup.find("a", {"class": "novel-title"}).string.strip()
    chaptername = soup.find("a", {"class": "chr-title"}).string.strip()
    chaptertext = soup.find("div", attrs={"id": "chr-content"}).get_text("\n\n",True)

    # Create folder for chapters if needed
    folder = os.path.join(os.getenv('HOME'), 'WebNovelScraper', titlename)
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Write new chapter
    with open(f"{folder}/{titlename}_{chaptername}.txt", "w") as file:
        file.write(f"{titlename}\n")
        file.write(f"{chaptername}\n")
        file.write(chaptertext)

    URL = nextchapter
    