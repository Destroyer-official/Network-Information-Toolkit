import dns.resolver

class NSRecordFetcher:
    """Class to fetch and save NS records for given domains."""

    def __init__(self):
        """Initialize DNS resolver."""
        self.resolver = dns.resolver.Resolver()

    def get_ns_records(self, domain):
        """Fetches NS records for a given domain using dnspython.

        Args:
            domain (str): The domain name for which to fetch NS records.

        Returns:
            list: A list of NS records.
        """
        try:
            answers = self.resolver.resolve(domain, 'NS')
            ns_records = [record.to_text() for record in answers]
            return ns_records

        except dns.resolver.NoAnswer:  # Specific for "No Records"
            print(f"No NS records found for {domain}.")
            return []
        except dns.resolver.NXDOMAIN: 
            print(f"The domain {domain} does not exist.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def save_to_file(self, filename, domain, content):
        """Saves content to a file.

        Args:
            filename (str): The name of the file to save the content to.
            domain (str): The domain name for which records were fetched.
            content (list): The list of NS records to be saved.
        """
        with open(filename, 'w+') as file:
            file.write(f"Domain: {domain}\n\n")
            for record in content:
                file.write(record + '\n')
        print(f"NS records saved to {filename}")

    def fetch_and_save_ns_records(self, domain):
        """Fetches and saves NS records for a list of domains.

        Args:
            domains (list): List of domains to fetch NS records for.
        """
        try:
            ns_records = self.get_ns_records(domain)

            if ns_records:
                self.save_to_file(f"{domain}_NS.txt", domain, ns_records)
            else:
                print(f"No NS records found for {domain}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
# Example usage
if __name__ == "__main__":
    ns_fetcher = NSRecordFetcher()
    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']  
    ns_fetcher.fetch_and_save_ns_records(domains)
