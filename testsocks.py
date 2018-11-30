import socket
import pprint

sock = socket.socket()
server_address = ('127.0.0.1', 8080)
sock.bind(server_address)
sock.listen(1)
while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(2048)
            print("recv:%s" % data)
            # if data:
            #     print('sending data back to the client')
            #     connection.sendall(data)
            # else:
            #     print('no data from', client_address)
            #     break

    finally:
        # Clean up the connection
        connection.close()