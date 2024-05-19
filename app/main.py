# Uncomment this to pass the first stage
import socket
import argparse
import os
import sys
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

# return the HTTP response for given path
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

    # default response if path not found
    default_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return default_response

        

def handle_request(client_socket, directory):
    try:
        # Read data from the client
        request_data = client_socket.recv(1024).decode()
        method, path, version, headers = parse_request(request_data)

        # Get the response based on the request path
        response = get_response(path, headers, directory)
        
        # Send the response to the client
        if isinstance(response, str):
            response = response.encode()
        client_socket.send(response)

    except Exception as e:
        print(f"Error occurred while handling request: {e}")

    finally:
        # Close the connection to the client
        client_socket.close()

def main():
    parser = argparse.ArgumentParser(description="Simple HTTP server.")
    parser.add_argument('--directory', required=True, help="Directory to serve files from")
    args = parser.parse_args()

    directory = args.directory

    # Ensure the provided directory exists
    if not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        sys.exit(1)


    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("server is running on port 4221")

    try:
        while True:
            print("waiting for connection")
            client_socket, addr = server_socket.accept() # wait for client

            print(f"connection from {addr} has been eshtablished.")

             # Handle the client request in a new thread
            thread = threading.Thread(target=handle_request, args=(client_socket, directory))
            thread.start()

            # close the connection to the client
            client_socket.close()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("server has been shut down.")


if __name__ == "__main__":
    main()
