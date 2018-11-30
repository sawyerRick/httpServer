import select
import socket
import sys


# inputs = [server]
#
# readable, writeable, err = select.select(inputs,[],[])

def handle(client, remote):
    inputs = [client, remote]
    readable, writeable, err = select.select(inputs, [], [])
    if client in readable:
        cli_data = client.recv(2048 * 100)
        remote.send(cli_data)
        pass

    if remote in readable:
        remote_data = client.recv(2048 * 100)
        client.send(remote_data)
        pass
    # # 有新消息在inputs[]
    # for sock in readable:
    #     # 如果是新连接 server处理
    #     if sock is server:
    #         connection, addr = sock.accept()
    #         print("[+] new connections from %s " % addr)
    #         inputs.append(connection)
    #     # 已连接的socket，接收消息
    #     else:
    #         data = sock.recv()
    #         if data:
    #             print("[+] recv data : %s from %s" % (data, sock.getgetpeername()))
if __name__ == "__main__":
    server = socket.socket()
    server.setblocking(False)
    server_addr = ("127.0.0.1", 8080)
    server.bind(server_addr)
    print('starting up on {} port {}'.format(*server_addr), file=sys.stderr)

    # 只允许一个连接
    server.listen(1)
    client, addr = server.accept()
    while True:
        handle()
