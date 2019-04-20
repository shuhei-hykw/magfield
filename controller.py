#!/usr/bin/env python3

import serial
import binascii
import os
import sys
from time import sleep

module_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                           'module')
sys.path.append(module_path)
import mover_controller
import utility

mover = None

#______________________________________________________________________________
if __name__ == '__main__':
  utility.set_debug()
  mover = mover_controller.MoverController('/dev/tty.usbserial-A506MR1O')
  mover.device_info(0x00)
  mover.version(0x00)
  mover.set_manual(0x00)
  mover.servo_on(0x00)
  mover.servo_status(0x00)
  #mover.return_origin(0x00)
  mover.return_origin_status(0x00)
  mover.get_position(0x00)
  mover.set_speed(0x00, 50)
  mover.io_status(0x00)
  mover.set_parameter(0x00, 31, 100)
  mover.get_parameter(0x00, 31)
  # mover.reset_alarm(0x00)
  mover.get_alarm(0x00)
  # mover.inching(0x00, -20000)
