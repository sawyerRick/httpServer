import socket
import pprint

msg = b"""GET /blog/ HTTP/1.1\r\nHost: www.ruanyifeng.com\r\nProxy-Connection: keep-alive\r\nUpgrade-Insecure-Requests: 1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36\r\nAccept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8\r\nReferer: http://www.ruanyifeng.com/home.html\r\nAccept-Encoding: gzip, deflate\r\nAccept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\nCookie: _ga=GA1.2.721683548.1543559736; _gid=GA1.2.366491944.1543559736; Hm_lvt_f89e0235da0841927341497d774e7b15=1543564299; Hm_lpvt_f89e0235da0841927341497d774e7b15=1543565048; _gat=1\r\n\r\n"""
sock = socket.socket()
server_address = ('www.ruanyifeng.com', 80)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
try:
    # Send data
    print('sending {!r}'.format(msg))
    sock.sendall(msg)

    # Look for the response
    amount_received = 0
    amount_expected = len(msg)

    while amount_received < amount_expected:
        data = sock.recv(2048)
        amount_received += len(data)
        pprint.pprint('received {!r}'.format(data))

finally:
    print('closing socket')
    sock.close()