import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import json
import os

def extract_blog_urls_from_sitemap(sitemap_url):
    response = requests.get(sitemap_url)
    # parse the XML content
    root = ET.fromstring(response.content)
    namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                 'xhtml': 'http://www.w3.org/1999/xhtml'}
    
    urls = []

    for url in root.findall('sitemap:url', namespace):
        loc = url.find('sitemap:loc', namespace).text.strip()  # Use strip() to clean the URL
        if '/insight/' in loc:  # Filter to include only blog post URLs
            urls.append(loc)
    
    return urls

def save_blog_post_as_json(url, filepath):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract the title from the h1 tag
    title = soup.find('h1').text.strip()

    # Extract the author from the alt attribute of the img tag inside the author container
    author_container = soup.find('div', class_='container is-author')
    if author_container:
        author_img = author_container.find('img')
        author = author_img['alt'].strip() if author_img else "Unknown"
    else:
        author = "Unknown"

    # Extract the content from divs with ids starting with 'article'
    text = ""
    for i in range(1, 10):  # Assuming ids like 'article1', 'article2', ..., 'article9'
        article_div = soup.find('div', id=f'article{i}')
        if article_div:
            text += article_div.get_text(separator="\n", strip=True)

    # Create the JSON object
    blog_post = {
        "title": title,
        "author": author,
        "text": text
    }

    # Save the JSON object to a file
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(blog_post, json_file, ensure_ascii=False, indent=4)

# URL of the sitemap
sitemap_url = 'https://www.osedea.com/sitemap.xml'

# Extract blog post URLs
blog_urls = extract_blog_urls_from_sitemap(sitemap_url)

# Create data directory if it doesn't exist
os.makedirs('../data', exist_ok=True)

for index, url in enumerate(blog_urls):
    filename = f"../data/blog_post_{index+1}.json"  # Save JSON in /data directory
    save_blog_post_as_json(url, filename)
