import dns.resolver
import subprocess
from typing import List

def get_cname_records(domain: str) -> List[str]:
    """
    Collects CNAME records for a given domain using multiple methods.

    Args:
        domain (str): The domain to query for CNAME records.

    Returns:
        List[str]: A list of CNAME records for the given domain.
    """
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        return [answer.target.to_text() for answer in answers]
    except dns.resolver.NoAnswer:
        print(f"No CNAME records found for {domain}.")
        return []
    except dns.resolver.NXDOMAIN:
        print(f"The domain {domain} does not exist.")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def save_to_file(domain: str, cname_records: List[str]) -> None:
    """
    Saves CNAME records to a file.

    Args:
        domain (str): The domain for which records are fetched.
        cname_records (List[str]): The list of CNAME records to save.
    """
    filename = f"{domain}_CNAME.txt"
    with open(filename, 'w') as file:
        for record in cname_records:
            file.write(record + '\n')
    print(f"CNAME records for {domain} saved in {filename}")

def get_cname_records_using_dig(domain: str) -> List[str]:
    """
    Uses 'dig' command to get CNAME records for a given domain.

    Args:
        domain (str): The domain to query for CNAME records.

    Returns:
        List[str]: A list of CNAME records for the given domain.
    """
    try:
        result = subprocess.run(['dig', domain, 'CNAME', '+short'], capture_output=True, text=True)
        return result.stdout.splitlines()
    except FileNotFoundError:
        print("The 'dig' command is not available. Please install it.")
        return []

def fetch_cname_records(domain):
    """
    Fetches CNAME records for a list of domains.

    Args:
        domains (List[str]): List of domains to fetch CNAME records for.
    """
    try:
        cname_records = []

        # Try dnspython method
        cname_records += get_cname_records(domain)

        # Try dig command (if available)
        cname_records += get_cname_records_using_dig(domain)

        if cname_records:
            save_to_file(domain, cname_records)
        else:
            print(f"No CNAME records found for {domain}")

    except TimeoutError:
        pass
        # Usage example
if __name__ == "__main__":
    domains_names = ['www.google.com', 'www.wikipedia.org', 'www.amazon.com', 'www.reddit.com', 'www.microsoft.com','www.techtarget.com','www.blog.example.','Searchsecurity.techtarget.com']
    fetch_cname_records(domains_names)
