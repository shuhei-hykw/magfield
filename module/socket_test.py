#!/usr/bin/env python3

import socket

if __name__ == '__main__':
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('192.168.2.9', 1234))
    print('connected')
    while True:
      data = input('>> ')
      if data == "q" :
        break
      if len(data) == 0:
        continue
      data += '\n'
      s.send(data.encode("UTF-8"))
      data = s.recv(1024)
      print(data.decode('utf-8'))
    s.close()
