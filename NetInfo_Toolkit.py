import requests  # Library for making HTTP requests to web servers
import json      # Library for working with JSON data
from ipwhois import IPWhois  # Library for gathering IP address information
import socket    # Library for network communication
import errno     # Library for defining error codes
# Libraries for parallel processing
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from IP_info.Whois import save_whois_info
from IP_info.HEADER_info import save_header_info
from IP_info.Robot_info import parse_robots_txt
from IP_info.sitemap import sitemap_main
from IP_info.SSL_Certificate_Information import ssl_main
from IP_info.Crawler import crawler_fetcher
from IP_info.IP_location import IPGeolocationAPI
from DNS_Records.A_records import get_a_records
from DNS_Records.CNAME_records import fetch_cname_records
from DNS_Records.MX_records import MXRecordFetcher
from DNS_Records.TXT_records import fetch_txt_records_for_domain
from DNS_Records.SOA_records import SOARecordFetcher
from DNS_Records.NS_records import NSRecordFetcher
from DNS_Records.PTR_records import PTRRecordFetcher
from DNS_Records.SRV_records import SRVRecordFetcher
import os


def safe_filename(name):
    return name.replace(':', '_')


def save_file(content, filename):
    with open(filename, 'w') as file:
        json.dump(content, file, indent=4)


def IP_info():
    IP = input("Enter the IP address: ")
    output_filename = f"{safe_filename(IP)}_IP_info.json"
    try:
        obj = IPWhois(IP)
        # Perform RDAP lookup
        results_rdap = obj.lookup_rdap(depth=3)
        # Perform WHOIS lookup
        results_whois = obj.lookup_whois()
        # Combine the results of RDAP and WHOIS lookups
        results = {
            "rdap": results_rdap,
            "whois": results_whois
        }
        save_file(results, output_filename)
        print(f"Data saved to '{output_filename}' successfully.")
    except Exception as e:  # For unexpected errors
        logging.error(f"Unexpected error occurred: {e}")


# Configuration parameters
MAX_THREAD_WORKERS = 100
DEFAULT_PROCESSES = 50
DEFAULT_TIMEOUT = 3  # Seconds


def get_scan_target():
    """Prompt the user for target details and perform input validation.

    Returns:
        tuple: (target_ip, start_port, end_port, timeout)
    """

    while True:
        target_address = input("Enter target IPv4 address or hostname: ")
        try:
            target_ip = socket.gethostbyname(target_address)
            return target_ip, *get_port_range(), get_connection_timeout()
        except socket.gaierror:
            print("Invalid hostname. Please try again.")
            exit()


def get_port_range():
    """Get a valid port range from the user.

    Returns:
        tuple: (start_port, end_port)
    """

    while True:
        try:
            start_port = int(input("Enter start port (0-65535): "))
            end_port = int(input("Enter end port (0-65535): "))
            if 0 <= start_port <= end_port <= 65535:
                return start_port, end_port
            else:
                print("Invalid port range. Ports must be between 0 and 65535.")
        except ValueError:
            print("Invalid input. Please enter integers.")


def get_connection_timeout():
    """Get a connection timeout from the user with a default value.

    Returns:
        int: Timeout in seconds
    """

    while True:
        timeout_input = input(
            "Enter connection timeout (in seconds, default is 3): ")
        try:
            return int(timeout_input) if timeout_input.strip() else DEFAULT_TIMEOUT
        except ValueError:
            print("Invalid timeout value. Please enter an integer.")


def check_port(target_ip, port, timeout):
    """Attempt to connect to a port, handle errors, and report status.

    Args:
        target_ip (str): The target IP address.
        port (int): The port number.
        timeout (int): Connection timeout in seconds.
    """

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            result = sock.connect_ex((target_ip, port))

            if result == 0:
                print(f"Port {port} is open")
            elif result in (errno.ETIMEDOUT, errno.ECONNREFUSED):
                print(f"Port {port} is closed or filtered")
            elif result == errno.WSAEWOULDBLOCK:  # Handle WSAEWOULDBLOCK error
                pass  # Ignore this error
            else:
                print(
                    f"Port {port}: Unexpected error - {errno.errorcode[result]}")
        except socket.error as err:
            print(f"Port {port}: Connection error - {err}")


def scan_ports_threaded(target_ip, start_port, end_port, timeout):
    """Scan a port range using a thread pool for efficiency.

    Args:
        target_ip (str): The target IP address.
        start_port (int): The starting port of the range.
        end_port (int): The ending port of the range.
        timeout (int): Connection timeout in seconds.
    """

    with ThreadPoolExecutor(max_workers=MAX_THREAD_WORKERS) as executor:
        for port in range(start_port, end_port + 1):
            executor.submit(check_port, target_ip, port, timeout)


