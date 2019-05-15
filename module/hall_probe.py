#!/usr/bin/env python3

import socket
import numpy as np
import threading
import time

from . import param_manager
from . import socket_base
from . import utility

#______________________________________________________________________________
class HallProbeController():
  EOS = '\n'
  CHANNEL_LIST = ['x', 'y', 'z', 'v']

  #____________________________________________________________________________
  def __init__(self):
    host = param_manager.get('gpib_server_host')
    port = int(param_manager.get('gpib_server_port'))
    addr = int(param_manager.get('gpib_address'))
    self.thread_state = 'IDLE'
    self.socket = socket_base.SocketBase(host, port)
    if self.socket.is_open:
      utility.print_info('HPC  connect ' +
                         f'host = {host}, port = {port}, addr = {addr}')
      self.socket.send('f')
      idn = self.get_idn()
      if idn is None:
        utility.print_error(f'HPC  failed to connect GPIB device')
      else:
        utility.print_info(f'HPC  IDN = {idn}')
        self.set_address(addr)
        self.thread_state = 'RUNNING'
    else:
      utility.print_error('HPC  failed to connect ' +
                          f'host = {host}, port = {port}')
    self.field = dict()
    self.max_history = 4
    self.field_history = dict()
    for key in self.__class__.CHANNEL_LIST:
      self.field_history[key] = []
    self.field_dev = dict()
    self.dev_limit = float(param_manager.get('field_dev'))
    self.dev_status = False
    self.update()
    self.thread = threading.Thread(target=self.run_thread)
    self.thread.setDaemon(True)
    self.thread.start()

  #____________________________________________________________________________
  def get_address(self):
    return self.socket.send('++addr')

  #____________________________________________________________________________
  def get_idn(self):
    return self.socket.send('*idn?')

  #____________________________________________________________________________
  def set_address(self, address):
    self.socket.send(f'++addr {address}')

  #____________________________________________________________________________
  def run_thread(self):
    while self.thread_state == 'RUNNING':
      self.update()

  #____________________________________________________________________________
  def update(self):
    status = True
    for key in self.__class__.CHANNEL_LIST:
      self.socket.send(f'chnl {key}')
      val = self.socket.send('field?')
      if val is None:
        self.field[key] = (0, '')
        self.field_dev[key] = 0
        continue
      m = self.socket.send('fieldm?')
      u = self.socket.send('unit?')
      try:
        field = float(val)
      except (TypeError, ValueError):
        field = 0
      if field == 0:
        status = False
        continue
      self.field[key] = (field, m + u)
      if len(self.field_history[key]) == self.max_history:
        self.field_history[key].pop(0)
      self.field_history[key].append(field)
      dev = abs(np.std(self.field_history[key]) /
                np.mean(self.field_history[key]))
      self.field_dev[key] = dev
      if 'z' in key:
        if self.dev_limit < dev*100:
          status = False
      else:
        if self.dev_limit*10 < dev*100:
          status = False
    self.dev_status = status
