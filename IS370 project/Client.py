import socket
import time

def send_request(proxy_host, proxy_port, url):
    # Remove 'http://' or 'https://' from the URL
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):
        url = url[8:]

    # Split into host and path
    host, path = (url.split('/', 1) + [""])[:2]
    path = '/' + path  # Ensure path starts with '/'

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(10)
        try:
            # Connect to the proxy server
            client_socket.connect((proxy_host, proxy_port))
            
            # Construct the HTTP request
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}\r\n"
                "Connection: close\r\n\r\n"
            )
            client_socket.sendall(request.encode())

            # Measure time and receive the response
            start_time = time.time()
            response = b""
            while True:
                part = client_socket.recv(4096)
                if not part:
                    break
                response += part
            elapsed_time = time.time() - start_time

            # Print the response and time 
            print(f"Status Code: {response.split()[1]}")
            print("Headers: [Show only key headers]")
            print(f"\nTime taken: {elapsed_time:.4f} seconds")
        except socket.error as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

# Test the client
#send_request("localhost", 8080, "http://example.com")
#send_request("localhost", 8080, "http://example1.com")
send_request("localhost", 8080, "http://google.com")
# Uncomment to test blocked website
#send_request("localhost", 8080, "http://blockedwebsite.com")
