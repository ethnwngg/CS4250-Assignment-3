import urllib.request
from bs4 import BeautifulSoup
import pymongo
from urllib.parse import urljoin

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['CPP']
collection = db['pages']

def storePage(url, html):
    if not collection.find_one({"url": url}):
        collection.insert_one({"url": url, "html": html})

def targetPage(html):
    soup = BeautifulSoup(html, 'html.parser')
    h1_tag = soup.find('h1', class_="cpp-h1")
    return h1_tag and 'Permanent Faculty' in h1_tag.text

def retrieveHTML(url):
    try:
        response = urllib.request.urlopen(url)
        if response.info().get_content_type() in ['text/html', 'application/xhtml+xml']:
            return response.read()
    except Exception as e:
        print(f"Not able to retrieve {url}: {e}")
        return None
    return None

def parse(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = set()
    for link in soup.find_all('a', href=True):
        full_url = urljoin(base_url, link['href'])
        if full_url.startswith(base_url):
            urls.add(full_url)
    return urls

def crawlerThread(frontier):
    visited = set()

    while frontier:
        url = frontier.pop(0)
        if url in visited:
            continue
    
    visited.add(url)
    html = retrieveHTML(url)
    if html:
        storePage (url, html)
        if targetPage(html):
            print(f"Page found: {url}")
            
        for new_url in parse(html, url):
            if new_url not in visited:
                frontier.append(new_url)

if __name__ == "__main__":
    starting_url = "https://www.cpp.edu/sci/computer-science/"
    frontier = [starting_url]
    crawlerThread(frontier)
    print("Process completed.")


