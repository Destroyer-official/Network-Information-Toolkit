import ssl
import socket
import whois
from datetime import datetime

def get_ssl_certificate_info(domain):
    context = ssl.create_default_context()
    with socket.create_connection((domain, 443)) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as ssock:
            cert = ssock.getpeercert()
            return cert

def save_certificate_info_to_file(domain, cert_info, whois_info):
    filename = f"{domain}_SSL_Certificate_Information.txt"
    with open(filename, 'a') as f:
        f.write(f"SSL Certificate Information for {domain}:\n\n")
        for key, value in cert_info.items():
            f.write(f"{key}: {value}\n")
        f.write("\nWhois Information:\n\n")
        f.write(whois_info)
        print(f"Certificate information saved in {filename}.")

def get_whois_info(domain):
    try:
        w = whois.whois(domain)
        return str(w)
    except Exception as e:
        return f"Error getting Whois information: {str(e)}"

def ssl_main():
    domain = input("Enter domain name (e.g., example.com): ")
    cert_info = get_ssl_certificate_info(domain)
    whois_info = get_whois_info(domain)
    save_certificate_info_to_file(domain, cert_info, whois_info)
    

if __name__ == "__main__":
    ssl_main()
