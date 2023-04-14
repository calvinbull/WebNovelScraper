#!/usr/bin/env python

import requests
from os import path, makedirs, getenv, cpu_count
from bs4 import BeautifulSoup
from multiprocessing import Pool, Queue
from time import time, sleep


# Chapt class
class chapter():
    def __init__(self, name, URL):
        self.name = name
        self.URL = URL

# Function to write chapter files using info from queue
def chapter_writer(chapt):
    try:
        print(f"Processing chapter {chapt[0]}")
        
        # Pull chapter page; exception if unsuccessful
        retries = 0
        while True:
            try:
                response = requests.get(chapt[1], headers=headers, timeout=3)
                break
            except Exception:
                retries += 1
                wait = retries * 2
                print(f"Request for chapter {chapt[0]} unsucessful. Waiting {wait} secs and re-trying...")
                sleep(wait)
                continue

        response.raise_for_status()
        
        # Turn text response into soup
        soup = BeautifulSoup(response.text, 'html5lib')

        # Parse chapter soup, write to file
        chaptertext = soup.find("div", attrs={"id": "chr-content"}).get_text("\n\n",True)
        
        with open(f"{folder}/{titlename} - {chapt[0]}.txt", "w") as file:
            file.write(f"{titlename}\n\n{chaptertext}")
        
        print(f"{chapt[0]} - Complete")

    except Exception as e:
        print(f"Error processing chapter {chapt[0]}: {str(e)}")


if __name__ == '__main__':

    URL = "https://free-webnovel.com/freewebnovel/super-gene/"
    # URL = input("Input exact URL to novel page (e.g. https://free-webnovel.com/freewebnovel/novel-name/): ").strip()

    # Dictionary of HTTP headers
    headers = {'User-Agent': 'helloworld'}
    # Pull initial page
    response = requests.get(URL, headers=headers)
    # Raise exception if unsuccessful
    response.raise_for_status()

    # Turn text response into soup
    soup = BeautifulSoup(response.text, "html5lib")
    # Parse soup
    titlename = soup.find("meta", {"property": "og:novel:novel_name"}).get("content")
    short_title = titlename.lower().replace(' ','-')
    imglink = soup.find("meta", {"property": "og:image"}).get("content")
    all_chapters = f"https://free-webnovel.com/ajax/chapter-archive?novelId={short_title}"

    # Prepare folder
    folder = path.join(getenv('HOME'), 'WebNovelScraper', titlename)
    if not path.exists(folder):
        makedirs(folder)

    # Pull all chapters page
    response = requests.get(all_chapters, headers=headers)
    # Raise exception if unsuccessful
    response.raise_for_status()

    # Create new soup for chapter list
    soup = BeautifulSoup(response.text, "html5lib")

    # Fill list with chapter URLs
    q = []
    counter = 1
    for a in soup.find_all("a", href=True):
        # chapt = chapter(a.span.contents[0], a['href'])
        q.append((str(counter), a['href']))
        counter += 1
        
    # start worker processes
    with Pool() as pool:
        t0 = time()    
        pool.map(chapter_writer, q)
        t1 = time()
        print(f"time taken: {t1-t0}s")

    # TODO: convert output into EPUB format