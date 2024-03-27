import dns.resolver

def get_a_records(domain):
    """
    Fetches A records for a given domain using dnspython.

    Args:
        domain (str): The domain name for which to fetch A records.

    Returns:
        list: A list of A records (IP addresses).
    """
    try:
        answers = dns.resolver.resolve(domain, 'A')
        a_records = [record.to_text() for record in answers]
        return a_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        print(f"No A records found for {domain} ({e}).")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

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

if __name__ == "__main__":
    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']  

    for domain in domains:
        a_records = get_a_records(domain)

        if a_records:
            save_to_file(f"{domain}_A.txt", domain, a_records)
            print(f"A records saved to {domain}_A.txt\n")
        else:
            print(f"No A records found for {domain}\n")
