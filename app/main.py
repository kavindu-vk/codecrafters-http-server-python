import socket
import sys
import os
import argparse
import threading
import gzip
from io import BytesIO

def parse_request(request_data):
    headers_part, body = request_data.split('\r\n\r\n', 1)
    lines = headers_part.split('\r\n')
    start_line = lines[0]
    method, path, version = start_line.split(' ')

    headers_dict = {}
    for line in lines[1:]:
        if ': ' in line:
            key, value = line.split(': ', 1)
            headers_dict[key.lower()] = value  # Use lowercase for case-insensitive comparison

    return method, path, version, headers_dict, body

def save_file(path, body, directory):
    filename = path[len('/files/'):]
    file_path = os.path.join(directory, filename)
    with open(file_path, 'wb') as f:
        f.write(body.encode())
    response = (
        "HTTP/1.1 201 Created\r\n"
        "Content-Type: text/plain\r\n"
        "Content-Length: 0\r\n"
        "\r\n"
    )
    return response

def gzip_compress(data):
    buf = BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb') as f:
        f.write(data.encode())
    return buf.getvalue()

def get_response(method, path, headers, body, directory):
    if method == "POST" and path.startswith("/files/"):
        return save_file(path, body, directory)
    
    if path.startswith("/echo/"):
        echo_str = path[len('/echo/'):]
        response_body = echo_str
        content_encoding = ""
        if "accept-encoding" in headers and "gzip" in headers["accept-encoding"]:
            response_body = gzip_compress(response_body)
            content_encoding = "Content-Encoding: gzip\r\n"
        
        response = (
            "HTTP/1.1 200 OK\r\n"
            f"{content_encoding}"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
        )
        if isinstance(response_body, bytes):
            response = response.encode() + response_body
        else:
            response += response_body
        return response
    
    if path == '/user-agent':
        user_agent = headers.get("user-agent", "Unknown")
        response_body = user_agent
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
            f"{response_body}"
        )
        return response
    
    if path.startswith("/files/") and method == "GET":
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
        method, path, version, headers, body = parse_request(request_data)
        response = get_response(method, path, headers, body, directory)
        client_socket.send(response if isinstance(response, bytes) else response.encode())
    except Exception as e:
        print(f"Error handling request: {e}")
    finally:
        client_socket.close()

def main():
    parser = argparse.ArgumentParser(description='Simple HTTP server')
    parser.add_argument('--directory', type=str, help='Directory to serve files from')
    args = parser.parse_args()

    directory = args.directory

    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221))
    print("server is running on port 4221")

    try:
        while True:
            print("waiting for connection")
            client_socket, addr = server_socket.accept()
            print(f"connection from {addr} has been established.")
            client_thread = threading.Thread(target=handle_request, args=(client_socket, directory))
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("server has been shut down.")

if __name__ == "__main__":
    main()
