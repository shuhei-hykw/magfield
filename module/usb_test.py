#!/usr/bin/env python3

import serial
import time

DEVICE = '/dev/ttyUSB1'
TERM = '\r\n'

if __name__ == '__main__':
  try:
    print(f'DEVICE = {DEVICE}')
    s = serial.Serial(DEVICE,
                      parity=serial.PARITY_ODD,
                      baudrate=57600,
                      timeout=0.5)
    print('connected')
    while True:
      try:
        data = input('>> ')
        # data = 'rdgfield?'
        # data = '*idn?'
      except (KeyboardInterrupt, EOFError) as e:
        print(e)
        break
      if data == 'q' :
        break
      if len(data) == 0:
        continue
      data += TERM
      s.write(data.encode('utf-8'))
      data = s.read_until(b'\r\x8a')
      if len(data) == 0:
        continue
      decoded = b''
      for d in data:
        print(f'{d:02x}', (d >> 7) & 0x1)
        # if ((d >> 7) & 0x80) == 1:
        #   decoded += ' '.encode()
        decoded += (d & 0x7f).to_bytes(1, 'big')
      print(decoded.decode())
    s.close()
  except serial.serialutil.SerialException:
    print('failed')
