import dns.resolver
import json

class PTRRecordFetcher:
    """Class to fetch and save PTR records for given IP addresses."""

    def fetch_ptr_records(self, ip_address):
        """Fetches PTR records for a given IP address using dnspython.

        Args:
            ip_address (str): The IP address for which to fetch PTR records.

        Returns:
            list: A list of PTR records.
        """
        reversed_ip = '.'.join(reversed(ip_address.split('.'))) + '.in-addr.arpa' 
        try:
            answers = dns.resolver.resolve(reversed_ip, 'PTR')
            ptr_records = [answer.to_text() for answer in answers]
            return ptr_records
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            print(f"No PTR records found for {ip_address}")
            return []

    def save_to_file(self, ip_address, ptr_records):
        """Saves PTR records to a JSON file.

        Args:
            ip_address (str): The IP address for which records were fetched.
            ptr_records (list): The list of PTR records to be saved.
        """
        try:
            with open(f"{ip_address}_ptr.json", "w") as output_file:
                json.dump(ptr_records, output_file, indent=4)
            print(f"PTR records saved to {ip_address}_ptr.json")
        except Exception as e:
            print(f"Error occurred while saving PTR records for {ip_address}: {e}")

    def fetch_and_save_ptr_records(self, ip_address):
        """Fetches and saves PTR records for a list of IP addresses.

        Args:
            ip_addresses (list): List of IP addresses to fetch PTR records for.
        """
        try:
            ptr_records = self.fetch_ptr_records(ip_address)

            if ptr_records:
                self.save_to_file(ip_address, ptr_records)
            else:
                print(f"No PTR records found for {ip_address}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
# Example usage
if __name__ == '__main__':
    ptr_fetcher = PTRRecordFetcher()
    ip_addresses = ['8.8.8.8', '1.1.1.1']

    ptr_fetcher.fetch_and_save_ptr_records(ip_addresses)
