import socket
import time

def send_request(proxy_host, proxy_port, url):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((proxy_host, proxy_port))
        request = f"GET {url} HTTP/1.1\r\nHost: {url}\r\nConnection: close\r\n\r\n"
        client_socket.sendall(request.encode())
        
        start_time = time.time()
        response = b""
        while True:
            part = client_socket.recv(4096)
            if not part:
                break
            response += part
        elapsed_time = time.time() - start_time
        print(response.decode(errors="ignore"))
        print(f"\nTime taken: {elapsed_time:.4f} seconds")
