import requests
import logging

class IPGeolocationAPI:
    def __init__(self):
        self.apis = [
            'https://ipapi.co/{ip}/json/',
            'https://ipinfo.io/{ip}/json',
            'https://freegeoip.app/json/{ip}',
            # Add more APIs here if needed
        ]

    def get_ip_location(self, ip_address):
        results = {}
        for api in self.apis:
            try:
                url = api.format(ip=ip_address)
                response = requests.get(url, timeout=5)  # Add a timeout of 5 seconds
                response.raise_for_status()  # Raise an exception for non-200 status codes
                data = response.json()
                results[api] = data

            except requests.exceptions.RequestException as e:
                logging.warning("Error from %s: %s", api, e)
                results[api] = {"error": str(e)}

        # Save results to a text file
        filename = f"{ip_address}_IP_location.txt"
        test=1
        with open(filename, 'w', encoding='utf-8') as file:
            for api, data in results.items():
                file.write(f"\n\n api {test} Results :\n\n\n")
                if 'error' in data:
                    file.write(f"Error: {data['error']}\n")
                else:
                    for key, value in data.items():
                        file.write(f"{key}: {value}\n")
                test+=1
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    api = IPGeolocationAPI()
    ip_address = input("Enter an IP address: ")
    api.get_ip_location(ip_address)
