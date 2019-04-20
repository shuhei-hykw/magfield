#!/usr/bin/env python3

import serial
import binascii
import os
import sys
import tkinter

module_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                           'module')
sys.path.append(module_path)
import mover_controller
import utility

mover = None

#______________________________________________________________________________
class Controller(tkinter.Frame):

  #____________________________________________________________________________
  def __init__(self):
    tkinter.Frame.__init__(self)
    self.master.title(f'Field Mapping Controller (pid={os.getpid()})')
    self.master.resizable(0, 0)
    # self.pack(fill=tkinter.Y, expand=True)
    self.__make_menu()
    self.__make_label()

  #____________________________________________________________________________
  def __del__(self):
    pass

  #____________________________________________________________________________
  def __make_label(self):
    font = ('Helvetica', -24, 'bold')
    self.label = tkinter.Label(self, text='DAQ: Idle',
                               bg='black', fg='blue', font=font)
    self.label.pack(side=tkinter.TOP, fill=tkinter.X)
    flabels = tkinter.Frame(self)
    flabels.pack(side=tkinter.TOP, fill=tkinter.X, padx=100)
    self.lasttime = tkinter.Label(flabels, text='Last Run Start Time:')
    self.lasttime.pack(side=tkinter.LEFT, pady=10)
    self.disklink = tkinter.Label(flabels, text='Data Storage Path:')
    self.disklink.pack(side=tkinter.RIGHT, pady=10)


  #____________________________________________________________________________
  def __make_menu(self):
    menubar = tkinter.Menu(self)
    self.master.config(menu=menubar)
    self.menu1 = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Control', menu=self.menu1)
    self.menu1.add_command(label='Quit', command=self.master.quit)

  #____________________________________________________________________________
  def updater(self):
    self.after(500, self.updater)

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
  app = Controller()
  app.updater()
  app.mainloop()
