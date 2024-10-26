##Proxy.py


import socket
import threading
import requests
from Cache import get_cached_response, cache_response
from Firewall import is_blocked

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode()
        print(f"Request received: {request}")  # Print the request
        url = request.split(' ')[1]

        if is_blocked(url):
            client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nBlocked by firewall.")
            client_socket.close()
            return

        cached_response = get_cached_response(url)
        if cached_response:
            print("Came from cache.")
            client_socket.sendall(cached_response)
        else:
            print("Fetching from web server.") ## send rerquest to web server
            try:
                response = requests.get(url)
                # HTTP response
                http_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
                http_response += response.headers.as_string() + "\r\n"
                http_response = http_response.encode() + response.content
                cache_response(url, http_response)  # Cache the response
                client_socket.sendall(http_response)
            except Exception as e:
                print(f"Error fetching from web server: {e}")
                client_socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\nError fetching response.")
        
        client_socket.close()
    except Exception as e:
        print(f"Error: {e}")
        client_socket.close()

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Proxy server running on {host}:{port}")
    
    while True:
        client_socket, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
start_server("localhost", 8080)
