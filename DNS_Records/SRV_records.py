import dns.resolver
import json
import time

class SRVRecordFetcher:
    # Class definition here...

    def fetch_srv_records(self, domain, retries=3, delay=1):
        """Fetches SRV records for a given domain with retry mechanism.

        Args:
            domain (str): The domain name to query for SRV records.
            retries (int): Number of retry attempts (default: 3).
            delay (float): Delay in seconds between retries (default: 1).

        Returns:
            list: A list of dictionaries, each representing an SRV record.
                  An empty list if no SRV records are found.
        """
        for _ in range(retries):
            try:
                answers = dns.resolver.resolve(domain, 'SRV')
                srv_records = []
                for record in answers:
                    srv_records.append({
                        "Priority": record.priority,
                        "Weight": record.weight,
                        "Port": record.port,
                        "Target": record.target.to_text()
                    })
                return srv_records
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                print(f"No SRV records found for {domain}")
                return []
            except dns.exception.Timeout:
                print(f"Timeout occurred while fetching SRV records for {domain}. Retrying...")
                time.sleep(delay)
        print(f"Failed to fetch SRV records for {domain} after {retries} attempts.")
        return []

    def save_to_file(self, filename, srv_records):
        """Saves SRV records to a JSON file.

        Args:
            filename (str): The name of the file to save the SRV records to.
            srv_records (list): The list of SRV records to be saved.
        """
        try:
            with open(filename, "w") as output_file:
                json.dump(srv_records, output_file, indent=4)
            print(f"SRV records saved to {filename}")
        except Exception as e:
            print(f"Error occurred while saving SRV records: {e}")

    def fetch_and_save_srv_records(self, domain):
        """Fetches and saves SRV records for a list of domains.

        Args:
            domains (list): List of domain names to fetch SRV records for.
        """
        try:
            srv_records = self.fetch_srv_records(domain)

            if srv_records:
                self.save_to_file(f"{domain}_srv.json", srv_records)
            else:
                print(f"No SRV records found for {domain}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
# Example usage
if __name__ == '__main__':
    srv_fetcher = SRVRecordFetcher()
    domains = ['_imaps._tcp.gmail.com', '_xmpp-server._tcp.xmpp.org']
    srv_fetcher.fetch_and_save_srv_records(domains)
