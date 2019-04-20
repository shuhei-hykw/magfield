#!/usr/bin/env python3

import binascii
import serial
import time

import utility

#______________________________________________________________________________
class MoverController():
  START_MAGIC = b'\xef'
  END_MAGIC = b'\x0d\x0a'

  #____________________________________________________________________________
  def __init__(self, device_name, baudrate=115200, timeout=3.0):
    self.device_name = device_name
    self.device = serial.Serial(device_name,
                                parity=serial.PARITY_NONE,
                                baudrate=baudrate,
                                timeout=timeout)

  #____________________________________________________________________________
  def __del__(self):
    # self.servo_off(0x00)
    self.device.close()

  #____________________________________________________________________________
  def __get_bytes(self, device_id, cmd_no, data=None):
    device_id = device_id.to_bytes(1, 'big')
    cmd_no = cmd_no.to_bytes(1, 'big')
    ret = (self.__class__.START_MAGIC + device_id + cmd_no)
    if data is None:
      pass
    elif type(data) is str:
      ret += binascii.unhexlify(data)
    elif type(data) is bytes:
      ret += data
    else:
      utility.print_error(f'unknown data type = {type(data)}')
    ret += self.__get_crc(cmd_no, data) + self.__class__.END_MAGIC
    return ret

  #____________________________________________________________________________
  def __get_crc(self, cmd_no, data=None):
    crc_data = cmd_no
    if data is None:
      pass
    elif type(data) is str:
      crc_data += binascii.unhexlify(data)
    elif type(data) is bytes:
      crc_data += data
    else:
      utility.print_error(f'unknown data type = {type(data)}')
    ret_int = binascii.crc_hqx(crc_data, 0)
    ret = ret_int.to_bytes(2,'big')
    return ret

  #____________________________________________________________________________
  def __decode(self, line):
    linebytes = binascii.hexlify(line)
    response = linebytes[2:len(linebytes)-8] # except for start/end codes
    device_id = int(response[0:2], 16)
    cmd_no = int(response[2:4], 16)
    data = response[4:len(response)]
    return device_id, cmd_no, data

  #____________________________________________________________________________
  def device_info(self, device_id):
    utility.print_info(f'device_info()')
    device_id, cmd_no, data = self.send(device_id, 0x01)
    model = int(data.decode())
    if model == 0x1:
      utility.print_info(f'device id = {device_id}, model = TSC')
    elif model == 0x2:
      utility.print_info(f'device id = {device_id}, model = TLC')
    elif model == 0x3:
      utility.print_info(f'device id = {device_id}, model = THC')
    elif model == 0x8:
      utility.print_info(f'device id = {device_id}, model = TSC-T')
    else:
      utility.print_warning(f'unknown device model = {model}')

  #____________________________________________________________________________
  def get_alarm(self, device_id):
    utility.print_info(f'get_alarm()')
    device_id, cmd_no, data = self.send(device_id, 0x5b)
    no = int(data, 16)
    if no != 0xff:
      utility.print_error(f'found alarm #{no}')

  #____________________________________________________________________________
  def get_parameter(self, device_id, param_no):
    utility.print_info(f'get_parameter()')
    device_id, cmd_no, data = self.send(device_id, 0x24,
                                        param_no.to_bytes(2, 'little'))
    no = int(data[:4], 16).to_bytes(2, 'little')
    no = int.from_bytes(no, 'big')
    val = int(data[4:], 16).to_bytes(4, 'little')
    val = int.from_bytes(val, 'big')
    if param_no != no:
      utility.print_error(f'invalid param no returned = {no}/{param_no}')
    utility.print_info(f'param no = 0x{no:x}, val = 0x{val:x}')

  #____________________________________________________________________________
  def get_position(self, device_id):
    utility.print_info(f'get_position()')
    device_id, cmd_no, data = self.send(device_id, 0x17)
    cur = int(data[:8], 16)
    cmd = int(data[8:], 16)
    print(f'{data} ... {cur:08x}  {cmd:08x}')

  #____________________________________________________________________________
  def inching(self, device_id, displacement):
    ''' [0.1um] '''
    distance = abs(displacement)
    self.set_parameter(0x00, 31, distance)
    if displacement > 0:
      self.send(device_id, 0x11, '01')
    else:
      self.send(device_id, 0x11, '02')

  #____________________________________________________________________________
  def io_status(self, device_id):
    utility.print_info('io_status()')
    device_id, cmd_no, data = self.send(device_id, 0x19)
    in_status = int(data[:4], 16)
    out_status = int(data[4:], 16)
    print(f'{data} ... {in_status:04x} {out_status:04x}')
    # status = 'OFF' if data == 0x0 else 'ON' if data == 0x1 else 'UNKNOWN'
    # utility.print_info(f'servo status = {status}')

  #____________________________________________________________________________
  def reset_alarm(self, device_id):
    utility.print_info(f'reset_alarm()')
    device_id, cmd_no, data = self.send(device_id, 0x5c)
    no = int(data, 16)
    if no == 0x0:
      utility.print_warning('failed to reset alarm')
    elif no == 0x1:
      utility.print_info('reset alarm')
      time.sleep(1)
    else:
      utility.print_error(f'unknown status = {data}')

  #____________________________________________________________________________
  def return_origin(self, device_id):
    utility.print_info('return origin()')
    self.send(device_id, 0x0d, '01')

  #____________________________________________________________________________
  def return_origin_status(self, device_id):
    utility.print_info('return origin status()')
    device_id, cmd_no, data = self.send(device_id, 0x16)
    status = int(data, 16)
    status = 'YET' if status == 0x0 else 'DONE' if status == 0x1 else 'UNKNOWN'
    utility.print_info(f'return origin status = {status}')

  #____________________________________________________________________________
  def send(self, device_id, cmd_no, data=None):
    send = self.__get_bytes(device_id, cmd_no, data)
    if type(data) is str:
      data = binascii.unhexlify(data)
    vout = (f'ID: 0x{device_id:02x}  CMD: 0x{cmd_no:02x}  ' +
            f'DATA: {"0x" + data.hex() if data is not None else data}')
    utility.print_debug("W -->  " + vout)
    self.device.write(send)
    ret = self.device.readline()
    if len(ret) == 0:
      utility.print_warning('device read timeout')
      return None, None, None
    else:
      device_id, cmd_no, data = self.__decode(ret)
      utility.print_debug(f'R <--  ID: 0x{device_id:02x}  CMD: 0x{cmd_no:02x}' +
                          f'  DATA: 0x{data.decode()}')
      return device_id, cmd_no, data

  #____________________________________________________________________________
  def servo_off(self, device_id):
    utility.print_info('servo_off()')
    device_id, cmd_no, data = self.send(device_id, 0x0c)
    status = int(data, 16)
    if status == 0x0:
      utility.print_warning('failed turn servo off')
    elif status == 0x1:
      utility.print_info('turn servo off')
      time.sleep(3)
    else:
      utility.print_error(f'unknown status = {data}')

  #____________________________________________________________________________
  def servo_on(self, device_id):
    utility.print_info('servo_on()')
    device_id, cmd_no, data = self.send(device_id, 0x0b)
    status = int(data, 16)
    if status == 0x0:
      utility.print_warning('failed turn servo on')
    elif status == 0x1:
      utility.print_info('turn servo on')
      time.sleep(3)
    else:
      utility.print_error(f'unknown status = {data}')

  #____________________________________________________________________________
  def servo_status(self, device_id):
    utility.print_info('servo_status()')
    device_id, cmd_no, data = self.send(device_id, 0x15)
    status = int(data, 16)
    status = 'OFF' if status == 0x0 else 'ON' if status == 0x1 else 'UNKNOWN'
    utility.print_info(f'servo status = {status}')

  #____________________________________________________________________________
  def set_manual(self, device_id):
    utility.print_info('set_manual()')
    device_id, cmd_no, data = self.send(device_id, 0x70, '01')
    if data == 0x0:
      utility.print_error('failed to set manual')

  #____________________________________________________________________________
  def set_parameter(self, device_id, param_no, val):
    utility.print_info(f'set_parameter()')
    data = param_no.to_bytes(2, 'little') + val.to_bytes(4, 'little')
    device_id, cmd_no, data = self.send(device_id, 0x25, data)
    if data == 0x0:
      utility.print_error('failed to set parameter : ' +
                          f'param_no = {param_no}, val = {val}')

  #____________________________________________________________________________
  def set_speed(self, device_id, speed):
    utility.print_info(f'set_speed()')
    ''' [mm/s] '''
    self.send(device_id, 0x25, '1000' + speed.to_bytes(4, 'little').hex())

  #____________________________________________________________________________
  def version(self, device_id):
    utility.print_info('version()')
    device_id, cmd_no, data = self.send(device_id, 0x04)
    ver = int(data[:8], 16).to_bytes(4, 'big').decode()
    comment = int(data[8:], 16).to_bytes(16, 'big').decode()
    utility.print_info(f'version = {ver[0]}.{ver[1]}.{ver[2]}.{ver[3]}')
    utility.print_info(f'comment = {comment}')
