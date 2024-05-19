import socket
import sys
import os
import argparse
import threading

def parse_request(request_data):
    lines = request_data.split('\r\n')
    start_line = lines[0]
    method, path, version = start_line.split(' ')

    headers = {}
    for line in lines[1:]:
        if line == '':
            break
        key, value = line.split(': ', 1)
        headers[key] = value
        
    return method, path, version, headers

def get_response(path, headers, directory):
    if path.startswith("/echo/"):
        echo_str = path[len('/echo/'):]
        response_body = echo_str
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            f"{response_body}"
        )
        return response
    
    if path == '/user-agent':
        user_agent = headers.get("User-Agent", "Unknown")
        response_body = user_agent
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            f"{response_body}"
        )
        return response
    
    if path.startswith("/files/"):
        filename = path[len('/files/'):]
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                response_body = f.read()
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/octet-stream\r\n"
                f"Content-Length: {len(response_body)}\r\n"
                "\r\n"
            ).encode() + response_body
            return response
        return "HTTP/1.1 404 Not Found\r\n\r\n"
    
    if path == "/":
        response_body = "Welcome to the HTTP server!"
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            f"{response_body}"
        )
        return response

    default_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return default_response

def handle_request(client_socket, directory):
    try:
        request_data = client_socket.recv(1024).decode()
        method, path, version, headers = parse_request(request_data)
        response = get_response(path, headers, directory)
        client_socket.send(response if isinstance(response, bytes) else response.encode())
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def main():
    parser = argparse.ArgumentParser(description='Simple HTTP server')
    parser.add_argument('--directory', required=True, help='Directory to serve files from')
    args = parser.parse_args()

    global base_directory
    base_directory = args.directory

    if not os.path.isdir(base_directory):
        print(f"Error: Directory '{base_directory}' does not exist.")
        sys.exit(1)

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221))
    print("server is running on port 4221")

    try:
        while True:
            print("waiting for connection")
            client_socket, addr = server_socket.accept()
            print(f"connection from {addr} has been established.")
            client_thread = threading.Thread(target=handle_request, args=(client_socket, base_directory))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("server has been shut down.")

if __name__ == "__main__":
    main()
