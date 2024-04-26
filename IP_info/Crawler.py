import asyncio
import json
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ANSI color codes for colored output
RED = '\033[31m'
CYAN = '\033[36m'
WHITE = '\033[0m'
YELLOW = '\033[33m'
GREEN = '\033[32m'

# User-Agent header for requests
USER_AGENT = {'User-Agent': 'Destroyer'}

def fetch_page_content(url):
    """Fetches the content of a web page.

    Args:
        url (str): The URL of the web page to fetch.

    Returns:
        bytes: The content of the web page.
    """
    try:
        response = requests.get(url, verify=True)
        if response.status_code == 200:
            return response.content
        else:
            print(f"{RED}Failed to retrieve page: {response.status_code}{WHITE}")
            return None
    except Exception as e:
        print(f"{RED}Error occurred while retrieving page: {str(e)}{WHITE}")
        return None

async def js_crawl(js_urls):
    """Crawls external JavaScript files and extracts potential links.

    Args:
        js_urls (list): List of JavaScript file URLs to crawl.

    Returns:
        set: Set of URLs found inside JavaScript files.
    """
    js_crawl_total = set()

    async def fetch(js_url):
        try:
            response = requests.get(js_url, headers=USER_AGENT, verify=True, timeout=10)
            if response.status_code == 200:
                js_data = response.content.decode()
                matches = re.findall(r'(?:http[s]?://|\/)[\w\-\._~:\/?#[\]@!$&\'()*+,;=]+', js_data)
                for match in matches:
                    if not match.startswith('http'):
                        match = urljoin(js_url, match)
                    js_crawl_total.add(match)
        except Exception as exc:
            print(f"{RED}Error fetching JavaScript: {exc}{WHITE}")

    tasks = [fetch(js_url) for js_url in js_urls]
    await asyncio.gather(*tasks)

    return js_crawl_total

async def crawl(target_url):
    """Crawls a target URL and extracts various information from the web page.

    Args:
        target_url (str): The URL of the web page to crawl.

    Returns:
        dict: A dictionary containing various information extracted from the web page.
    """
    print(f"{YELLOW}[!] Crawling {CYAN}{target_url}{WHITE}")
    data = {}

    # Fetch page content
    page_content = fetch_page_content(target_url)
    if not page_content:
        print(f"{RED}Failed to fetch page content for {CYAN}{target_url}{WHITE}")
        return data

    # Parse HTML
    soup = BeautifulSoup(page_content, 'html.parser')

    # Extract basic information
    basic_info = {}
    basic_info['url'] = target_url
    basic_info['title'] = soup.title.string if soup.title else None
    basic_info['meta_tags'] = extract_meta_tags(soup)
    basic_info['headings'] = extract_headings(soup)
    data['basic_info'] = basic_info

    # Extract advanced information
    advanced_info = extract_advanced_info(soup)
    data['advanced_info'] = advanced_info

    # Extract links, CSS, JavaScript, and images
    css_files, js_files, internal_links, external_links, images = extract_css_js_internal_external_images(soup, target_url)
    data['css_files'] = list(css_files)
    data['js_files'] = list(js_files)
    data['internal_links'] = list(internal_links)
    data['external_links'] = list(external_links)
    data['images'] = list(images)

    # Extract links from JavaScript files
    js_urls = list(js_files)
    js_links = await js_crawl(js_urls)
    data['js_links'] = list(js_links)

    # Check Wayback Machine availability
    wayback_avail = await check_wayback_availability(target_url)

    data['wayback_available'] = (wayback_avail)

    return data

def extract_meta_tags(soup):
    """Extracts meta tags from a web page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML of the web page.

    Returns:
        dict: A dictionary containing meta tags extracted from the web page.
    """
    meta_tags = {}

    for meta_tag in soup.find_all('meta'):
        tag_name = meta_tag.get('name', meta_tag.get('property', meta_tag.get('http-equiv', '')))
        tag_content = meta_tag.get('content', '')
        meta_tags[tag_name] = tag_content

    return meta_tags

