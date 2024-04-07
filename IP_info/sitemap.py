import os
import re
import argparse
import pyvis
import matplotlib.cm as cm
import concurrent.futures
import logging
import tldextract
import webbrowser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
import matplotlib.colors as mcolors
import http.server
import socketserver


logging.basicConfig(filename='sitemap.log', level=logging.ERROR)


class LinkExtractor:
    def __init__(self, url, depth):
        self.base_url = url
        self.depth = depth
        self.visited = set()
        self.all_links = set()
        self.session = requests.Session()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=60)  # Adjust workers as needed

    def close_session(self):
        self.session.close()
        self.executor.shutdown()

    def get_internal_links(self, url):
        try:
            response = self.session.get(url, timeout=5)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')
            internal_links = []
            for link in soup.find_all('a'):
                href = link.get('href')
                if href and not re.match('(http|https|ftp|javascript)', href):
                    internal_links.append(urljoin(url, href))
            return internal_links
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting links from {url}: {e}")
            return []

    def extract_links(self, url, depth):
        if depth == 0:
            return
        try:
            internal_links = self.get_internal_links(url)
            futures = []
            for link in internal_links:
                if link not in self.visited:
                    self.visited.add(link)
                    self.all_links.add(link)
                    futures.append(self.executor.submit(self.extract_links, link, depth-1))
            concurrent.futures.wait(futures)  # Process futures in batches
        except Exception as e:
            logging.error(f"Error extracting links from {url}: {e}")

    def save_links_to_file(self):
        domain = tldextract.extract(self.base_url).domain
        file_name = f"{domain}_depth{self.depth}.txt"
        directory = "sitemap_files"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(f"Links found on {self.base_url}:\n")
            for link in self.all_links:
                file.write(link + '\n')
        logging.info(f"{len(self.all_links)} links found and saved to {file_name}")
        return file_path


class EnhancedLinkExtractor(LinkExtractor):
    def visualize_sitemap(self, interactive=True):
        G = nx.DiGraph()
        for url in self.all_links:
            G.add_node(url, title=url)  # Include full URL as node attribute for hover effect
            for child in self.all_links:
                if child.startswith(url) and child != url:
                    G.add_edge(url, child)

        # Generate colors for each node using a color map
        color_map = cm.plasma.colors
        node_colors = [mcolors.to_hex(color_map[i]) for i in range(len(G.nodes()))]

        # Draw nodes with custom attributes for hover effect
        nt = pyvis.network.Network(height='900', width='100%', notebook=True)
        nt.from_nx(G)

        # Configure hover effects to show full URL
        nt.set_edge_smooth('dynamic')
        nt.show_buttons(filter_=['physics'])  # Enable zooming and panning

        # Assign color and hover information to nodes
        for idx, node in enumerate(G.nodes()):  # Iterate with index
            nt.nodes[idx]['color'] = node_colors[idx]
            nt.nodes[idx]['title'] = node

        # Save the visualization as HTML file
        nt.save_graph("sitemap_files/sitemap.html")


def validate_input(url, depth):
    if not re.match(r'(https?://)?[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}', url):
        raise ValueError("Invalid URL format")
    if not isinstance(depth, int) or depth <= 0:
        raise ValueError("Invalid depth level. Depth level must be a positive integer")


def serve_html_file(filename):
    class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=os.path.dirname(os.path.abspath(filename)), **kwargs)

    PORT = 8080
    with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
        print(f"HTTP server serving at port {PORT}...")
        webbrowser.open(f'http://localhost:{PORT}/{os.path.basename(filename)}')  # Open the HTML file in the browser
        httpd.serve_forever()


def sitemap_main():
    url = input('\t Enter URL: ')
    depth = int(input('\t Enter depth: '))
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url  # Add http:// prefix if missing
        validate_input(url, depth)
        extractor = EnhancedLinkExtractor(url, depth)  # Using EnhancedLinkExtractor
        extractor.extract_links(url, depth)
        file_name = extractor.save_links_to_file()
        extractor.visualize_sitemap()
        extractor.close_session()
        os.system('cls')
        os.system('clear')
        print(f"\n\t{len(extractor.all_links)} links found and saved to {file_name}\n")

        # Serve the HTML file directly after it's created
        serve_html_file("sitemap_files/sitemap.html")

    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")


if __name__ == '__main__':
    sitemap_main()
