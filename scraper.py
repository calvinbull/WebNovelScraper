#!/usr/bin/env python

import requests
from os import path, makedirs, getenv, cpu_count
from bs4 import BeautifulSoup
from multiprocessing import Pool, Queue


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


# Pull chapter names/links from soup
class chapter():
    def __init__(self, name, URL, num):
        self.name = name
        self.URL = URL
        self.num = num


# Fill queue with chapter objects
q = Queue()
global q

counter = 1
for a in soup.find_all("a", href=True):
    chapt = chapter(a.span.contents[0], a['href'], counter)
    counter += 1
    q.put(chapt)
    

# Function to write chapter files using info from queue
def chapter_writer(chapt):
    # Pull chapter page; exception if unsuccessful
    response = requests.get(chapt.URL, headers=headers)
    response.raise_for_status()

    # Turn text response into soup
    soup = BeautifulSoup(response.text, 'html5lib')

    # Parse chapter soup, write to file
    chaptertext = soup.find("div", attrs={"id": "chr-content"}).get_text("\n\n",True)
       
    with open(f"{folder}/{titlename} - {chapt.name}.txt", "w") as file:
        file.write(f"{titlename}\n{chapt.name}\n{chaptertext}")
    
    print(f"{chapt.name} - Complete")


# TODO: multiprocessing https://docs.python.org/3/library/multiprocessing.html

if __name__ == '__main__':
    # start worker processes
    with Pool(processes=cpu_count()) as pool:
        pool.apply_async(chapter_writer(),(q,))
        # while not q.empty():
            # chapter_writer(q.get())       