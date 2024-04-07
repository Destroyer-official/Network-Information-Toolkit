import logging
import asyncio
from aioipapi import location
import ipapi
import aiohttp

class IPGeolocationAPI:
    def __init__(self):
        self.apis = [
            'https://ipinfo.io/{ip}/json',
            'https://freegeoip.app/json/{ip}',
            # Add more APIs here if needed
        ]

    async def get_ipinfo_location_async(self, ip_address):
        try:
            url = self.apis[0].format(ip=ip_address)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    data = await response.json()
                    return data
        except aiohttp.ClientError as e:
            logging.warning("Error from ipinfo API: %s", e)
            return {"error": str(e)}

    async def get_freegeoip_location_async(self, ip_address):
        try:
            url = self.apis[1].format(ip=ip_address)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    data = await response.json()
                    return data
        except aiohttp.ClientError as e:
            logging.warning("Error from freegeoip API: %s", e)
            return {"error": str(e)}

    async def get_aioipapi_location_async(self, ip_address):
        try:
            return await location(ip_address)
        except Exception as e:
            logging.warning("Error from aioipapi.location: %s", e)
            return {"error": str(e)}

    async def get_ipapi_async(self, ip_address):
        try:
            return ipapi.location(ip=ip_address)
        except Exception as e:
            logging.warning("Error from ipapi.location: %s", e)
            return {"error": str(e)}

    async def get_ip_location(self, ip_address):
        results = {
            "[1]": await self.get_ipinfo_location_async(ip_address),
            "[2]": await self.get_freegeoip_location_async(ip_address),
            "[3]": await self.get_aioipapi_location_async(ip_address),
            "[4]": await self.get_ipapi_async(ip_address),
        }

        # Save results to a text file
        filename = f"{ip_address}_IP_location.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            for api_name, data in results.items():
                file.write(f"Results {api_name} : \n")
                if isinstance(data, dict):
                    for key, value in data.items():
                        # Skip writing unwanted URLs
                        if key not in ['readme', 'url']:
                            if isinstance(value, dict):
                                file.write(f"{key}:\n")
                                for sub_key, sub_value in value.items():
                                    # Skip writing unwanted URLs
                                    if sub_key not in ['readme', 'url']:
                                        file.write(f"  {sub_key}: {sub_value}\n")
                            else:
                                file.write(f"{key}: {value}\n")
                    file.write("\n")  # Add space between API results
                else:
                    file.write(f"{data}\n\n\n")  # In case the result is not a dictionary
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    api = IPGeolocationAPI()
    ip_address = input("Enter an IP address: ")
    asyncio.run(api.get_ip_location(ip_address))
