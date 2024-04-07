import os
import time
import json
import asyncio
import logging
from ipwhois import IPWhois
from imp.ASN_info import BGP
from IP_info.sitemap import sitemap_main
from IP_info.Whois_info import whois_info
from IP_info.Crawler import crawler_fetcher
from IP_info.Robot_info import parse_robots_txt
from IP_info.IP_location import IPGeolocationAPI
from IP_info.HEADER_info import save_header_info
from DNS_Records.A_records import ARecordFetcher
from DNS_Records.NS_records import NSRecordFetcher
from DNS_Records.MX_records import MXRecordFetcher
from DNS_Records.SOA_records import SOARecordFetcher
from DNS_Records.PTR_records import PTRRecordFetcher
from DNS_Records.SRV_records import SRVRecordFetcher
from IP_info.SSL_Certificate_Information import ssl_main
from DNS_Records.CNAME_records import fetch_cname_records
from DNS_Records.TXT_records import fetch_txt_records_for_domain
from IP_info.port_scanner import port_scanner_async as port_scanner


def safe_filename(name):
    return name.replace(':', '_')


def save_file(content, filename):
    try:
        with open(filename, 'w') as file:
            json.dump(content, file, indent=4)
    except IOError as e:
        logging.error(f"Error saving file: {e}")


async def IP_info():
    IP = input("Enter the IP address: ")
    output_filename = f"{safe_filename(IP)}_IP_info.json"
    try:
        obj = IPWhois(IP)
        # Perform RDAP lookup
        results_rdap = await asyncio.to_thread(obj.lookup_rdap, depth=3)
        # Perform WHOIS lookup
        results_whois = await asyncio.to_thread(obj.lookup_whois)
        # Combine the results of RDAP and WHOIS lookups
        results = {
            "rdap": results_rdap,
            "whois": results_whois
        }
        save_file(results, output_filename)
        print(f"Data saved to '{output_filename}' successfully.")
    except Exception as e:  # For unexpected errors
        logging.error(f"Unexpected error occurred: {e}")


