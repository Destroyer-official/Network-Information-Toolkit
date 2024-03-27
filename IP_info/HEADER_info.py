import requests

def save_header_info(url):
    try:
        response = requests.head(url)
        headers = response.headers
        file_name = url.replace("://", "_").replace("/", "_").replace(".", "_") + "_header.txt"
        with open(file_name, "w") as file:
            file.write("Header Information for " + url + "\n")
            file.write("=====================================\n")
            for header in headers:
                file.write(header + ": " + headers[header] + "\n")
            file.write("=====================================")
        print("Header information saved in", file_name)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

# Example usage:
if __name__ == "__main__":
    url = "https://www.google.com"
    save_header_info(url)
