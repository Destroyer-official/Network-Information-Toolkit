import requests
import logging
import json

class BGP:
    def save_to_file(self, filename, domain, content):
        """
        Saves content to a file.

        Args:
            filename (str): The name of the file to save the content to.
            domain (str): The domain name for which records were fetched.
            content (dict): The JSON content to be saved.
        """
        with open(filename, 'w+') as file:
            # Assuming 'content' is a dictionary containing the data to be saved
            json.dump(content, file, indent=4)


    def safe_filename(self, name):
        """Replace invalid characters in filename."""
        return name.replace(':', '_')

    def fetch_data(self, endpoint, output_filename):
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            content = response.json()
            self.save_to_file(output_filename, endpoint, content)
            print(f"Data saved to '{output_filename}' successfully.")
        except requests.exceptions.HTTPError as he:
            logging.error(f"HTTP Error: {he}")
            print(f"Received HTML instead of JSON from '{endpoint}'. Saving as is to '{output_filename}'.")
            with open(output_filename, 'w') as file:
                file.write(response.text)
        except Exception as e:
            logging.error(f"Error fetching data from '{endpoint}': {e}")


    # Function to get ASN Information
    def ASN_Info(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_Info.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}', output_filename)

    # Function to get ASN Prefixes
    def ASN_Prefixes(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_Prefixes.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}/prefixes', output_filename)

    # Function to get ASN Peers
    def ASN_Peers(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_Peers.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}/peers', output_filename)

    # Function to get ASN Upstreams
    def ASN_Upstreams(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_Upstreams.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}/upstreams', output_filename)

    # Function to get ASN Downstreams
    def ASN_Downstreams(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_Downstreams.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}/downstreams', output_filename)

    # Function to get ASN IXs
    def ASN_IXs(self, as_number):
        output_filename = f"{self.safe_filename(as_number)}_ASN_IXs.json"
        self.fetch_data(f'https://api.bgpview.io/asn/{as_number}/ixs', output_filename)

    # Function to get IP Prefix Information
    def IP_Prefix(self, IP, Cidr):
        output_filename = f"{self.safe_filename(IP)}_IP_Prefix.json"
        self.fetch_data(f'https://api.bgpview.io/prefix/{IP}/{Cidr}', output_filename)

    # Function to get IX Information
    def IX(self, ix_id):
        output_filename = f"{self.safe_filename(ix_id)}_IX.json"
        self.fetch_data(f'https://api.bgpview.io/ix/{ix_id}', output_filename)

    # Function to search BGPview
    def Search(self, query):
        output_filename = f"{self.safe_filename(query)}_Search.json"
        self.fetch_data(f'https://api.bgpview.io/search?query_term={query}', output_filename)


if __name__ == "__main__":


    try:
        asn_number = 'AS55836'
        BGP().ASN_Prefixes(asn_number)
        
        asn_number = 'AS13335'
        BGP().ASN_Peers(asn_number)
        BGP().ASN_Upstreams(asn_number)
        BGP().ASN_Downstreams(asn_number)
        BGP().ASN_IXs(asn_number)
        
        ip_address = '192.209.63.0'
        cidr = '24'
        BGP().IP_Prefix(ip_address, cidr)
        
        asn_number = 'AS55836'
        BGP().ASN_Info(asn_number)
        
        ix_id = '492'
        BGP().IX(ix_id)
        
        query = 'digitalocean'
        BGP().Search(query)
    except KeyboardInterrupt:
        print("Operation interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
