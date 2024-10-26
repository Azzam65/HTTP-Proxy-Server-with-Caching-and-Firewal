##Client.py
import socket
import time

def send_request(proxy_host, proxy_port, url):
    if url.startswith("http://"):
        url = url[7:]
    elif url.startswith("https://"):  ## removes HTTP:// OR HTTPS:// From the URL
        url = url[8:]
    
    host, path = (url.split('/', 1) + [""])[:2] ## Split the code before / after it
    path = '/' + path  
           
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.settimeout(10)
        try:
            client_socket.connect((proxy_host, proxy_port))
            request = f"GET {url} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
            client_socket.sendall(request.encode())
        
            start_time = time.time()
            response = b"" ## byte string
            while True:
                part = client_socket.recv(4096)
                if not part:
                    break
                response += part
            elapsed_time = time.time() - start_time
            print(response.decode(errors="ignore"))
            print(f"\nTime taken: {elapsed_time:.4f} seconds")
        except socket.error as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
        
##send_request("localhost", 8080, "http://example.com")
send_request("localhost", 8080, "http://blockedwebsite.com")

