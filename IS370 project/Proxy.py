import socket
import threading
from Cache import get_cached_response, cache_response
from Firewall import is_blocked

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode()
        url = request.split(' ')[1]

        if is_blocked(url):
            client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nBlocked by firewall.")
            client_socket.close()
            return

        cached_response = get_cached_response(url)
        if cached_response:
            client_socket.sendall(cached_response)
        else:
            # Handle forwarding request to web server and caching (not fully implemented here)
            response = b"HTTP response from web server"  # Placeholder for actual response
            cache_response(url, response)
            client_socket.sendall(response)
        
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
