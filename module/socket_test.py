#!/usr/bin/env python3

import socket

HOST = '192.168.30.3'
PORT = 1234

if __name__ == '__main__':
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print(f'host = {HOST}')
    print(f'port = {PORT}')
    s.settimeout(0.5)
    try:
      s.connect((HOST, PORT))
      print('connected')
      while True:
        try:
          data = input('>> ')
        except (KeyboardInterrupt, EOFError) as e:
          print(e)
          break
        if data == 'q' :
          break
        if len(data) == 0:
          continue
        data += '\n'
        s.send(data.encode('utf-8'))
        data = s.recv(1024)
        print(data.decode('utf-8'))
      s.close()
    except (socket.error, socket.timeout):
      print('failed')
