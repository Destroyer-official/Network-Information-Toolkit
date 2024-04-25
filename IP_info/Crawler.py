import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

def get_page(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            print("Failed to retrieve page:", response.status_code)
            return None
    except Exception as e:
        print("Error occurred while retrieving page:", str(e))
        return None

def extract_links(soup, base_url):
    internal_links = set()
    external_links = set()

    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith('http'):
            external_links.add(href)
        else:
            internal_links.add(urljoin(base_url, href))

    return internal_links, external_links

def extract_images(soup, base_url):
    images = set()

    for img in soup.find_all('img', src=True):
        src = img.get('src')
        images.add(urljoin(base_url, src))

    return images

def extract_assets(soup, base_url):
    css_files = set()
    js_files = set()

    for css in soup.find_all('link', {'rel': 'stylesheet'}, href=True):
        css_files.add(urljoin(base_url, css['href']))

    for script in soup.find_all('script', src=True):
        js_files.add(urljoin(base_url, script['src']))

    return css_files, js_files

def extract_meta_tags(soup):
    meta_tags = {}
    
    for meta_tag in soup.find_all('meta'):
        tag_name = meta_tag.get('name', meta_tag.get('property', meta_tag.get('http-equiv', '')))
        tag_content = meta_tag.get('content', '')
        meta_tags[tag_name] = tag_content

    return meta_tags

def extract_headings(soup):
    headings = {}
    
    for i in range(1, 7):
        heading_tags = soup.find_all(f'h{i}')
        if heading_tags:
            headings[f'h{i}'] = [tag.get_text().strip() for tag in heading_tags]
    
    return headings

def save_crawler_info(url, internal_links, external_links, images, css_files, js_files, meta_tags, headings):
    filename = url.replace('http://', '').replace('https://', '').replace('/', '_') + "_Crawler.txt"
    # print(filename)
    with open(filename, 'w') as f:
        f.write(f"URL: {url}\n")
        f.write("Internal Links:\n")
        for link in internal_links:
            f.write(f"\t{link}\n")
        f.write("\nExternal Links:\n")
        for link in external_links:
            f.write(f"\t{link}\n")
        f.write("\nImages:\n")
        for img in images:
            f.write(f"\t{img}\n")
        f.write("\nCSS Files:\n")
        for css in css_files:
            f.write(f"\t{css}\n")
        f.write("\nJavaScript Files:\n")
        for js in js_files:
            f.write(f"\t{js}\n")
        f.write("\nMeta Tags:\n")
        for tag, content in meta_tags.items():
            f.write(f"\t{tag}: {content}\n")
        f.write("\nHeadings:\n")
        for tag, values in headings.items():
            f.write(f"\t{tag}: {values}\n")

def crawler_fetcher(url):
    page_content = get_page(url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        internal_links, external_links = extract_links(soup, url)
        images = extract_images(soup, url)
        css_files, js_files = extract_assets(soup, url)
        meta_tags = extract_meta_tags(soup)
        headings = extract_headings(soup)
        save_crawler_info(url, internal_links, external_links, images, css_files, js_files, meta_tags, headings)
        print(f"Crawler information saved successfully. ")

if __name__ == "__main__":
    url = input("Enter the URL to crawl: ")
    crawler_fetcher(url)