def extract_headings(soup):
    """Extracts headings (h1 to h6) from a web page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML of the web page.

    Returns:
        dict: A dictionary containing headings extracted from the web page.
    """
    headings = {}

    for i in range(1, 7):
        heading_tags = soup.find_all(f'h{i}')
        if heading_tags:
            headings[f'h{i}'] = [tag.get_text().strip() for tag in heading_tags]

    return headings

def extract_advanced_info(soup):
    """Extracts advanced information such as phone numbers, email addresses, and data attributes from a web page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML of the web page.

    Returns:
        dict: A dictionary containing advanced information extracted from the web page.
    """
    advanced_info = {}

    # Extract phone numbers
    phone_numbers = set()
    for text in soup.find_all(string=True, recursive=True):
        phone_numbers.update(re.findall(r"\d{3}-\d{3}-\d{4}", text))  # Find ###-###-#### format
        phone_numbers.update(re.findall(r"\(\d{3}\) \d{3}-\d{4}", text))  # Find (###) ###-#### format

    # Extract email addresses
    email_addresses = set()
    for text in soup.find_all(string=True, recursive=True):
        email_addresses.update(re.findall(r"[\w\.-]+@[\w\.-]+\.[\w]{2,4}", text))

    advanced_info["phone_numbers"] = list(phone_numbers)
    advanced_info["email_addresses"] = list(email_addresses)

    # Extract data attributes
    data_attributes = {}
    for attr, value in soup.attrs.items():
        if attr.startswith('data-'):
            data_attributes[attr] = value
    advanced_info["data_attributes"] = data_attributes

    return advanced_info

def extract_css_js_internal_external_images(soup, base_url):
    """Extracts CSS files, JavaScript files, internal links, external links, and images from a web page.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML of the web page.
        base_url (str): The base URL of the web page.

    Returns:
        tuple: A tuple containing sets of CSS files, JavaScript files, internal links, external links, and images.
    """
    css_files = set()
    js_files = set()
    internal_links = set()
    external_links = set()
    images = set()

    css_links = soup.find_all('link', href=True)
    for link in css_links:
        url = link.get('href')
        if url is not None and '.css' in url:
            css_files.add(urljoin(base_url, url))

    script_tags = soup.find_all('script', src=True)
    for tag in script_tags:
        url = tag.get('src')
        if url is not None and '.js' in url:
            js_files.add(urljoin(base_url, url))

    links = soup.find_all('a')
    for link in links:
        url = link.get('href')
        if url is not None:
            if base_url in url:
                internal_links.add(urljoin(base_url, url))
            elif url.startswith('http'):
                external_links.add(url)

    img_tags = soup.find_all('img', src=True)
    for img in img_tags:
        url = img.get('src')
        if url is not None and len(url) > 1:
            images.add(urljoin(base_url, url))

    return css_files, js_files, internal_links, external_links, images

async def check_wayback_availability(url):
    """Checks if a URL is archived on the Wayback Machine.

    Args:
        url (str): The URL to check.

    Returns:
        dict: A dictionary containing information about the archived URL or None if not found.
    """
    wayback_url = 'http://archive.org/wayback/available'
    avail_data = {'url': url}
    
    try:
        response = requests.get(wayback_url, params=avail_data, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            avail_snapshots = json_data.get('archived_snapshots')
            if avail_snapshots:
                return avail_snapshots
            else:
                return None
        else:
            print(f"Error: Status Code {response.status_code}")
            return None
    except Exception as exc:
        print(f"Error checking Wayback Machine availability: {exc}")
        return None

async def main():
    
    target_url = input(f"{YELLOW}Enter the URL to crawl: {WHITE}")
    filename = target_url.replace('http://', '').replace('https://', '').replace('/', '_') + "_Crawler.json"
    result = await crawl(target_url)
    print(f"{GREEN}Crawling completed.{WHITE}")

    # Write data to JSON file
    with open(f'{filename}', 'w') as json_file:
        json.dump(result, json_file, indent=4)
    print(f"{GREEN}Output saved to '{filename}'{WHITE}")

if __name__ == "__main__":
    asyncio.run(main())
