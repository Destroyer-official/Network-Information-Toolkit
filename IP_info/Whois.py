import whois
import sys
from urllib.parse import urlparse

def save_whois_info(url):
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url  # Adding prefix if not present
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        domain_info = whois.whois(domain)
        if domain_info:
            output_filename = f"{domain}_Whois.txt"
            with open(output_filename, 'w') as f:
                f.write("WHOIS information for {}\n".format(domain))
                f.write("=" * 50 + "\n")
                f.write(str(domain_info))
                print("Whois information saved to:", output_filename)
        else:
            print("No Whois information available for", domain)
    except Exception as e:
        print("Error occurred:", str(e))

if __name__ == "__main__":
    url = "www.google.com"  # Example URL without prefix
    save_whois_info(url)


