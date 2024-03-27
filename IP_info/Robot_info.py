import requests
import json
from bs4 import BeautifulSoup

def parse_robots_txt(url):
    """Parses the robots.txt file of a website.

    Args:
        url (str): The URL of the website to parse robots.txt from.

    Returns:
        dict: Parsed data from the robots.txt file.
    """
    robots_url = url.rstrip('/') + '/robots.txt'

    try:
        response = requests.get(robots_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        user_agent_blocks = []
        current_user_agent = None

        for line in soup.text.splitlines():
            line = line.strip()

            if line.startswith('User-agent:'):
                current_user_agent = {'name': line.split(':')[1].strip(), 'allowed': [], 'disallowed': []}
                user_agent_blocks.append(current_user_agent)

            elif line.startswith('Allow:'):
                if current_user_agent:
                    current_user_agent['allowed'].append(line.split(':')[1].strip())

            elif line.startswith('Disallow:'):
                if current_user_agent:
                    current_user_agent['disallowed'].append(line.split(':')[1].strip())

        combined_data = {'robot_info_robots_txt': user_agent_blocks}
        save_robot_info(url, combined_data)
        print("Robot information saved successfully.")

    except requests.exceptions.RequestException:
        print("Failed to fetch robot information.")

def save_robot_info(url, combined_data):
    """Saves the combined robot data to a file.

    Args:
        url (str): The URL of the website.
        combined_data (dict): The combined robot data to save.
    """
    filename = f"{url.replace('/', '_').replace(':', '_')}_combined_robot_info.json"

    with open(filename, 'w') as outfile:
        json.dump(combined_data, outfile, indent=2)

if __name__=="__main__":
    url = "https://www.wikipedia.org/" 
    parse_robots_txt(url)
