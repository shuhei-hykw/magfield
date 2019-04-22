#!/usr/bin/env python3

import argparse
import datetime
import serial
import binascii
import os
import sys
import tkinter
from tkinter.scrolledtext import ScrolledText

module_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
                           'module')
sys.path.append(module_path)
import mover_controller
import param_manager
import utility

#______________________________________________________________________________
class Controller(tkinter.Frame):

  #____________________________________________________________________________
  def __init__(self, data_path):
    self.data_path = data_path
    self.mover = mover_controller.MoverController(param_manager
                                                  .get('mover_device'))
    self.mover_position = {'x': 0., 'y': 0., 'z': 0.}
    if self.mover.device is None:
      utility.print_error(f'MVC  failed to open: {self.mover.device_name}')
    tkinter.Frame.__init__(self)
    self.master.title(f'Field Mapping Controller (pid={os.getpid()})')
    #self.master.geometry('640x480')
    self.master.resizable(0, 0)
    self.pack(fill=tkinter.Y, expand=True)
    self.check_files()
    self.__make_menu()
    self.__make_label()
    self.__make_button()
    self.__make_status()
    self.mover_good = False
    self.mover_status = 'IDLE'

  #____________________________________________________________________________
  def __make_button(self):
    fbuttons = tkinter.Frame(self)
    fbuttons.pack(side=tkinter.TOP, padx=10, pady=10)
    #fbuttons.pack(row=0, column=0, padx=2, pady=2)
    font = ('Helvetica', -24, 'bold')
    self.bstart = tkinter.Button(fbuttons, text='Start', font=font,
                                 command=self.quit)
    self.bstart.config(state=tkinter.DISABLED)
    self.bstop = tkinter.Button(fbuttons, text='Stop', font=font,
                                command=self.stop)
    self.bstop.config(state=tkinter.DISABLED)
    self.bstart.pack(side=tkinter.LEFT, padx=5)
    self.bstop.pack(side=tkinter.LEFT, padx=5)
    font = ('Helvetica', -16, 'normal')
    self.bservo_on = tkinter.Button(fbuttons, text='Servo ON', font=font,
                                    command=self.servo_on)
    self.bservo_on.config(state=tkinter.DISABLED)
    self.bservo_off = tkinter.Button(fbuttons, text='Servo OFF', font=font,
                                     command=self.servo_off)
    self.bservo_off.config(state=tkinter.DISABLED)
    self.bservo_on.pack(side=tkinter.LEFT, padx=5)
    self.bservo_off.pack(side=tkinter.LEFT, padx=5)
    font = ('Helvetica', -16, 'bold')
    self.mover_enable = dict()
    self.mover_check = dict()
    self.set_manual = dict()
    self.lalarm_status = dict()
    self.lservo_status = dict()
    font = ('Helvetica', -14, 'bold')
    for key in self.mover.DEVICE_LIST:
      fxyz = tkinter.Frame(fbuttons)
      fxyz.pack(side=tkinter.LEFT, padx=10)
      self.mover_enable[key] = tkinter.BooleanVar()
      self.mover_enable[key].set(param_manager.get(f'device_id_{key}') is not None)
      self.mover_check[key] = tkinter.Checkbutton(fxyz, text=key.upper(),
                                                  variable=self.mover_enable[key])
      if not self.mover_enable[key].get():
        self.mover_check[key].config(state=tkinter.DISABLED)
      self.mover_check[key].pack(side=tkinter.TOP)
      self.set_manual[key] = False
      self.lservo_status[key] = tkinter.Label(fxyz, text='Servo OFF', font=font)
      self.lservo_status[key].pack(side=tkinter.TOP)
      self.lalarm_status[key] = tkinter.Label(fxyz, text='Alarm OFF', font=font)
      self.lalarm_status[key].pack(side=tkinter.TOP)
    fspeed = tkinter.Frame(fbuttons)
    lspeed = tkinter.Label(fspeed, text='Speed [mm/s]')
    lspeed.pack(side=tkinter.TOP)
    self.speed_e = tkinter.Entry(fspeed, justify=tkinter.RIGHT, width=10)
    self.speed_e.insert(0, str(self.get_speed()))
    self.speed_e.pack()
    fspeed.pack(side=tkinter.LEFT, padx=10)
    # finching = tkinter.Frame(fbuttons)
    linching = tkinter.Label(fspeed, text='Inching [mm]')
    linching.pack(side=tkinter.TOP)
    self.manual_inching_e = tkinter.Entry(fspeed, justify=tkinter.RIGHT, width=10)
    self.manual_inching_e.insert(0, str(self.get_manual_inching()))
    self.manual_inching_e.pack()
    # finching.pack(side=tkinter.LEFT, padx=10)
    finching = tkinter.Frame(fbuttons)
    font = ('Helvetica', -12, 'normal')
    lmanual = tkinter.Label(finching, text='Manual Inching')
    self.binching_up = tkinter.Button(finching, text='Inching Up', font=font,
                                      command=self.manual_inching_up)
    self.binching_up.config(state=tkinter.DISABLED)
    self.binching_dw = tkinter.Button(finching, text='Inching Dw', font=font,
                                      command=self.manual_inching_down)
    self.binching_dw.config(state=tkinter.DISABLED)
    lmanual.pack(side=tkinter.TOP, padx=5)
    self.binching_up.pack(side=tkinter.TOP, padx=5, pady=2)
    self.binching_dw.pack(side=tkinter.TOP, padx=5, pady=2)
    finching.pack(side=tkinter.LEFT, padx=5)

  #____________________________________________________________________________
  def __make_label(self):
    font = ('Helvetica', -24, 'bold')
    fstate = tkinter.Frame(self)
    fstate.pack(side=tkinter.TOP, fill=tkinter.X)
    self.daq_label = tkinter.Label(fstate, text='DAQ: Idle', width=30,
                                   relief=tkinter.SOLID,
                                   bg='black', fg='blue', font=font)
    self.daq_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    # tkinter.Frame(fstate, width=3).pack(side=tkinter.LEFT)
    self.mover_label = tkinter.Label(fstate, text='MOVER: Idle', width=30,
                                     bg='black', fg='blue', font=font)
    self.mover_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
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
    self.menu1.add_command(label='Zero return', command=self.zero_return)
    self.menu1.entryconfig('Zero return', state=tkinter.DISABLED)
    self.menu1.add_separator()
    self.menu1.add_command(label='Alarm reset', command=self.reset_alarm)
    self.menu1.entryconfig('Alarm reset', state=tkinter.DISABLED)
    self.menu1.add_separator()
    self.menu1.add_command(label='Quit', command=self.master.quit)
    self.menu2 = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Status', menu=self.menu2)
    self.print_debug = tkinter.IntVar()
    self.print_debug.set(0)
    self.print_info = tkinter.IntVar()
    self.print_info.set(1)
    self.print_warning = tkinter.IntVar()
    self.print_warning.set(1)
    self.print_error = tkinter.IntVar()
    self.print_error.set(1)
    self.menu2.add_checkbutton(label='Debug', onvalue=1, offvalue=0,
                               variable=self.print_debug)
    self.menu2.add_checkbutton(label='Info', onvalue=1, offvalue=0,
                               variable=self.print_info)
    self.menu2.add_checkbutton(label='Warning', onvalue=1, offvalue=0,
                               variable=self.print_warning)
    self.menu2.add_checkbutton(label='Error', onvalue=1, offvalue=0,
                               variable=self.print_error)
    menubar.add_cascade(label=' '*193, state=tkinter.DISABLED)
    self.menu3 = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Develop', menu=self.menu3)
    self.menu3.add_command(label='Reconnect Mover Driver',
                           command=self.reconnect_mover_driver)
    self.menu3.add_command(label='Force Zero return', command=self.zero_return)
    self.menu3.add_command(label='Force Alarm reset', command=self.reset_alarm)
    self.menu3.add_command(label='Force Servo ON', command=self.servo_on)
    self.menu3.add_command(label='Force Servo OFF', command=self.servo_off)

  #____________________________________________________________________________
  def __make_status(self):
    fstatus = tkinter.Frame(self)
    fstatus.pack(side=tkinter.LEFT, padx=10, pady=10)
    font = ('Helvetica', -16, 'bold')
    self.lmover_position_title = tkinter.Label(fstatus,
                                               text='Mover Coordinate',
                                               font=font)
    self.lmover_position_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    pos_txt = ''
    for key, val in self.mover.DEVICE_LIST.items():
      pos_txt += f'{key.upper()} {"-"*9:9}({"-"*9:9})\n'
    self.lmover_position = tkinter.Label(fstatus, text=pos_txt, font=font)
    self.lmover_position.pack(side=tkinter.TOP, padx=5)
    font = ('Helvetica', -16, 'bold')
    self.lfield_title = tkinter.Label(fstatus,
                                      text='Magnetic Field',
                                      font=font)
    self.lfield_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    mag_txt = ''
    for key, val in self.mover.DEVICE_LIST.items():
      mag_txt += f'B{key} {"-"*9:9} [T]\n'
    mag_txt += f'B  {"-"*9:9} [T]\n'
    self.lfield = tkinter.Label(fstatus, text=mag_txt, font=font)
    self.lfield.pack(side=tkinter.TOP, padx=5)
    font = ('Helvetica', -16, 'bold')
    self.lnmr_title = tkinter.Label(fstatus, text='NMR', font=font)
    self.lnmr_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    self.lnmr = tkinter.Label(fstatus, text='--------- [T]', font=font)
    self.lnmr.pack(side=tkinter.TOP, padx=5)
    flog = tkinter.Frame(self)
    flog.pack(side=tkinter.LEFT, padx=10, pady=10)
    font = ('Courier', -12)
    self.status_log = ScrolledText(flog, font=font, width=100)
    self.status_log.config(state=tkinter.DISABLED)
    self.status_log.pack(side=tkinter.TOP, padx=5, fill=tkinter.X)
    utility.set_log(self.status_log)

  #____________________________________________________________________________
  def check_files(self):
    misc_dir = os.path.join(self.data_path, 'misc')
    if not os.path.isdir(misc_dir):
      os.mkdir(misc_dir)
    self.speed_file = os.path.join(misc_dir, 'speed.txt')
    speed = self.get_speed() if os.path.isfile(self.speed_file) else 500
    with open(self.speed_file,'w') as f:
      f.write(str(speed))
    self.manual_inching_file = os.path.join(misc_dir, 'manual_inching.txt')
    inching = (self.get_manual_inching()
               if os.path.isfile(self.manual_inching_file) else 0)
    with open(self.manual_inching_file,'w') as f:
      f.write(str(inching))

  #____________________________________________________________________________
  def get_manual_inching(self):
    with open(self.manual_inching_file,'r') as f:
      return int(f.read())

  #____________________________________________________________________________
  def get_speed(self):
    with open(self.speed_file,'r') as f:
      return int(f.read())

  #____________________________________________________________________________
  def manual_inching_down(self):
    self.binching_up.config(state=tkinter.DISABLED)
    self.binching_dw.config(state=tkinter.DISABLED)
    self.bservo_on.config(state=tkinter.DISABLED)
    self.bservo_off.config(state=tkinter.DISABLED)
    utility.print_info('MVC  manual inching down (' +
                       f'{self.mover_position["x"]:9.1f},' +
                       f'{self.mover_position["y"]:9.1f},' +
                       f'{self.mover_position["z"]:9.1f})')
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.inching_down(val)

  #____________________________________________________________________________
  def manual_inching_up(self):
    self.binching_up.config(state=tkinter.DISABLED)
    self.binching_dw.config(state=tkinter.DISABLED)
    self.bservo_on.config(state=tkinter.DISABLED)
    self.bservo_off.config(state=tkinter.DISABLED)
    utility.print_info('MVC  manual inching up   (' +
                       f'{self.mover_position["x"]:9.1f},' +
                       f'{self.mover_position["y"]:9.1f},' +
                       f'{self.mover_position["z"]:9.1f})')
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.inching_up(val)

  #____________________________________________________________________________
  def reconnect_mover_driver(self):
    utility.print_info(f'MVC  reconnect mover driver')
    self.mover = mover_controller.MoverController(param_manager
                                                  .get('mover_device'))
    if self.mover.device is None:
      utility.print_error(f'MVC  failed to open: {self.mover.device_name}')
    self.mover_good = False
    self.mover_status = 'IDLE'
    for key, val in self.mover.DEVICE_LIST.items():
      self.set_manual[key] = False

  #____________________________________________________________________________
  def reset_alarm(self):
    utility.print_info(f'MVC  reset alarm')
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.reset_alarm(val)

  #____________________________________________________________________________
  def servo_off(self):
    self.bservo_off.config(state=tkinter.DISABLED)
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.servo_off(val)

  #____________________________________________________________________________
  def servo_on(self):
    self.bservo_on.config(state=tkinter.DISABLED)
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.servo_on(val)

  #____________________________________________________________________________
  def set_manual_inching(self, inching):
    if int(inching) < 0:
      self.manual_inching_e.delete(0, tkinter.END)
      self.manual_inching_e.insert(0, str(abs(int(inching))))
    inching = abs(int(inching))
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.set_manual_inching(val, inching*1000)
    with open(self.manual_inching_file,'w') as f:
      f.write(str(inching))

  #____________________________________________________________________________
  def set_speed(self, speed):
    if int(speed) < 0:
      self.speed_e.delete(0, tkinter.END)
      self.speed_e.insert(0, str(abs(int(speed))))
    speed = abs(int(speed))
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.set_speed(val, speed)
        ret = self.mover.get_speed(val)
    with open(self.speed_file,'w') as f:
      f.write(str(speed))

  #____________________________________________________________________________
  def stop(self):
    for key, val in self.mover.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        continue
      self.mover.stop(val)

  #____________________________________________________________________________
  def updater(self):
    utility.set_debug(self.print_debug.get() == 1)
    utility.set_info(self.print_info.get() == 1)
    utility.set_warning(self.print_warning.get() == 1)
    utility.set_error(self.print_error.get() == 1)
    self.update_mover()
    self.update_label()
    self.after(500, self.updater)

  #____________________________________________________________________________
  def update_label(self):
    now = str(datetime.datetime.now())[:19]
    self.lasttime.config(text=f'Last Run Start Time: {now}')
    data_path = param_manager.get('data_path')
    self.disklink.config(text=f'Data Storage Path: {data_path}')
    if self.mover_good:
      if self.mover_status == 'IDLE':
        self.mover_label.config(text='MOVER: Idle', bg='black', fg='blue')
    else:
      self.mover_label.config(text='MOVER: under Transition', fg='yellow', bg='red')
    # for key, val in self.mover.DEVICE_LIST.items():
    #   if self.mover_good and self.mover_enable[key].get():
    #     self.mover_check[key].config(state=tkinter.NORMAL)
    #   if not self.mover_good:
    #     self.mover_check[key].config(state=tkinter.DISABLED)

  #____________________________________________________________________________
  def update_mover(self):
    self.mover_good = False
    self.mover_status = 'IDLE'
    if self.mover.device is None:
      self.mover_status = 'ERROR'
      return
    count = 0
    for key, val in self.mover.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        continue
      count += 1
      if not self.set_manual[key]:
        self.set_manual[key] = self.mover.set_manual(val)
        if not self.set_manual[key]:
          return
        self.mover.device_info(val)
        self.mover.version(val)
      if not self.set_manual[key]:
        continue
    for key, val in self.mover.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        continue
      o_status = self.mover.io_status(val)
      if o_status is None:
        return
      is_moving = (o_status >> 6) & 0x1
      alarm_off = (o_status >> 15) & 0x1
      if is_moving == 1 and self.mover_status != 'ERROR':
        self.mover_status = 'MOVING'
      if alarm_off == 0:
        self.mover_status = 'ERROR'
    alarm_status = dict()
    alarm_status_all = 0
    for key, val in self.mover.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        self.lalarm_status[key].config(text='Alarm N/A', fg='gray')
        continue
      alarm_status[key] = self.mover.alarm_status(val)
      alarm_status_all += alarm_status[key]
      if alarm_status[key] == 0:
        self.lalarm_status[key].config(text='Alarm OFF', fg='black')
      else:
        self.lalarm_status[key].config(text=f'Alarm #{alarm_status[key]}', fg='red')
    if alarm_status_all == 0:
      self.menu1.entryconfig('Alarm reset', state=tkinter.DISABLED)
    else:
      self.menu1.entryconfig('Alarm reset', state=tkinter.NORMAL)
    # if count == 0:
    #   self.mover_good = True
    #   return
    servo_status = dict()
    servo_status_all = 0
    zero_return_status = dict()
    zero_return_status_all = 0
    for key, val in self.mover.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        self.lservo_status[key].config(text='Servo N/A', fg='gray')
        continue
      servo_status[key] = self.mover.servo_status(val)
      servo_status_all += servo_status[key]
      zero_return_status = self.mover.zero_return_status(val)
      zero_return_status_all += zero_return_status
      if servo_status[key] == 1:
        self.lservo_status[key].config(text=f'Servo ON', fg='red')
      elif servo_status[key] == 0:
        self.lservo_status[key].config(text=f'Servo OFF', fg='black')
    if count == servo_status_all:
      self.bservo_on.config(state=tkinter.DISABLED)
      if count == zero_return_status_all and count > 0:
        self.menu1.entryconfig('Zero return', state=tkinter.NORMAL)
        self.bservo_off.config(state=tkinter.NORMAL)
      else:
        self.menu1.entryconfig('Zero return', state=tkinter.DISABLED)
        self.bservo_off.config(state=tkinter.DISABLED)
    else:
      if alarm_status_all == 0:
        self.bservo_on.config(state=tkinter.NORMAL)
      else:
        self.bservo_on.config(state=tkinter.DISABLED)
      self.bservo_off.config(state=tkinter.DISABLED)
      self.menu1.entryconfig('Zero return', state=tkinter.DISABLED)
    pos_cur = dict()
    pos_cmd = dict()
    pos_txt = ''
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        pos_cur[key], pos_cmd[key] = self.mover.get_position(val)
        self.mover_position[key] = pos_cur[key]
        pos_txt += f'{key.upper()} {pos_cur[key]:9.1f}({pos_cmd[key]:9.1f})\n'
      else:
        pos_txt += f'{key.upper()} {"-"*9:9}({"-"*9:9})\n'
    self.lmover_position.config(text=pos_txt)
    try:
      val = int(self.speed_e.get())
    except ValueError:
      val = 0
      self.speed_e.delete(0, tkinter.END)
      self.speed_e.insert(0, str(val))
    if val != self.get_speed():
      self.set_speed(val)
    try:
      val = int(self.manual_inching_e.get())
    except ValueError:
      val = 0
      self.manual_inching_e.delete(0, tkinter.END)
      self.manual_inching_e.insert(0, str(val))
    if val != self.get_manual_inching():
      self.set_manual_inching(val)
    if (alarm_status_all == 0 and count == zero_return_status_all and
        self.mover_status != 'ERROR'):
      self.mover_good = True
      if (count == servo_status_all and count > 0 and
          self.mover_status != 'MOVING'):
        self.binching_up.config(state=tkinter.NORMAL)
        self.binching_dw.config(state=tkinter.NORMAL)
      else:
        self.binching_up.config(state=tkinter.DISABLED)
        self.binching_dw.config(state=tkinter.DISABLED)
    else:
      self.binching_up.config(state=tkinter.DISABLED)
      self.binching_dw.config(state=tkinter.DISABLED)
    if self.mover_status == 'MOVING':
      self.bservo_on.config(state=tkinter.DISABLED)
      self.bservo_off.config(state=tkinter.DISABLED)
      self.menu1.entryconfig('Zero return', state=tkinter.DISABLED)
      self.bstop.config(state=tkinter.NORMAL)
    else:
      self.bstop.config(state=tkinter.DISABLED)

  #____________________________________________________________________________
  def zero_return(self):
    for key, val in self.mover.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.zero_return(val)

#______________________________________________________________________________
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('param_file', nargs='?', default='param/param.txt',
                      help='param file')
  parsed, unparsed = parser.parse_known_args()
  param_manager.initialize(parsed.param_file)
  app = Controller(param_manager.get('data_path'))
  app.updater()
  app.mainloop()