def distribute_ports_processes(target_ip, start_port, end_port, timeout, num_processes=DEFAULT_PROCESSES):
    """Distribute scanning tasks across multiple processes.

    Args:
        target_ip (str): The target IP address.
        start_port (int): The starting port of the range.
        end_port (int): The ending port of the range.
        timeout (int): Connection timeout in seconds.
        num_processes (int): Number of processes to spawn.
    """

    chunk_size, remainder = divmod(end_port - start_port + 1, num_processes)

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        for i in range(num_processes):
            process_start = start_port + (i * chunk_size)
            process_end = process_start + chunk_size - 1
            if i == num_processes - 1:
                process_end += remainder

            executor.submit(scan_ports_threaded, target_ip,
                            process_start, process_end, timeout)


def port_scanner():
    try:
        target_ip, start_port, end_port, timeout = get_scan_target()
        distribute_ports_processes(target_ip, start_port, end_port, timeout)
    except KeyboardInterrupt:
        print("\nScan interrupted by YOU.")


def fetch_data(endpoint, output_filename):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        content = response.json()
        save_to_file(content, output_filename)
        print(f"Data saved to '{output_filename}' successfully.")
    except requests.exceptions.HTTPError:
        print(f"Received HTML instead of JSON from '{
              endpoint}'. Saving as is to '{output_filename}'.")
        with open(output_filename, 'w') as file:
            file.write(response.text)
    except Exception as e:
        logging.error(f"Error fetching data from '{endpoint}': {e}")

# Function to get ASN Information