async def all_main():
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
        '1': "Get IP Information:\nThis option retrieves detailed information about a specific IP address, including its associated Autonomous System Number (ASN), prefix, country, registry, and more. It combines data from RDAP and WHOIS lookups to provide comprehensive insights.",
        '2': "Port Scanner:\nPort Scanner is a powerful tool that probes a server or host to determine if specific network ports are open. Open ports indicate the presence of active services, allowing users to assess the security and accessibility of a system.",
        '3': "Whois Information:\nWHOIS is a tool used to retrieve registration information for domains. This option allows users to obtain WHOIS information for a given domain, providing details about its registrant, registrar, registration date, and more. Example of domain for test: www.google.com.",
        '4': "Get Crawler:\nThe Crawler tool retrieves data related to web crawling for a specified domain, aiding in website indexing and analysis. It allows users to gather information about a website's structure, content, and links, facilitating SEO optimization and content management. Example of domain for test: https://www.google.com.",
        '5': "Get Header Information:\nRetrieves header information from HTTP requests for a given domain. This option provides insights into server configurations, supported protocols, and response headers, helping users understand how web servers handle incoming requests. Example of domain for test: https://www.google.com.",
        '6': "Get Robot Information:\nRetrieves information from the robots.txt file of a domain, helping users understand directives for web crawlers. The robots.txt file specifies which parts of a website should be crawled or not crawled by search engine spiders. Example of domain for test: https://www.wikipedia.org/.",
        '7': "Get Sitemap Information:\nRetrieves sitemap information for a domain, assisting users in understanding website structure and content organization. Sitemaps provide a list of URLs on a website, helping search engines index web pages more efficiently. Example of domain for test: www.xml-sitemaps.com, depth: 2.",
        '8': "Get SSL Certificate Information:\nRetrieves SSL certificate information for a domain, including certificate authority, validity period, and encryption algorithms. SSL certificates ensure secure communication between web servers and clients, protecting sensitive data from eavesdropping and tampering. Example of domain for test: www.wikipedia.org/.",
        '9': "Get ASN Prefixes:\nRetrieves information about the IP address prefixes assigned to a specific Autonomous System Number (ASN). ASN prefixes, also known as IP address blocks, are blocks of IP addresses allocated to organizations or ISPs for their use. Example of ASN for test: AS55836.",
        '10': "Get ASN Peers:\nRetrieves information about the peers of a specific ASN. Peers are entities that have established peering relationships with the queried ASN, enabling direct exchange of traffic between their networks. Example of ASN for test: AS13335.",
        '11': "Get ASN Upstreams:\nRetrieves information about the upstream providers of a specific ASN. Upstream providers are larger networks to which the queried ASN connects to gain access to the global internet. Example of ASN for test: AS13335.",
        '12': "Get ASN Downstreams:\nRetrieves information about the downstream networks of a specific ASN. Downstream networks receive internet connectivity from their upstream providers, forming the hierarchical structure of internet routing. Example of ASN for test: AS13335.",
        '13': "Get ASN IXs:\nRetrieves information about the Internet Exchange Points (IXPs) that a specific ASN is connected to. IXPs are physical locations where different networks come together to peer with each other directly, facilitating the exchange of internet traffic. Example of ASN for test: AS13335.",
        '14': "Get IP Prefix Information:\nRetrieves information about a specific IP address prefix, including details about the associated ASN, registry, country, and more. IP prefixes, also known as IP address blocks or subnets, are blocks of IP addresses allocated to organizations or ISPs for their use. Example of IP address and CIDR for test: '192.209.63.0', '24'.",
        '15': "Get ASN Information:\nRetrieves general information about a specific Autonomous System Number (ASN), such as its name, description, country, registry, etc. ASNs are unique identifiers assigned to autonomous systems, which are collections of IP networks and routers under the control of one or more network operators. Example of ASN for test: AS55836.",
        '16': "Get IX Information:\nRetrieves information about a specific Internet Exchange Point (IXP), including its name, location, participants, and other relevant details. IXPs are physical locations where different networks come together to peer with each other directly, facilitating the exchange of internet traffic. Example of IX ID for test: 492.",
        '17': "Search:\nAllows users to search for information across multiple categories, including ASNs, IP addresses, IXPs, and more. Users can input a search query, and the API returns relevant information based on the query. Example of search query for test: 'digitalocean'.",
        '18': "Get A Records:\nRetrieves A records for a given domain, providing information about the IPv4 addresses associated with the domain. A records are DNS records that map domain names to IP addresses. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'.",
        '19': "Get CNAME Records:\nRetrieves Canonical Name (CNAME) records for a given domain, providing information about the aliases or canonical names associated with the domain. CNAME records are DNS records used to alias one domain name to another. Example of domain for test: 'www.google.com', 'www.wikipedia.org', 'www.amazon.com', 'www.reddit.com', 'www.microsoft.com','www.techtarget.com','www.blog.example.','Searchsecurity.techtarget.com'.",
        '20': "Get MX Records:\nRetrieves Mail Exchange (MX) records for a given domain, providing information about the mail servers responsible for receiving email messages on behalf of the domain. MX records are DNS records used in email delivery. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'.",
        '21': "Get SOA Records:\nRetrieves Start of Authority (SOA) records for a given domain, providing information about the authoritative name server for the domain and other related details. SOA records are DNS records that indicate the start of a zone of authority. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'.",
        '22': "Get NS Records:\nRetrieves Name Server (NS) records for a given domain, providing information about the authoritative name servers for the domain. NS records are DNS records that specify the name servers responsible for a DNS zone. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com'.",
        '23': "Get PTR Records:\nRetrieves Pointer (PTR) records for a given IP address, providing information about the domain name associated with the IP address. PTR records are DNS records used for reverse DNS lookups. Example of IP address for test: '8.8.8.8', '1.1.1.1'.",
        '24': "Get SRV Records:\nRetrieves Service (SRV) records for a given domain, providing information about available services and their locations. SRV records are DNS records used to specify the location of services such as SIP, LDAP, and XMPP. Example of domain for test: '_imaps._tcp.gmail.com', '_xmpp-server._tcp.xmpp.org'.",
        '25': "Get TXT Records:\nRetrieves Text (TXT) records for a given domain, providing arbitrary textual information associated with the domain. TXT records are DNS records used to store descriptive text. Example of domain for test: 'google.com', 'wikipedia.org', 'amazon.com'.",
        '26': "IP Location:\nRetrieves geolocation information for a specific IP address, including details such as country, region, city, latitude, longitude, and more. Geolocation data provides insights into the physical location of an IP address, aiding in network administration and security analysis."
    }

    if choice in functionalities:
        print(functionalities[choice])
    else:
        print("Invalid choice! Please choose a number between 1 and 26.")
        return

    # Perform selected action
    if choice == '1':
        await IP_info()
    elif choice == '2':
        await port_scanner()
    elif choice == '3':
        domain = input("Enter the domain: ")
        whois_info(domain)
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
        BGP().ASN_Prefixes(asn_number)
    elif choice == '10':
        asn_number = input("Enter the ASN number: ")
        BGP().ASN_Peers(asn_number)
    elif choice == '11':
        asn_number = input("Enter the ASN number: ")
        BGP().ASN_Upstreams(asn_number)
    elif choice == '12':
        asn_number = input("Enter the ASN number: ")
        BGP().ASN_Downstreams(asn_number)
    elif choice == '13':
        asn_number = input("Enter the ASN number: ")
        BGP().ASN_IXs(asn_number)
    elif choice == '14':
        ip_address = input("Enter the IP address: ")
        cidr = input("Enter the CIDR: ")
        BGP().IP_Prefix(ip_address, cidr)
    elif choice == '15':
        asn_number = input("Enter the ASN number: ")
        BGP().ASN_Info(asn_number)
    elif choice == '16':
        ix_id = input("Enter the IX ID: ")
        BGP().IX(ix_id)
    elif choice == '17':
        query = input("Enter your search query: ")
        BGP().Search(query)
    elif choice == '18':
        A_fetcher = ARecordFetcher()
        domain = input("Enter the domain: ")
        A_fetcher.get_a_records(domain)
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
            await api.get_ip_location(ip_address)
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        asyncio.run(all_main())
