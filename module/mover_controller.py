#!/usr/bin/env python3

import binascii
import serial
import time

from . import param_manager
from . import utility

#______________________________________________________________________________
class MoverController():
  DEVICE_LIST = {'x': None, 'y': None, 'z': None}
  START_MAGIC = b'\xef'
  END_MAGIC = b'\x0d\x0a'
  # not for alarm but for moving status
  DEVIATION_LIST = {'x': None, 'y': None, 'z': None}

  #____________________________________________________________________________
  def __init__(self, device_name, baudrate=115200, timeout=0.5):
    self.device_name = device_name
    try:
      utility.print_info(f'MVC  open serial device {device_name}')
      utility.print_info(f'MVC  - parity = {serial.PARITY_NONE}')
      utility.print_info(f'MVC  - baudrate = {baudrate}')
      utility.print_info(f'MVC  - timeout = {timeout}')
      self.device = serial.Serial(device_name,
                                  parity=serial.PARITY_NONE,
                                  baudrate=baudrate,
                                  timeout=timeout)
    except serial.serialutil.SerialException:
      self.device = None
    for i in ['x', 'y', 'z']:
      val = param_manager.get(f'device_id_{i}')
      if val is not None:
        self.__class__.DEVICE_LIST[i] = int(val)
      val = param_manager.get('deviation')
      self.__class__.DEVIATION_LIST[i] = int(val)

  #____________________________________________________________________________
  def __del__(self):
    # if self.servo_status(0x00) == 1:
    #   self.servo_off()
    if self.device is not None:
      self.device.close()

  #____________________________________________________________________________
  def __decode(self, line):
    linebytes = binascii.hexlify(line)
    response = linebytes[2:len(linebytes)-8] # except for start/end codes
    device_id = response[0:2]
    device_id = int(device_id, 16)
    cmd_no = response[2:4]
    cmd_no = int(cmd_no, 16)
    data = response[4:len(response)] # byte
    return device_id, cmd_no, data

  #____________________________________________________________________________
  def __get_bytes(self, device_id, cmd_no, data=None):
    device_id = device_id.to_bytes(1, 'big')
    cmd_no = cmd_no.to_bytes(1, 'big')
    ret = self.__class__.START_MAGIC + device_id + cmd_no
    if data is not None:
      ret += binascii.unhexlify(data)
    return ret + self.__get_crc(cmd_no, data) + self.__class__.END_MAGIC

  #____________________________________________________________________________
  def __get_crc(self, cmd_no, data=None):
    crc_data = cmd_no
    if data is not None:
      crc_data += binascii.unhexlify(data)
    ret_int = binascii.crc_hqx(crc_data, 0)
    ret = ret_int.to_bytes(2, 'big')
    return ret

  #____________________________________________________________________________
  def device_info(self, device_id):
    device_id, cmd_no, data = self.send(device_id, 0x01)
    model = int(data.decode()) if data is not None else -1
    if model == 0x1:
      utility.print_info(f'MVC  ID = {device_id} device info: model = TSC')
    elif model == 0x2:
      utility.print_info(f'MVC  ID = {device_id} device info: model = TLC')
    elif model == 0x3:
      utility.print_info(f'MVC  ID = {device_id} device info: model = THC')
    elif model == 0x8:
      utility.print_info(f'MVC  ID = {device_id} device info: model = TSC-T')
    else:
      utility.print_warning(f'MVC  ID = {device_id} device info: ' +
                            f'model = Unknown({model})')

  #____________________________________________________________________________
  def alarm_status(self, device_id):
    rdevice_id, cmd_no, data = self.send(device_id, 0x5b)
    if data is None or len(data) != 2:
      utility.print_warning(f'MVC  ID = {device_id} failed to read alarm status')
      return 0x100
    no = int(data, 16)
    no = 0x0 if no == 0xff else no
    if no != 0x0:
      utility.print_error(f'MVC  ID = {device_id} found alarm #{no}')
    return no

  #____________________________________________________________________________
  # def get_deviation(self, device_id):
  #   return self.get_parameter(device_id, 0x1e)

  #____________________________________________________________________________
  def get_manual_inching(self, device_id):
    return self.get_parameter(device_id, 0x1f)

  #____________________________________________________________________________
  def get_parameter(self, device_id, param_no):
    rdevice_id, cmd_no, data = self.send(device_id, 0x24,
                                         str(param_no.to_bytes(2, 'little').hex()))
    if data is None or len(data) != 12:
      return 0
    no = int(data[:4], 16).to_bytes(2, 'little')
    no = int.from_bytes(no, 'big')
    val = int(data[4:], 16).to_bytes(4, 'little')
    val = int.from_bytes(val, 'big', signed=True)
    if param_no != no:
      utility.print_debug(f'MVC  ID = {device_id} ' +
                          f'invalid param#{no} returned: {val} ' +
                          f'({param_no}/{no})')
      return self.get_parameter(device_id, param_no)
    return val

  #____________________________________________________________________________
  def get_position(self, device_id):
    device_id, cmd_no, data = self.send(device_id, 0x17)
    if data is None or len(data) != 16:
      return -999999., -999999.
    vmon = int(data[:8], 16).to_bytes(4, 'little')
    vmon = int.from_bytes(vmon, 'big', signed=True)
    vset = int(data[8:], 16).to_bytes(4, 'little')
    vset = int.from_bytes(vset, 'big', signed=True)
    utility.print_debug(f'MVC  ID = {device_id} position: ' +
                        f'{int(data, 16):16x} ... {vmon:08x}  {vset:08x}')
    return vmon * 1e-4, vset * 1e-4

  #____________________________________________________________________________
  def get_speed(self, device_id):
    return self.get_parameter(device_id, 0x10)

  #____________________________________________________________________________
  def go_to(self, device_id, val):
    vmon, vset = self.get_position(device_id)
    if vmon == -999999. or vset == -999999:
      return False
    dist = val - vset
    self.set_manual_inching(device_id, int(dist*1000), False)
    if dist > 0:
      self.inching_up(device_id)
    else:
      self.inching_down(device_id)
    return True

  #____________________________________________________________________________
  def inching_down(self, device_id):
    ''' [um] '''
    device_id, cmd_no, data = self.send(device_id, 0x11, '02')
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x1:
      return status
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed to process inching down')
      return status

  #____________________________________________________________________________
  def inching_up(self, device_id):
    ''' [um] '''
    device_id, cmd_no, data = self.send(device_id, 0x11, '01')
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x1:
      return status
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed to process inching up')
      return status

  #____________________________________________________________________________
  def io_status(self, device_id):
    rdevice_id, rcmd_no, data = self.send(device_id, 0x19)
    if data is None or len(data) != 8:
      utility.print_error(f'MVC  ID = {device_id} failed to read I/O status')
      return None
    in_status = int(data[:4], 16).to_bytes(2, 'little')
    in_status = int.from_bytes(in_status, 'big')
    out_status = int(data[4:], 16).to_bytes(2, 'little')
    out_status = int.from_bytes(out_status, 'big')
    utility.print_debug(f'MVC  ID = {rdevice_id} io status: {int(data, 16):08x}'
                        f'... {in_status:04x} {out_status:04x}')
    move = (out_status >> 6) & 0x1
    svrdy = (out_status >> 13) & 0x1
    alm = (out_status >> 15) & 0x1
    utility.print_debug(f'MVC  ID = {rdevice_id} MOVE={move} ' +
                        f'SVRDY={svrdy} ALM={alm}')
    return out_status

  #____________________________________________________________________________
  def print_parameter(self, device_id):
    for key, val in self.__class__.DEVICE_LIST.items():
      if val == device_id:
        utility.print_info(f'MVC  ID = {device_id} param#-- deviation limit for' +
                           f' status = {self.__class__.DEVIATION_LIST[key]} [um]')
    utility.print_info(f'MVC  ID = {device_id} param#01 area max = ' +
                       f'{self.get_parameter(device_id, 1)*1e-4} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#02 area min = ' +
                       f'{self.get_parameter(device_id, 2)*1e-4} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#03 soft max = ' +
                       f'{self.get_parameter(device_id, 3)*1e-4} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#04 soft min = ' +
                       f'{self.get_parameter(device_id, 4)*1e-4} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#06 zero offset = ' +
                       f'{self.get_parameter(device_id, 6)*1e-4} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#16 speed = ' +
                       f'{self.get_speed(device_id)} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#30 deviation limit for'
                       f' alarm = {self.get_parameter(device_id, 30)} [mm]')
    utility.print_info(f'MVC  ID = {device_id} param#31 inching = ' +
                       f'{self.get_manual_inching(device_id)*1e-3} [mm]')

  #____________________________________________________________________________
  def reset_alarm(self, device_id):
    device_id, cmd_no, data = self.send(device_id, 0x5c)
    no = -1 if data is None or len(data) == 0 else int(data, 16)
    if no == 0x1:
      time.sleep(0.2)
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed to reset alarm')

  #____________________________________________________________________________
  def send(self, device_id, cmd_no, data=None):
    send = self.__get_bytes(device_id, cmd_no, data)
    vout = (f'ID: {device_id:2x}  CMD: {cmd_no:2x}  ' +
            f'DATA: {"--" if data is None else data}')
    utility.print_debug(f"MVC  ID = {device_id} W -->  " + vout)
    self.device.write(send)
    ret = self.device.read_until(terminator=self.__class__.END_MAGIC)
    if len(ret) == 0:
      utility.print_warning(f'MVC  ID = {device_id} device timeout')
      return None, None, None
    rdevice_id, rcmd_no, rdata = self.__decode(ret)
    if rdevice_id != device_id or rcmd_no != cmd_no:
      utility.print_error(f'MVC  ID = {device_id} return invalid data  ' +
                          f'ID: {rdevice_id:2x}' +
                          f'  CMD: {rcmd_no:2x}' +
                          f'  DATA: {rdata.decode()}')
    utility.print_debug(f'MVC  ID = {device_id} R <--  ' +
                        f'ID: {rdevice_id:2x}' +
                        f'  CMD: {rcmd_no:2x}' +
                        f'  DATA: {rdata.decode()}')
    return rdevice_id, rcmd_no, rdata

  #____________________________________________________________________________
  def servo_off(self, device_id):
    utility.print_info(f'MVC  ID = {device_id} servo off')
    rdevice_id, cmd_no, data = self.send(device_id, 0x0c)
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x1:
      time.sleep(2)
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed turn servo off')

  #____________________________________________________________________________
  def servo_on(self, device_id):
    utility.print_info(f'MVC  ID = {device_id} servo on')
    rdevice_id, cmd_no, data = self.send(device_id, 0x0b)
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x1:
      time.sleep(2)
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed turn servo on')

  #____________________________________________________________________________
  def servo_status(self, device_id):
    rdevice_id, cmd_no, data = self.send(device_id, 0x15)
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x0 or status == 0x1:
      return status
    else:
      utility.print_error(f'MVC  ID = {device_id} unknown servo status = {status}')
      return status

  #____________________________________________________________________________
  def set_manual(self, device_id):
    rdevice_id, rcmd_no, rdata = self.send(device_id, 0x70, '01')
    if rdata != b'01':
      utility.print_error(f'MVC  ID = {device_id} failed to set manual mode')
      return False
    utility.print_info(f'MVC  ID = {device_id} set_manual mode')
    return True

  #____________________________________________________________________________
  def set_manual_inching(self, device_id, inching, verbose=True):
    if verbose:
      utility.print_info(f'MVC  ID = {device_id} set manual inching: {inching/1000} [mm]')
    distance = abs(inching) # [um]
    self.set_parameter(device_id, 0x1f, distance)

  #____________________________________________________________________________
  def set_parameter(self, device_id, param_no, val):
    data = str((param_no.to_bytes(2, 'little') + val.to_bytes(4, 'little')).hex())
    rdevice_id, cmd_no, data = self.send(device_id, 0x25, data)
    status = int(data, 16) if data is not None and len(data) != 0 else 0x100
    if status != 0x1:
      utility.print_error(f'MVC  ID = {device_id} failed to set parameter' +
                          f'#{param_no}, val = {val}')

  #____________________________________________________________________________
  def set_speed(self, device_id, speed):
    utility.print_info(f'MVC  ID = {device_id} set speed: {speed} [mm/s]')
    ''' [mm/s] '''
    self.set_parameter(device_id, 0x10, abs(speed))

  #____________________________________________________________________________
  def stop(self, device_id):
    rdevice_id, cmd_no, data = self.send(device_id, 0x0f)
    status = 0x0 if data is None or len(data) != 2 else int(data, 16)
    if status == 0x1:
      return status
    else:
      utility.print_warning(f'MVC  ID = {device_id} failed to stop moving')
      return status

  #____________________________________________________________________________
  def version(self, device_id):
    device_id, cmd_no, data = self.send(device_id, 0x04)
    if data is None or len(data) != 40:
      utility.print_error(f'MVC  ID = {device_id} failed to get version')
      return
    ver = int(data[:8], 16).to_bytes(4, 'big').decode()
    comment = int(data[8:], 16).to_bytes(16, 'big').decode()
    utility.print_info(f'MVC  ID = {device_id} ' +
                       f'version = {ver[0]}.{ver[1]}.{ver[2]}.{ver[3]}')
    utility.print_info(f'MVC  ID = {device_id} ' +
                       f'comment = {comment}')

  #____________________________________________________________________________
  def zero_return(self, device_id):
    utility.print_info(f'MVC  ID = {device_id} zero return')
    self.send(device_id, 0x0d, '01')

  #____________________________________________________________________________
  def zero_return_status(self, device_id):
    device_id, cmd_no, data = self.send(device_id, 0x16)
    status = 0x100 if data is None or len(data) != 2 else int(data, 16)
    if status != 0x0 and status != 0x1 and status != 0x100:
      utility.print_error(f'MVC  ID = {device_id} ' +
                          f'unknown zero return status = {status}')
    return status
