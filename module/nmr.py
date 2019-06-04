#!/usr/bin/env python3

import socket
import numpy as np
import threading
import time

from . import param_manager
from . import socket_base
from . import utility

#______________________________________________________________________________
class NMRController():
  EOS = '\n'

  #____________________________________________________________________________
  def __init__(self):
    host = param_manager.get('nmr_server_host')
    port = int(param_manager.get('nmr_server_port'))
    self.thread_state = 'IDLE'
    self.socket = socket_base.SocketBase(host, port)
    if self.socket.is_open:
      utility.print_info('NMR  connect ' +
                         f'host = {host}, port = {port}')
      self.thread_state = 'RUNNING'
    else:
      utility.print_error('NMR  failed to connect ' +
                          f'host = {host}, port = {port}')
    self.hold = False
    self.prev = 0.0
    self.field = 0.0
    self.thread = threading.Thread(target=self.run_thread)
    self.thread.setDaemon(True)
    self.thread.start()

  #____________________________________________________________________________
  def run_thread(self):
    while self.thread_state == 'RUNNING':
      self.update()
      time.sleep(0.5)

  #____________________________________________________________________________
  def update(self):
    val = self.socket.send('n')
    if val == '0000000':
      self.hold = False
      now = time.time()
      if 30 < now - self.prev:
        utility.print_warning('NMR  signal is undetectable')
        self.prev = now
    else:
      self.hold = True
    self.field = float(val)*1e-6
