import asyncio

DEFAULT_TIMEOUT = 3

async def check_port_async(target_ip, port, timeout, filename):
    """Attempt to connect to a port asynchronously and report status."""
    try:
        conn = asyncio.open_connection(target_ip, port)
        _, _ = await asyncio.wait_for(conn, timeout=timeout)
        print(f"Port {port} is open")
        with open(filename, 'a') as outfile:
            outfile.write(f"\nPort {port} is open")
    except (asyncio.TimeoutError, ConnectionRefusedError):
        pass
    except Exception as e:
        pass

async def scan_ports_async(target_ip, start_port, end_port, timeout, filename):
    """Scan a port range asynchronously."""
    tasks = [check_port_async(target_ip, port, timeout, filename) for port in range(start_port, end_port + 1)]
    await asyncio.gather(*tasks)

def port_scanner_async():
    target_ip = input("Enter target IPv4 address or hostname: ")
    start_port = int(input("Enter start port (0-65535): "))
    end_port = int(input(f"Enter end port ({start_port}-65535): "))
    timeout = int(input("Enter connection timeout (in seconds, default is 3): ") or DEFAULT_TIMEOUT)
    filename = f'{target_ip}_port_scanner.txt'

    try:
        with open(filename, 'a') as outfile:
            outfile.write(f"Scanning ports from {start_port} to {end_port} on {target_ip} timeout {timeout}\n")
        asyncio.run(scan_ports_async(target_ip, start_port, end_port, timeout, filename))
        print(f'Saved output in {filename}')
    except KeyboardInterrupt:
        print("\nScan interrupted by YOU.")
    except Exception as e:
        pass

if __name__ == "__main__":
    port_scanner_async()
