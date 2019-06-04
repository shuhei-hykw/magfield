#!/usr/bin/env python3

import serial
import numpy as np
import threading
import time

from . import param_manager
from . import utility

#______________________________________________________________________________
class RefProbeController():
  EOS = b'\r\n'

  #____________________________________________________________________________
  def __init__(self):
    device_name = param_manager.get('ref_device')
    self.thread_state = 'IDLE'
    try:
      self.device = serial.Serial(device_name,
                                  parity=serial.PARITY_ODD,
                                  baudrate=57600,
                                  timeout=1.0)
      utility.print_info(f'HPC  open serial device {device_name}')
      self.thread_state = 'RUNNING'
    except serial.serialutil.SerialException:
      self.device = None
      utility.print_error(f'HPC  failed to open {device_name}')
    self.field = 0
    self.max_history = 4
    self.field_history = []
    self.field_dev = 0
    self.status = True
    self.thread = threading.Thread(target=self.run_thread)
    self.thread.setDaemon(True)
    self.thread.start()

  #____________________________________________________________________________
  def send(self, data):
    data = data.encode('utf-8').rstrip(self.__class__.EOS)
    data += self.__class__.EOS
    try:
      self.device.write(data)
      ret = self.device.read_until(self.__class__.EOS)
      data = b''
      for d in ret:
        data += (d & 0x7f).to_bytes(1, 'big')
      decoded = data.decode()
      return decoded
    except serial.serialutil.SerialException:
      return b''

  #____________________________________________________________________________
  def get_idn(self):
    return self.send('*idn?')

  #____________________________________________________________________________
  def run_thread(self):
    while self.thread_state == 'RUNNING':
      self.update()

  #____________________________________________________________________________
  def update(self):
    val = self.send('rdgfield?')
    try:
      field = float(val)
    except (TypeError, ValueError):
      field = 0
      utility.print_warning(f'HPC  failed to read ref. field')
    self.status = (field != 0)
    if not self.status:
      return
    self.field = field
    # if len(self.field_history) == self.max_history:
    #   self.field_history.pop(0)
    #   self.field_history.append(field)
    # dev = abs(np.std(self.field_history) /
    #           np.mean(self.field_history))
    # self.field_dev = dev
