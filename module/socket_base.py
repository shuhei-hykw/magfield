#!/usr/bin/env python3

import socket
import time

from . import socket_base

#______________________________________________________________________________
class SocketBase():
  EOS = '\n'

  #____________________________________________________________________________
  def __init__(self, host, port, timeout=1.0):
    self.host = host
    self.port = port
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.settimeout(timeout)
    try:
      self.socket.connect((self.host, self.port))
      self.is_open = True
    except socket.error:
      self.is_open = False

  #____________________________________________________________________________
  def __del__(self):
    if self.is_open:
      self.socket.close()

  #____________________________________________________________________________
  def recv(self, buflen=1024):
    return self.socket.recv(buflen).decode('utf-8')

  #____________________________________________________________________________
  def send(self, data):
    data += self.__class__.EOS
    try:
      self.socket.send(data.encode('utf-8'))
      return self.recv().rstrip()
    except (socket.error, socket.timeout):
      return None
