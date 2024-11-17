import socket
import threading
import requests
from Cache import get_cached_response, cache_response
from Firewall import is_blocked

# Dictionary to store E-Tags for each URL
etag_cache = {}

def handle_client(client_socket):
    try:
        # Receive the request from the client
        request = client_socket.recv(4096).decode()
        print(f"Request received: {request}")
        
        # Extract the URL and Host from the request
        try:
            request_line = request.split("\r\n")[0]
            method, path, _ = request_line.split(" ")
            host_header = next(
                (line for line in request.split("\r\n") if line.startswith("Host: ")), None
            )
            if host_header:
                host = host_header.split(" ")[1].strip()
            else:
                raise ValueError("Host header not found in the request.")
            
            # Reconstruct the full URL
            url = f"http://{host}{path}"
        except Exception as e:
            client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\nInvalid request format.")
            client_socket.close()
            return

        # Check if the URL is blocked by the firewall
        if is_blocked(url):
            client_socket.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\nBlocked by firewall.")
            client_socket.close()
            return

        # Check if the response is cached
        cached_response = get_cached_response(url)
        cached_etag = etag_cache.get(url)

        headers = {}
        if cached_etag:
            headers["If-None-Match"] = cached_etag  # Add E-Tag to headers for conditional request

        if cached_response:
            print("Serving from cache with E-Tag validation.")
            try:
                # Make a conditional request to the web server
                response = requests.get(url, headers=headers)

                if response.status_code == 304:
                    # Content has not changed; use the cached response
                    client_socket.sendall(cached_response)
                else:
                    # Content has changed; update cache and E-Tag
                    http_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
                    http_response += ''.join(f"{key}: {value}\r\n" for key, value in response.headers.items())
                    http_response += "\r\n"
                    #full_response = http_response.encode() + response.content
                    cache_response(url, full_response)
                    
                    # Update the E-Tag
                    etag_cache[url] = response.headers.get("ETag")
                    client_socket.sendall(full_response)
            except Exception as e:
                print(f"Error fetching from web server: {e}")
                client_socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\nError fetching response.")
        else:
            print("Fetching from web server.")
            try:
                # Fetch the resource from the web server
                response = requests.get(url)
                http_response = f"HTTP/1.1 {response.status_code} {response.reason}\r\n"
                http_response += ''.join(f"{key}: {value}\r\n" for key, value in response.headers.items())
                http_response += "\r\n"
                #full_response = http_response.encode() + response.content
                cache_response(url, full_response)
                
                # Store the E-Tag
                etag_cache[url] = response.headers.get("ETag")
                client_socket.sendall(full_response)
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
