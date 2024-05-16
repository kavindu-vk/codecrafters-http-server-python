# Uncomment this to pass the first stage
import socket

def handle_request(client_socket):
    # Read data from the client
    client_socket.recv(1024) #Reading a bit of data

    # send a 200 OK response
    response = "HTTP/1.1 200 OK\r\n\r\n"
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
