# select_echo_server.py

import select
import socket
import sys
import queue

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(False)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on {} port {}'.format(*server_address),file=sys.stderr)
server.bind(server_address)

# Listen for incoming connections
# 维持五个socket连接
server.listen(5)

# Sockets from which we expect to read
inputs = [server]

# Sockets to which we expect to write
outputs = []

# Outgoing message queues (socket:Queue)
# 读写消息队列字典，(socket:Queue) 对应的socket有着对应的队列类型的msg
message_queues = {}

print('waiting for the next event', file=sys.stderr)
# 三个sockets列表，对应可读socket(有新消息), 可写socket(可以发送新消息), 出错socket 用for s in readable来遍历可读socket
# readable:All of the sockets in the readable list have incoming data buffered and available to be read
# writable:All of the sockets in the writable list have free space in their buffer and can be written to
readable, writable, exceptional = select.select(inputs,
                                                outputs,
                                                inputs)

# 如果可读，从sock读数据
for s in readable:

      # Server端sock把新连接socket加入input
      if s is server:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            print('  connection from', client_address,
                  file=sys.stderr)
            connection.setblocking(0)
            inputs.append(connection)

            # Give the connection a queue for data
            # we want to send
            # 新建消息队列给新连的会话socket
            message_queues[connection] = queue.Queue()


      # 新的子连接端socket,读内容
      else:
            data = s.recv(1024)
            if data:
                  # A readable client socket has data
                  # getpeername获取(host, port)
                  print('  received {!r} from {}'.format(
                        data, s.getpeername()), file=sys.stderr,
                  )
                  # msg入队(对应socket)
                  message_queues[s].put(data)
                  # Add output channel for response
                  if s not in outputs:
                        outputs.append(s)


# 如果sock可写，把对应msg发送到sock
for s in writable:
      try:
            # 非阻塞出队
            next_msg = message_queues[s].get_nowait()
      except queue.Empty:
      # No messages waiting so stop checking
      # for writability.
            print('  ', s.getpeername(), 'queue empty',
                  file=sys.stderr)
            outputs.remove(s)
      else:
            print('  sending {!r} to {}'.format(next_msg,
                                                s.getpeername()),
                  file=sys.stderr)
            s.send(next_msg)

# 如果socket出错关闭
for s in exceptional:
        print('exception condition on', s.getpeername(),
              file=sys.stderr)
        # Stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()

        # Remove message queue
        del message_queues[s]

