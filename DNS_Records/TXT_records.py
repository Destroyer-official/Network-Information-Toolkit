import dns.resolver

def get_txt_records(domain):
    """
    Fetches TXT records for a given domain using dnspython.

    Args:
        domain (str): The domain name for which to fetch TXT records.

    Returns:
        list: A list of TXT records.
    """
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        txt_records = [record.strings for record in answers]
        return txt_records
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def fetch_txt_records_for_domain(domain):
    """
    Fetches TXT records for a single domain and saves to file.

    Args:
        domain (str): The domain name for which to fetch TXT records.

    Returns:
        str: A message indicating whether the operation was successful or not.
    """
    txt_records = get_txt_records(domain)
    with open(f"{domain}_TXT.txt", 'w+') as file:
            file.write(f"Domain: {domain}\n\n")
            for record in txt_records:
                for text_string in record:
                    file.write(text_string.decode('utf-8') + '\n')
                file.write('\n')
    print(f"TXT records saved to {domain}_TXT.txt\n")
    
if __name__ == "__main__":
    domain = input("Enter the domain: ")
    result = fetch_txt_records_for_domain(domain)
    # print(result)
