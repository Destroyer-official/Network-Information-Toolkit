import dns.resolver

class SOARecordFetcher:
    """Class to fetch and save SOA records for given domains."""

    def __init__(self):
        """Initialize DNS resolver."""
        self.resolver = dns.resolver.Resolver()

    def get_soa_record(self, domain):
        """Fetches SOA record for a given domain using dnspython.

        Args:
            domain (str): The domain name for which to fetch SOA record.

        Returns:
            str: The SOA record.
        """
        try:
            answers = self.resolver.resolve(domain, 'SOA')
            soa_record = answers[0].to_text()
            return soa_record

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
            print(f"No SOA record found for {domain} ({e}).")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def save_to_file(self, filename, domain, content):
        """Saves content to a file.

        Args:
            filename (str): The name of the file to save the content to.
            domain (str): The domain name for which records were fetched.
            content (str): The content to be saved.
        """
        with open(filename, 'w+') as file:
            file.write(f"Domain: {domain}\n\n")
            file.write(content)
        print(f"SOA record saved to {filename}")

    def fetch_and_save_soa_records(self, domain):
        """Fetches and saves SOA records for a list of domains.

        Args:
            domains (list): List of domains to fetch SOA records for.
        """
        try:
            soa_record = self.get_soa_record(domain)

            if soa_record:
                self.save_to_file(f"{domain}_SOA.txt", domain, soa_record)
            else:
                print(f"No SOA record found for {domain}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
# Example usage
if __name__ == "__main__":
    soa_fetcher = SOARecordFetcher()
    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']  
    soa_fetcher.fetch_and_save_soa_records(domains)