def ASN_Info(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_Info.json"
    fetch_data(f'https://api.bgpview.io/asn/{as_number}', output_filename)

# Function to get ASN Prefixes


def ASN_Prefixes(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_Prefixes.json"
    fetch_data(
        f'https://api.bgpview.io/asn/{as_number}/prefixes', output_filename)

# Function to get ASN Peers


def ASN_Peers(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_Peers.json"
    fetch_data(
        f'https://api.bgpview.io/asn/{as_number}/peers', output_filename)

# Function to get ASN Upstreams


def ASN_Upstreams(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_Upstreams.json"
    fetch_data(
        f'https://api.bgpview.io/asn/{as_number}/upstreams', output_filename)

# Function to get ASN Downstreams


def ASN_Downstreams(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_Downstreams.json"
    fetch_data(
        f'https://api.bgpview.io/asn/{as_number}/downstreams', output_filename)

# Function to get ASN IXs


def ASN_IXs(as_number):
    output_filename = f"{safe_filename(as_number)}_ASN_IXs.json"
    fetch_data(f'https://api.bgpview.io/asn/{as_number}/ixs', output_filename)

# Function to get IP Prefix Information


def IP_Prefix(IP, Cidr):
    output_filename = f"{safe_filename(IP)}_IP_Prefix.json"
    fetch_data(f'https://api.bgpview.io/prefix/{IP}/{Cidr}', output_filename)


# Function to get IX Information
def IX(ix_id):
    output_filename = f"{safe_filename(ix_id)}_IX.json"
    fetch_data(f'https://api.bgpview.io/ix/{ix_id}', output_filename)

# Function to search BGPview


def Search(query):
    output_filename = f"{safe_filename(query)}_Search.json"
    fetch_data(
        f'https://api.bgpview.io/search?query_term={query}', output_filename)


def save_to_file(filename, domain, content):
    """
    Saves content to a file.

    Args:
        filename (str): The name of the file to save the content to.
        domain (str): The domain name for which records were fetched.
        content (list): The list of A records to be saved.
    """
    with open(filename, 'w+') as file:
        file.write(f"Domain: {domain}\n\n")
        for record in content:
            file.write(record + '\n')


def all_main():
    time.sleep(3)
    os.system("cls")
    os.system("clear")
    print("\n\n")
    print("Choose an option:")
    print("1.  Get IP Information")
    print("2.  Port Scanner")
    print("3.  Get Whois information")
    print("4.  Get Crawler")
    print("5.  Get Header")
    print("6.  Get Robot information")
    print("7.  Get sitemap")
    print("8.  Get SSL Certificate information")
    print("9.  Get ASN Prefixes")
    print("10. Get ASN Peers")
    print("11. Get ASN Upstreams")
    print("12. Get ASN Downstreams")
    print("13. Get ASN IXs")
    print("14. Get IP Prefix Information")
    print("15. Get ASN Information")
    print("16. Get IX Information")
    print("17. Search")
    print("18. Get A Records")
    print("19. Get CNAME Records")
    print("20. Get MX Records")
    print("21. Get SOA Records")
    print("22. Get NS Records")
    print("23. Get PTR Records")
    print("24. Get SRV Records")
    print("25. Get TXT Records")
    print("26. Get IP Locations")
    choice = input("Enter your choice (1-26): ")
    os.system("clear")
    os.system("cls")
    functionalities = {
        '1': "Get IP Information:\nThis option retrieves information about a specific IP address, including details such as its associated ASN, prefix, country, registry, and more.",
        '2': "Port Scanner:\nPort Scanner is a powerful tool that probes a server or host to determine if specific network ports are open, indicating the presence of active services.",
        '3': "Whois information:\nWHOIS is a tool used to retrieve registration information for domains. Example of domain for test: www.google.com.",
        '4': "Get Crawler:\nThe Crawler tool retrieves data related to web crawling for a specified domain, aiding in website indexing and analysis. Example of domain for test: https://www.google.com.",
        '5': "Get Header :\nRetrieves header information from HTTP requests for a given domain, providing insights into server configurations and protocols. Example of domain for test: https://www.google.com.",
        '6': "Get Robot information :\nRetrieves information from the robots.txt file of a domain, helping users understand directives for web crawlers. Example of domain for test: https://www.wikipedia.org/.",
        '7': "Get sitemap :\nsitemap  .Retrieves sitemap information for a domain, assisting users in understanding website structure and content organization. Example of domain for test: www.xml-sitemaps.com.",
        '8': "Get SSL Certificate information :\nRetrieves SSL certificate information for a domain, including certificate authority, validity period, and encryption algorithms. Example of domain for test: https://www.wikipedia.org/.",
        '9': "Get ASN Prefixes:\nASN prefixes, also known as IP address blocks, are blocks of IP addresses assigned to autonomous systems. This option retrieves information about the IP address prefixes assigned to a specific ASN. Example of domain for test:'AS55836'",
        '10': "Get ASN Peers:\nPeering is the process of interconnecting separate networks for the purpose of exchanging traffic directly rather than via the internet backbone. Peers are entities that have agreed to exchange traffic between their networks. This option retrieves information about the peers of a specific ASN. It lists other autonomous systems that have established peering relationships with the queried ASN. Example of domain for test:'AS13335'",
        '11': "Get ASN Upstreams:\nUpstream providers are larger networks to which an autonomous system (ISP) connects to gain access to the global internet. These providers offer connectivity and routes to the rest of the internet. This option retrieves information about the upstream providers of a specific ASN. It lists the autonomous systems that provide connectivity to the queried ASN. Example of domain for test:'AS13335'",
        '12': "Get ASN Downstreams:\nDownstream networks are smaller networks that connect to a larger network (upstream provider) to access the internet. Downstream networks receive internet connectivity from their upstream providers. This option retrieves information about the downstream networks of a specific ASN. It lists the autonomous systems that receive connectivity from the queried ASN. Example of domain for test:'AS13335'",
        '13': "Get ASN IXs:\nInternet Exchange Points (IXPs) are physical locations where different networks come together to peer with each other directly. IXs facilitate the exchange of internet traffic between various networks. This option retrieves information about the Internet Exchange Points that a specific ASN is connected to. It lists the IXPs where the queried ASN peers with other networks. Example of domain for test:'AS13335'",
        '14': "Get IP Prefix Information:\nIP prefixes, also known as IP address blocks or subnets, are blocks of IP addresses allocated to organizations or ISPs for their use. This option retrieves information about a specific IP address prefix, including details about the associated ASN, registry, country, and more. Example of domain for test:'192.209.63.0', '24'",
        '15': "Get ASN Information:\nASN stands for Autonomous System Number. It's a unique identifier assigned to an autonomous system (AS), which is a collection of IP networks and routers under the control of one or more network operators that share a common, clearly defined routing policy. This option retrieves general information about a specific ASN, such as its name, description, country, registry, etc. Example of domain for test:'AS55836'",
        '16': "Get IX Information:\nThis option retrieves information about a specific Internet Exchange Point (IXP), including its name, location, participants, and other relevant details. Example of domain for test:'492'",
        '17': "Search:\nThis option allows users to search for information across multiple categories, including ASNs, IP addresses, IXPs, and more. Users can input a search query, and the API returns relevant information based on the query. Example of domain for test:'digitalocean'",
        '18': "Get A Records:\nThis option retrieves A records for a given domain. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'",
        '19': "Get CNAME Records:\nThis option retrieves CNAME records for a given domain. Example of domain for test: 'www.google.com', 'www.wikipedia.org', 'www.amazon.com', 'www.reddit.com', 'www.microsoft.com','www.techtarget.com','www.blog.example.','Searchsecurity.techtarget.com'",
        '20': "Get MX Records:\nThis option retrieves MX records for a given domain. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'",
        '21': "Get SOA Records:\nThis option retrieves SOA records for a given domain. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'",
        '22': "Get NS Records:\nThis option retrieves NS records for a given domain. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'",
        '23': "Get PTR Records:\nThis option retrieves PTR records for a given IP address. Example: '8.8.8.8', '1.1.1.1'",
        '24': "Get SRV Records:\nThis option retrieves SRV records for a given domain. Example of domain for test: '_imaps._tcp.gmail.com', '_xmpp-server._tcp.xmpp.org'",
        '25': "Get TXT Records:\nThis option retrieves TXT  for a given domain. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com'",
        '26': "IP Location:\nThis option retrieves geolocation information for a specific IP address, including details such as country, region, city, latitude, longitude, and more."
    }

    if choice in functionalities:
        print(functionalities[choice])
    else:
        print("Invalid choice! Please choose a number between 1 and 26.")
        return

    # Perform selected action
    if choice == '1':
        IP_info()
    elif choice == '2':
        port_scanner()
    elif choice == '3':
        domain = input("Enter the domain: ")
        save_whois_info(domain)
    elif choice == '4':
        domain = input("Enter the domain: ")
        crawler_fetcher(domain)
    elif choice == '5':
        domain = input("Enter the domain: ")
        save_header_info(domain)
    elif choice == '6':
        domain = input("Enter the domain: ")
        parse_robots_txt(domain)
    elif choice == '7':
        sitemap_main()
    elif choice == '8':
        ssl_main()
    elif choice == '9':
        asn_number = input("Enter the ASN number: ")
        ASN_Prefixes(asn_number)
    elif choice == '10':
        asn_number = input("Enter the ASN number: ")
        ASN_Peers(asn_number)
    elif choice == '11':
        asn_number = input("Enter the ASN number: ")
        ASN_Upstreams(asn_number)
    elif choice == '12':
        asn_number = input("Enter the ASN number: ")
        ASN_Downstreams(asn_number)
    elif choice == '13':
        asn_number = input("Enter the ASN number: ")
        ASN_IXs(asn_number)
    elif choice == '14':
        ip_address = input("Enter the IP address: ")
        cidr = input("Enter the CIDR: ")
        IP_Prefix(ip_address, cidr)
    elif choice == '15':
        asn_number = input("Enter the ASN number: ")
        ASN_Info(asn_number)
    elif choice == '16':
        ix_id = input("Enter the IX ID: ")
        IX(ix_id)
    elif choice == '17':
        query = input("Enter your search query: ")
        Search(query)
    elif choice == '18':
        domain = input("Enter the domain: ")
        a_records = get_a_records(domain)
        if a_records:
            save_to_file(f"{domain}_A.txt", domain, a_records)
            print(f"A records saved to {domain}_A.txt\n")
        else:
            print(f"No A records found for {domain}\n")
    elif choice == '19':
        domain = input("Enter the domain: ")
        fetch_cname_records(domain)
    elif choice == '20':
        mx_fetcher = MXRecordFetcher()
        domain = input("Enter the domain: ")
        mx_fetcher.fetch_and_save_mx_records(domain)
    elif choice == '21':
        soa_fetcher = SOARecordFetcher()
        domain = input("Enter the domain: ")
        soa_fetcher.fetch_and_save_soa_records(domain)
    elif choice == '22':
        ns_fetcher = NSRecordFetcher()
        domain = input("Enter the domain: ")
        ns_fetcher.fetch_and_save_ns_records(domain)
    elif choice == '23':
        ptr_fetcher = PTRRecordFetcher()
        ip_address = input("Enter the IP address: ")
        ptr_fetcher.fetch_and_save_ptr_records(ip_address)
    elif choice == '24':
        srv_fetcher = SRVRecordFetcher()
        domain = input("Enter the domain: ")
        srv_fetcher.fetch_and_save_srv_records(domain)
    elif choice == '25':
        domain = input("Enter the domain: ")
        fetch_txt_records_for_domain(domain)
    elif choice == '26':
        api = IPGeolocationAPI()
        ip_address = input("Enter the IP address: ")
        try:
            api.get_ip_location(ip_address)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        all_main()
