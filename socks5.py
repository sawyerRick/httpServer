#coding=utf-8
import socket
import select
import socketserver
import logging
import json

logging.basicConfig(filename='logger.log', level=logging.DEBUG, format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S', filemode='a+')

#打开配置文件
with open('config.json', 'rb') as f:
    config = json.load(f)

port = int(config['port'])

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Socks5Server(socketserver.StreamRequestHandler):
    def handle_tcp(self, client, remote):
        try:
            fds = [client,remote]
            while True:
                r,w,e = select.select(fds,[],[],5)
                if client in r:
                    cli_data = client.recv(1024 * 100)
                    if len(cli_data) <= 0:
                        break
                    result = send_all(remote, cli_data)
                    if result < len(cli_data):
                       logging.warning("Failed pipping all data to target!!!")
                       break
                if remote in r:
                    remote_data = remote.recv(1024 * 100)
                    if len(remote_data) <= 0:
                        break
                    result = send_all(client, remote_data)
                    if result < len(remote_data):
                       logging.warning("Failed pipping all data to client!!!")
                       break
        except Exception as e:
            logging.error(e)
        finally:
            client.close()
            remote.close()


    def handle(self):
        client = self.request
        ver,methods = client.recv(1),client.recv(1)
        methods = client.recv(ord(methods))

        client.send(b'\x05\x00')

        ver,cmd,rsv,atype = client.recv(1),client.recv(1),client.recv(1),client.recv(1)
        if ord(cmd) is not 1:
            client.close()
            return

        # 判断是否支持atype，目前不支持IPv6
        # 比特流转化成整型 big表示编码为大端法，
        if ord(atype) == 1:
            # IPv4
            remote_addr = socket.inet_ntoa(client.recv(4))
            remote_port = int.from_bytes(client.recv(2), 'big')
        elif ord(atype) == 3:
            # 域名
            addr_len = int.from_bytes(client.recv(1), byteorder = 'big')
            remote_addr = client.recv(addr_len)
            remote_port = int.from_bytes(client.recv(2), byteorder = 'big')
        else:
            #不支持则关闭连接
            client.close()
            return
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info('[+] %s:%dConnect to --> %s:%d' % (self.client_address[0], self.client_address[1], remote_addr, remote_port))
        remote.connect((remote_addr, remote_port))

        reply = b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + (2222).to_bytes(2, byteorder = 'big')
        client.send(reply)

        self.handle_tcp(client,remote)

def send_all(sock, data):

    bytes_sent = 0
    while True:
        r = sock.send(data[bytes_sent:])
        if r < 0:
            return r
        bytes_sent += r
        if bytes_sent == len(data):
            return bytes_sent
try:
    server = ThreadingTCPServer(('', port), Socks5Server)
    logging.info('[+] Lintening on port:%d' % port)
    server.serve_forever()
except Exception as e:
    logging.error(e)