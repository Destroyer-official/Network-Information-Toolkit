import dns.resolver
import socket

class DNSUtils:
    @staticmethod
    def fetch_ip_addresses(domain):
        """
        Fetch all IPv4 and IPv6 addresses associated with a domain name.

        :param domain: Domain name as a string.
        :return: A tuple of two lists containing IPv4 and IPv6 addresses.
        """
        ipv4_addresses = []
        ipv6_addresses = []
        try:
            # Get all the associated addresses
            info = socket.getaddrinfo(domain, None)

            # Separate the IPv4 and IPv6 addresses
            ipv4_addresses = [ip[4][0] for ip in info if ip[0] == socket.AF_INET]
            ipv6_addresses = [ip[4][0] for ip in info if ip[0] == socket.AF_INET6]

        except socket.gaierror as e:
            print(f"Error retrieving IP addresses for {domain}: {e}")

        return ipv4_addresses, ipv6_addresses

    @staticmethod
    def fetch_a_records(domain):
        """
        Fetch A records for a given domain using dnspython.

        :param domain: The domain name for which to fetch A records.
        :return: A list of A records (IP addresses).
        """
        try:
            answers = dns.resolver.resolve(domain, 'A')
            return [record.to_text() for record in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
            print(f"No A records found for {domain}: {e}")
            return []
        except Exception as e:
            print(f"An error occurred while fetching A records for {domain}: {e}")
            return []

def save_to_file(filename, domain, content):
    """
    Save content to a file.

    :param filename: The name of the file to save the content to.
    :param domain: The domain name for which records were fetched.
    :param content: The list of records to be saved.
    """
    with open(filename, 'a') as file:
        file.write(f"Domain: {domain}\n")
        file.write("A Records:\n")
        for record in content[0]:
            file.write(f"- {record}\n")

        file.write("\nIPv4 Addresses:\n")
        for ip in content[1]:
            file.write(f"- {ip}\n")

        file.write("\nIPv6 Addresses:\n")
        for ip in content[2]:
            file.write(f"- {ip}\n")

        file.write("\n\n")
def get_a_records(domain):
    a_records = DNSUtils.fetch_a_records(domain)
    ipv4_addresses, ipv6_addresses = DNSUtils.fetch_ip_addresses(domain)
    records_to_save = (a_records, ipv4_addresses, ipv6_addresses)
    if any(records_to_save):
        save_to_file(f"{domain}_A_records.txt", domain, records_to_save)
        print(f"A records saved to {domain}_A_records.txt")
    else:
        print(f"No records found for {domain}")
if __name__ == "__main__":
    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']





if __name__ == "__main__":

    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']  

    for domain in domains:
        get_a_records(domain)
