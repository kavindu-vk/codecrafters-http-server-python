# Uncomment this to pass the first stage
import socket

def parse_request(request_data):
    lines = request_data.split('\r\n')
    start_line = lines[0]
    method, path, version = start_line.split(' ')
    return method, path, version

# return the HTTP response for given path
def get_response(path):
    response = {
        "/": "HTTP/1.1 200 OK\r\n\r\n",
    }

    # default response if path not found
    default_response = "HTTP/1.1 404 Not Found\r\n\r\n"

    return response.get(path, default_response)

def handle_request(client_socket):
    # Read data from the client
    request_data = client_socket.recv(1024).decode() #Reading a bit of data
    method, path, version = parse_request(request_data)

    # send a 200 OK response
    response = get_response(path)
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
