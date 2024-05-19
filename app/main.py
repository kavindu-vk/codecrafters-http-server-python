# Uncomment this to pass the first stage
import socket

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
def get_response(path, headers):
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

        

def handle_request(client_socket):
    # Read data from the client
    request_data = client_socket.recv(1024).decode() #Reading a bit of data
    method, path, version, headers = parse_request(request_data)

    # send a 200 OK response
    response = get_response(path, headers)
    client_socket.send(response.encode())

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221))
    print("server is running on port 4221")

    try:
        while True:
            print("waiting for connection")
            client_socket, addr = server_socket.accept() # wait for client

            print(f"connection from {addr} has been eshtablished.")

            # handle the client request
            handle_request(client_socket)

            # close the connection to the client
            client_socket.close()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        server_socket.close()
        print("server has been shut down.")


if __name__ == "__main__":
    main()
