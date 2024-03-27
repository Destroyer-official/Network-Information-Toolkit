import dns.resolver

class MXRecordFetcher:
    """Class to fetch and save MX records for given domains."""

    def __init__(self):
        """Initialize DNS resolver."""
        self.resolver = dns.resolver.Resolver()

    def get_mx_records(self, domain):
        """Fetches MX records for a given domain using dnspython.

        Args:
            domain (str): The domain name for which to fetch MX records.

        Returns:
            list: A list of MX records, each represented as a tuple (preference, exchange):
                * preference (int): The preference value of the MX record.
                * exchange (str): The hostname of the mail exchange.
        """
        try:
            answers = self.resolver.resolve(domain, 'MX')
            mx_records = [(answer.preference, answer.exchange.to_text()) for answer in answers]
            return mx_records

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) as e:
            print(f"No MX records found for {domain} ({e}).")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def save_to_file(self, filename, content):
        """Saves content to a file.

        Args:
            filename (str): The name of the file to save the content to.
            content (str): The content to be saved.
        """
        with open(filename, 'w') as file:
            file.write(content)
        print(f"MX records saved to {filename}")

    def fetch_and_save_mx_records(self, domain):
        """Fetches and saves MX records for a list of domains.

        Args:
            domains (list): List of domains to fetch MX records for.
        """
        try:
            mx_records = self.get_mx_records(domain)

            if mx_records:
                output = f"MX records for {domain}:\n"
                for preference, exchange in mx_records:
                    output += f"Preference: {preference}, Exchange: {exchange}\n"
                self.save_to_file(f"{domain}_MX.txt", output)
            else:
               print(f"No MX records found for {domain}")
        except TimeoutError:
            pass
# Example usage
if __name__ == "__main__":
    mx_fetcher = MXRecordFetcher()
    domains = ['google.com', 'wikipedia.org', 'amazon.com', 'reddit.com', 'microsoft.com', 
               'techtarget.com', 'example.com', 'searchsecurity.techtarget.com']  
    mx_fetcher.fetch_and_save_mx_records(domains)
