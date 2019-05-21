#!/usr/bin/env python3

USE_NMR = False

import argparse
import datetime
import serial
import binascii
import fcntl
import os
import sys
import subprocess
import time
import tkinter
from tkinter.scrolledtext import ScrolledText

from module import alarm_list
from module import hall_probe
if USE_NMR:
  from module import nmr
else:
  from module import ref_probe
from module import mover_controller
from module import param_manager
from module import progress
from module import step_manager
from module import temp_monitor
from module import utility

#______________________________________________________________________________
class Controller(tkinter.Frame):
  SOUND_FILE = 'module/under_transition.wav'

  #____________________________________________________________________________
  def __init__(self, param_file):
    self.mover_good = False
    self.mover_status = 'IDLE'
    self.daq_status = 'IDLE'
    self.step_status = 'IDLE'
    self.hpc_status = 'IDLE'
    if USE_NMR:
      self.nmr_status = 'IDLE'
    else:
      self.ref_status = 'IDLE'
    self.alarm_list = alarm_list.AlarmListWindow()
    self.progress = progress.ProgressWindow()
    tkinter.Frame.__init__(self)
    self.__make_menu()
    self.__make_label()
    self.__make_button()
    self.__make_status()
    param_manager.initialize(param_file)
    step_manager.initialize(param_manager.get('step_file'))
    self.data_path = param_manager.get('data_path')
    self.output_name = None
    if not os.path.isdir(self.data_path):
      os.mkdir(self.data_path)
    self.mover = mover_controller.MoverController()
    self.servo_status = {'x': 0, 'y': 0, 'z': 0}
    self.zero_return_status = {'x': 0, 'y': 0, 'z': 0}
    self.zero_return_status_all = 0
    self.mover_position_mon = {'x': 0., 'y': 0., 'z': 0.}
    self.mover_position_set = {'x': 0., 'y': 0., 'z': 0.}
    self.last_move = time.time()
    if self.mover.device is None:
      utility.print_error(f'MVC  failed to open: {self.mover.device_name}')
    self.hallprobe = hall_probe.HallProbeController()
    if USE_NMR:
      self.nmr = nmr.NMRController()
    else:
      self.ref = ref_probe.RefProbeController()
    self.temp = temp_monitor.TempMonitor()
    self.master.title(f'Field Mapping Controller (pid={os.getpid()})')
    self.master.resizable(0, 1)
    self.pack(fill=tkinter.Y, expand=True)
    self.check_files()
    self.check_button()
    self.last_under_transition = 0
    self.sound_file = self.__class__.SOUND_FILE

  #____________________________________________________________________________
  def __make_button(self):
    fbuttons = tkinter.Frame(self)
    fbuttons.pack(side=tkinter.TOP, padx=10, pady=10)
    font = ('Helvetica', -24, 'bold')
    self.bstart = tkinter.Button(fbuttons, text='Start', font=font,
                                 command=self.start)
    self.config_disabled(self.bstart)
    self.bstop = tkinter.Button(fbuttons, text='Stop', font=font,
                                command=self.stop)
    self.config_disabled(self.bstop)
    self.bstart.pack(side=tkinter.LEFT, padx=5)
    self.bstop.pack(side=tkinter.LEFT, padx=5)
    fstep = tkinter.Frame(fbuttons)
    fstep.pack(side=tkinter.LEFT, padx=10, pady=10)
    font = ('Helvetica', -12, 'normal')
    lstep_title = tkinter.Label(fstep, text='Step#', font=font)
    lstep_title.pack(side=tkinter.TOP, padx=5, expand=True)
    self.step_e = tkinter.Entry(fstep, justify=tkinter.RIGHT, width=10,
                                disabledbackground='white',
                                disabledforeground='black')
    self.step_e.bind('<Return>', self.set_step_by_return)
    self.step_e.pack(side=tkinter.TOP)
    fservo = tkinter.Frame(fbuttons)
    fservo.pack(side=tkinter.LEFT)
    lservo_title = tkinter.Label(fservo, text='Servo Power', font=font)
    lservo_title.pack(side=tkinter.TOP, padx=5, expand=True)
    self.bservo_on = tkinter.Button(fservo, text='Servo ON', font=font,
                                    command=self.servo_on)
    self.config_disabled(self.bservo_on)
    self.bservo_off = tkinter.Button(fservo, text='Servo OFF', font=font,
                                     command=self.servo_off)
    self.config_disabled(self.bservo_off)
    self.bservo_on.pack(side=tkinter.TOP, padx=5)
    self.bservo_off.pack(side=tkinter.TOP, padx=5)
    self.mover_enable = dict()
    self.mover_check = dict()
    self.set_manual = dict()
    self.lalarm_status = dict()
    self.lservo_status = dict()
    tkinter.Frame(fbuttons, width=10).pack(side=tkinter.LEFT)
    font = ('Helvetica', -14, 'bold')
    for key in mover_controller.MoverController.DEVICE_LIST:
      fxyz = tkinter.Frame(fbuttons)
      fxyz.pack(side=tkinter.LEFT, padx=0)
      self.mover_enable[key] = tkinter.BooleanVar()
      self.mover_check[key] = tkinter.Checkbutton(fxyz, text=key.upper(), width=7,
                                                  variable=self.mover_enable[key])
      self.mover_check[key].pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
      self.lservo_status[key] = tkinter.Label(fxyz, text='Servo OFF', font=font,
                                              bg='black', relief=tkinter.RAISED)
      self.lservo_status[key].pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
      self.lalarm_status[key] = tkinter.Label(fxyz, text='Alarm OFF', font=font,
                                              bg='black', relief=tkinter.RAISED)
      self.lalarm_status[key].pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
    fspeed = tkinter.Frame(fbuttons)
    lspeed = tkinter.Label(fspeed, text='Speed [mm/s]')
    lspeed.pack(side=tkinter.TOP)
    self.speed_e = tkinter.Entry(fspeed, justify=tkinter.RIGHT, width=10,
                                 disabledbackground='white',
                                 disabledforeground='black')
    self.speed_e.bind('<Return>', self.set_speed_by_return)
    self.speed_e.pack()
    fspeed.pack(side=tkinter.LEFT, padx=10)
    linching = tkinter.Label(fspeed, text='Inching [mm]')
    linching.pack(side=tkinter.TOP)
    self.manual_inching_e = tkinter.Entry(fspeed, justify=tkinter.RIGHT, width=10,
                                          disabledbackground='white',
                                          disabledforeground='black')
    self.manual_inching_e.bind('<Return>', self.set_manual_inching_by_return)
    self.manual_inching_e.pack()
    finching = tkinter.Frame(fbuttons)
    font = ('Helvetica', -12, 'normal')
    lmanual = tkinter.Label(finching, text='Manual Inching')
    self.binching_up = tkinter.Button(finching, text='Inching Up', font=font,
                                      command=self.manual_inching_up)
    self.config_disabled(self.binching_up)
    self.binching_dw = tkinter.Button(finching, text='Inching Dw', font=font,
                                      command=self.manual_inching_down)
    self.config_disabled(self.binching_dw)
    lmanual.pack(side=tkinter.TOP, padx=5)
    self.binching_up.pack(side=tkinter.TOP, padx=5, pady=2)
    self.binching_dw.pack(side=tkinter.TOP, padx=5, pady=2)
    finching.pack(side=tkinter.LEFT, padx=5)

  #____________________________________________________________________________
  def __make_label(self):
    font = ('Helvetica', -24, 'bold')
    fstate = tkinter.Frame(self)
    fstate.pack(side=tkinter.TOP, fill=tkinter.X)
    self.daq_label = tkinter.Label(fstate, text='DAQ: Idle', width=20,
                                   relief=tkinter.RAISED,
                                   bg='black', fg='blue', font=font)
    self.daq_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    # tkinter.Frame(fstate, width=3).pack(side=tkinter.LEFT)
    self.mover_label = tkinter.Label(fstate, text='MVC: Idle', width=20,
                                     relief=tkinter.RAISED,
                                     bg='black', fg='blue', font=font)
    self.mover_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    self.hpc_label = tkinter.Label(fstate, text='HPC: Idle', width=20,
                                   relief=tkinter.RAISED,
                                   bg='black', fg='blue', font=font)
    self.hpc_label.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
    flabels = tkinter.Frame(self)
    flabels.pack(side=tkinter.TOP, fill=tkinter.X, padx=100)
    self.lasttime = tkinter.Label(flabels, text='Last Update:')
    self.lasttime.pack(side=tkinter.LEFT, pady=10)
    self.disklink = tkinter.Label(flabels, text='Data Path:')
    self.disklink.pack(side=tkinter.RIGHT, pady=10)

  #____________________________________________________________________________
  def __make_menu(self):
    menubar = tkinter.Menu(self)
    self.master.config(menu=menubar)
    self.menu1 = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Control', menu=self.menu1)
    self.menu1.add_command(label='Alarm list',
                           command=self.alarm_list.deiconify)
    # self.menu1.add_command(label='Progress',
    #                        command=self.progress.deiconify)
    self.menu1.add_command(label='Print parameter',
                           command=self.print_parameter)
    self.menu1.add_command(label='Print mover parameter',
                           command=self.print_mover_parameter)
    self.config_disabled(self.menu1, 'Print mover parameter')
    self.menu1.add_separator()
    # self.menu1.add_command(label='Zero return', command=self.zero_return)
    # self.config_disabled(self.menu1, 'Zero return')
    self.menu1.add_command(label='Go to center', command=self.goto_center)
    self.config_disabled(self.menu1, 'Go to center')
    self.menu1.add_command(label='Alarm reset', command=self.reset_alarm)
    self.config_disabled(self.menu1, 'Alarm reset')
    self.menu1.add_separator()
    self.develop_mode = tkinter.BooleanVar()
    self.develop_mode.set(False)
    self.menu1.add_checkbutton(label='Develop mode', onvalue=True,
                               offvalue=False, variable=self.develop_mode)
    self.free_daq_mode = tkinter.BooleanVar()
    self.free_daq_mode.set(False)
    self.menu1.add_checkbutton(label='Free DAQ mode', onvalue=True,
                               offvalue=False, variable=self.free_daq_mode)
    self.free_daq_nevent = 0
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
    # menubar.add_cascade(label=' '*176, state=tkinter.DISABLED)
    self.menu3 = tkinter.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='Develop', menu=self.menu3)
    self.menu3.add_command(label='Reconnect Mover Driver',
                           command=self.reconnect_mover_driver)
    self.menu3.add_command(label='Zero return', command=self.zero_return)
    self.menu3.add_command(label='Force Go to center', command=self.goto_center)
    self.menu3.add_command(label='Force Alarm reset', command=self.reset_alarm)
    self.menu3.add_command(label='Force Servo ON', command=self.servo_on)
    self.menu3.add_command(label='Force Servo OFF', command=self.servo_off)
    self.menu3.add_command(label='Force Inching Up',
                           command=self.manual_inching_up)
    self.menu3.add_command(label='Force Inching Down',
                           command=self.manual_inching_down)
    self.menu3.add_command(label='Force Start', command=self.start)
    self.menu3.add_command(label='Force Stop', command=self.stop)
    # self.config_disabled(self.menu3)

  #____________________________________________________________________________
  def __make_status(self):
    fstatus = tkinter.Frame(self)
    fstatus.pack(side=tkinter.LEFT, padx=10, pady=10)
    font = ('Helvetica', -16, 'bold')
    lmover_position_title = tkinter.Label(fstatus, text='Mover Coordinate',
                                          font=font)
    lmover_position_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    pos_txt = f'   {"mon":^8}  {"set":^8}\n'
    for key in mover_controller.MoverController.DEVICE_LIST:
      pos_txt += f'{key.upper()} {"-"*9:9}({"-"*9:9})\n'
    self.lmover_position = tkinter.Label(fstatus, text=pos_txt, font=font)
    self.lmover_position.pack(side=tkinter.TOP, padx=5)
    font = ('Helvetica', -16, 'bold')
    lfield_title = tkinter.Label(fstatus, text='Hall Probe', font=font)
    lfield_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    mag_txt = ''
    for key in hall_probe.HallProbeController.CHANNEL_LIST:
      mag_txt += f'B{key} {"-"*10:10} [T]\n'
    self.lfield = tkinter.Label(fstatus, text=mag_txt, font=font)
    self.lfield.pack(side=tkinter.TOP)
    font = ('Helvetica', -16, 'bold')
    if USE_NMR:
      self.lnmr_title = tkinter.Label(fstatus, text='NMR', font=font)
      self.lnmr_title.pack(side=tkinter.TOP, padx=5, pady=5)
    else:
      self.lref_title = tkinter.Label(fstatus, text='Reference Probe',
                                      font=font)
      self.lref_title.pack(side=tkinter.TOP, padx=5, pady=5)
    font = ('Courier', -14, 'bold')
    if USE_NMR:
      self.lnmr = tkinter.Label(fstatus, text='--------- [T]', font=font)
      self.lnmr.pack(side=tkinter.TOP, padx=5)
    else:
      self.lref = tkinter.Label(fstatus, text='--------- [T]', font=font)
      self.lref.pack(side=tkinter.TOP, padx=5)
    flog = tkinter.Frame(self)
    flog.pack(side=tkinter.LEFT, padx=5, pady=5,
              expand=True, fill=tkinter.BOTH)
    font = ('Courier', -12)
    log_widget = ScrolledText(flog, font=font, width=90)
    self.config_disabled(log_widget)
    log_widget.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)
    utility.set_log_widget(log_widget)

  #____________________________________________________________________________
  def check_button(self):
    for key in mover_controller.MoverController.DEVICE_LIST:
      self.mover_enable[key].set(param_manager.get(f'device_id_{key}')
                                 is not None)
      if not self.mover_enable[key].get():
        self.config_disabled(self.mover_check[key])
      self.set_manual[key] = False

  #____________________________________________________________________________
  def check_files(self):
    ''' check misc files '''
    misc_dir = os.path.join(self.data_path, 'misc')
    if not os.path.isdir(misc_dir):
      os.mkdir(misc_dir)
    self.step_file = os.path.join(misc_dir, 'step.txt')
    step = self.get_step() if os.path.isfile(self.step_file) else 0
    self.step_e.insert(0, str(step))
    with open(self.step_file,'w') as f:
      f.write(str(step))
    self.speed_file = os.path.join(misc_dir, 'speed.txt')
    speed = self.get_speed() if os.path.isfile(self.speed_file) else 1
    self.speed_e.insert(0, str(speed))
    with open(self.speed_file,'w') as f:
      f.write(str(speed))
    self.manual_inching_file = os.path.join(misc_dir, 'manual_inching.txt')
    inching = (self.get_manual_inching()
               if os.path.isfile(self.manual_inching_file) else 0)
    self.manual_inching_e.insert(0, str(inching))
    with open(self.manual_inching_file,'w') as f:
      f.write(str(inching))
    self.log_dir = os.path.join(self.data_path, 'log')
    if not os.path.isdir(self.log_dir):
      os.mkdir(self.log_dir)

  #____________________________________________________________________________
  def check_under_transition(self):
    if self.sound_file is None:
      return
    if ((not self.mover_good and self.mover_status == 'ERROR') or
        self.hpc_status == 'ERROR'):
      now = time.time()
      if now - self.last_under_transition > 4:
        self.last_under_transition = now
        try:
          subprocess.Popen(['aplay', '-q', self.sound_file])
        except FileNotFoundError:
          pass

  #____________________________________________________________________________
  def config_disabled(self, widget, label=None):
    if label is None:
      if widget.cget('state') != 'disabled':
        widget.config(state=tkinter.DISABLED)
    else:
      if widget.entrycget(label, 'state') != 'disabled':
        widget.entryconfig(label, state=tkinter.DISABLED)

  #____________________________________________________________________________
  def config_normal(self, widget, label=None):
    if label is None:
      if widget.cget('state') != tkinter.NORMAL:
        widget.config(state=tkinter.NORMAL)
    else:
      if widget.entrycget(label, 'state') != tkinter.NORMAL:
        widget.entryconfig(label, state=tkinter.NORMAL)

  #____________________________________________________________________________
  def get_manual_inching(self):
    ''' get manual inching parameter '''
    with open(self.manual_inching_file,'r') as f:
      return float(f.read())

  #____________________________________________________________________________
  def get_speed(self):
    ''' get speed parameter '''
    with open(self.speed_file,'r') as f:
      return int(f.read())

  #____________________________________________________________________________
  def get_step(self):
    ''' get step number '''
    with open(self.step_file,'r') as f:
      return int(f.read())

  #____________________________________________________________________________
  def goto_center(self):
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        center = float(param_manager.get(f'center_{key}'))
        if self.mover.go_to(val, center):
          utility.print_info(f'MVC  ID = {val} go to center: {center}')

  #____________________________________________________________________________
  def manual_inching_down(self):
    ''' get manual inching down '''
    self.config_disabled(self.binching_up)
    self.config_disabled(self.binching_dw)
    self.config_disabled(self.bservo_on)
    self.config_disabled(self.bservo_off)
    utility.print_info('MVC  manual inching down from (' +
                       f'{self.mover_position_set["x"]:9.1f},' +
                       f'{self.mover_position_set["y"]:9.1f},' +
                       f'{self.mover_position_set["z"]:9.1f})')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        utility.print_info(f'MVC  ID = {val} inching up ' +
                           f'{self.manual_inching_e.get()} mm')
        self.mover.inching_down(val)

  #____________________________________________________________________________
  def manual_inching_up(self):
    ''' get manual inching up '''
    self.config_disabled(self.binching_up)
    self.config_disabled(self.binching_dw)
    self.config_disabled(self.bservo_on)
    self.config_disabled(self.bservo_off)
    utility.print_info('MVC  manual inching up  from (' +
                       f'{self.mover_position_set["x"]:9.1f},' +
                       f'{self.mover_position_set["y"]:9.1f},' +
                       f'{self.mover_position_set["z"]:9.1f})')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        utility.print_info(f'MVC  ID = {val} inching down ' +
                           f'{self.manual_inching_e.get()} mm')
        self.mover.inching_up(val)

  #____________________________________________________________________________
  def n_enable(self):
    count = 0
    for key, val in self.mover_enable.items():
      if val.get():
        count += 1
    return count

  #____________________________________________________________________________
  def print_mover_parameter(self):
    ''' print all mover parameters '''
    utility.print_info(f'MVC  print mover parameter')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.print_parameter(val)

  #____________________________________________________________________________
  def print_parameter(self):
    ''' print parameters '''
    param_manager.print_parameter()

  #____________________________________________________________________________
  def reconnect_mover_driver(self):
    ''' reconnect mover driver '''
    utility.print_info(f'MVC  reconnect mover driver')
    self.mover = mover_controller.MoverController()
    if self.mover.device is None:
      utility.print_error(f'MVC  failed to open: {self.mover.device_name}')
    self.mover_good = False
    self.mover_status = 'IDLE'
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      self.set_manual[key] = False

  #____________________________________________________________________________
  def reset_alarm(self):
    ''' send reset alarm command '''
    utility.print_info(f'MVC  reset alarm')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.reset_alarm(val)

  #____________________________________________________________________________
  def servo_off(self):
    ''' send servo off command '''
    self.config_disabled(self.bservo_off)
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.servo_off(val)

  #____________________________________________________________________________
  def servo_on(self):
    ''' send servo on command '''
    self.config_disabled(self.bservo_on)
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.servo_on(val)

  #____________________________________________________________________________
  def set_manual_inching(self, inching=None, force=False):
    if inching is None:
      try:
        val = float(self.manual_inching_e.get())
      except ValueError:
        val = 0
        self.manual_inching_e.delete(0, tkinter.END)
        self.manual_inching_e.insert(0, str(val))
      if force or val != self.get_manual_inching():
        self.set_manual_inching(val)
    else:
      if float(inching) < 0:
        self.manual_inching_e.delete(0, tkinter.END)
        self.manual_inching_e.insert(0, str(abs(int(inching))))
      inching = abs(float(inching))
      for key, val in mover_controller.MoverController.DEVICE_LIST.items():
        # if self.mover_enable[key].get():
        if val is not None:
          self.mover.set_manual_inching(val, int(inching*1000))
      with open(self.manual_inching_file,'w') as f:
        f.write(str(inching))

  #____________________________________________________________________________
  def set_manual_inching_by_return(self, event):
    self.set_manual_inching(force=True)

  #____________________________________________________________________________
  def set_speed(self, speed=None, force=False):
    if speed is None:
      try:
        val = int(self.speed_e.get())
      except ValueError:
        val = 1
        self.speed_e.delete(0, tkinter.END)
        self.speed_e.insert(0, str(val))
      if val == 0:
        val = 1
      if force or val != self.get_speed():
        self.set_speed(val)
    else:
      if int(speed) < 0:
        self.speed_e.delete(0, tkinter.END)
        self.speed_e.insert(0, str(abs(int(speed))))
      speed = abs(int(speed))
      for key, val in mover_controller.MoverController.DEVICE_LIST.items():
        # if self.mover_enable[key].get():
        if val is not None:
          self.mover.set_speed(val, speed)
          ret = self.mover.get_speed(val)
      with open(self.speed_file,'w') as f:
        f.write(str(speed))

  #____________________________________________________________________________
  def set_speed_by_return(self, event):
    self.set_speed(force=True)

  #____________________________________________________________________________
  def set_step(self, step=None, force=False):
    if step is None:
      try:
        val = int(self.step_e.get())
      except ValueError:
        val = 0
        self.step_e.delete(0, tkinter.END)
        self.step_e.insert(0, str(val))
      if force or val != self.get_step():
        self.set_step(val)
    else:
      if int(step) < 0:
        self.step_e.delete(0, tkinter.END)
        self.step_e.insert(0, str(abs(int(step))))
      step = abs(int(step))
      step_manager.set_step(step)
      with open(self.step_file,'w') as f:
        f.write(str(step))

  #____________________________________________________________________________
  def set_step_by_return(self, event):
    self.set_step(force=True)

  #____________________________________________________________________________
  def start(self):
    name = (str(datetime.datetime.now())[:19]
            .replace(':', '').replace("-", '').replace(' ', '_'))
    utility.set_log_file((os.path.join(self.log_dir, name + '.log')))
    utility.print_info('DAQ  start')
    self.free_daq_nevent = 0
    self.daq_status = 'RUNNING'
    self.config_disabled(self.bstart)
    self.config_normal(self.bstop)
    self.output_name = os.path.join(self.data_path, name + '.txt')
    utility.print_info(f'DAQ  open file: {self.output_name}')
    self.output_file = open(self.output_name, 'w')
    self.output_file.write(f'#\n# {self.output_name}\n#\n# param = ' +
                           f'{param_manager.get("param_file")}\n# step = ' +
                           f'{param_manager.get("step_file")}\n# speed = ' +
                           f'{self.get_speed()}\n#\n' +
                           f'# date time step x y z Bx By Bz ' +
                           ('NMR' if USE_NMR else 'REF') +
                           ' Temp1 Temp2\n\n')


  #____________________________________________________________________________
  def stop(self):
    if self.daq_status == 'RUNNING':
      utility.print_info('DAQ  stop')
      self.output_file.close()
      self.daq_status = 'IDLE'
      self.set_manual_inching(force=True)
      utility.print_info(f'DAQ  close file: {self.output_name}')
      utility.close_log_file()
    self.config_disabled(self.bstop)
    if self.mover_status == 'MOVING' or self.mover_status == 'ERROR':
      utility.print_info('MVC  stop')
      for key, val in mover_controller.MoverController.DEVICE_LIST.items():
        if self.mover_enable[key].get():
          self.mover.stop(val)

  #____________________________________________________________________________
  def updater(self):
    utility.set_debug(self.print_debug.get() == 1)
    utility.set_info(self.print_info.get() == 1)
    utility.set_warning(self.print_warning.get() == 1)
    utility.set_error(self.print_error.get() == 1)
    self.update_mover()
    self.update_hallprobe()
    if USE_NMR:
      self.update_nmr()
    else:
      self.update_ref()
    self.update_label()
    self.check_under_transition()
    self.update_step()
    self.update_free_daq()
    self.after(200, self.updater)

  #____________________________________________________________________________
  def update_free_daq(self):
    device_list = mover_controller.MoverController.DEVICE_LIST
    if not self.free_daq_mode.get():
      return
    if (self.daq_status == 'RUNNING' and self.ref.status):
      # for i in range(10):
      now = str(datetime.datetime.now())#[:19]
      utility.print_info(f'DAQ  save field : {self.free_daq_nevent}')
      buf = f'{now} {self.free_daq_nevent:>6} '
      for key, val in device_list.items():
        buf += f'{self.mover_position_mon[key]:9.3f} '
      for key in hall_probe.HallProbeController.CHANNEL_LIST:
        field = self.hallprobe.field[key][0]
        if 'mT' in self.hallprobe.field[key][1]:
          field *= 1e-3
        buf += f'{field:13.8f} '
      if USE_NMR:
        buf += f'{self.nmr.field:10.5f}'
      else:
        buf += f'{self.ref.field:10.7f}'
      # utility.print_info(f'STP  step#{step_manager.step_number} {buf}')
      buf += f'{self.temp.temp[0]:6.1f}'
      buf += f'{self.temp.temp[1]:6.1f}'
      self.output_file.write(buf + '\n')
      self.output_file.flush()
      self.free_daq_nevent += 1

  #____________________________________________________________________________
  def update_label(self):
    now = str(datetime.datetime.now())[:19]
    self.lasttime.config(text=f'Last Update: {now}')
    # data_path = param_manager.get('data_path')
    self.disklink.config(text=f'Data Path: {self.output_name}')
    if self.develop_mode.get():
      for i in range(10):
        self.config_normal(self.menu3, i)
    else:
      for i in range(10):
        self.config_disabled(self.menu3, i)
    # else:
    #   self.config_disabled(self.menu3)
    servo_status = True
    for key in mover_controller.MoverController.DEVICE_LIST:
      if self.mover_enable[key].get() and self.servo_status[key] != 1:
        servo_status = False
    if self.n_enable() == 0:
      servo_status = False
    if self.mover_good:
      if self.mover_status == 'IDLE':
        self.mover_label.config(text='MVC: Idle', fg='blue', bg='black')
        if ((self.daq_status == 'IDLE' and self.hpc_status == 'RUNNING' and
             servo_status) or
            (self.daq_status == 'IDLE' and self.free_daq_mode.get())):
          self.config_normal(self.bstart)
        else:
          self.config_disabled(self.bstart)
      elif self.mover_status == 'MOVING':
        self.mover_label.config(text='MVC: MOVING', fg='green', bg='black')
        self.config_disabled(self.bstart)
      else:
        self.config_disabled(self.bstart)
    else:
      self.mover_label.config(text='MVC: ERROR',
                              fg='yellow', bg='red')
      self.config_disabled(self.bstart)
    if self.daq_status == 'IDLE':
      self.daq_label.config(text='DAQ: Idle', fg='blue')
      self.config_normal(self.menu1, 'Quit')
    elif self.daq_status == 'RUNNING':
      self.daq_label.config(text='DAQ: RUNNING', fg='green')
      self.config_disabled(self.menu1, 'Quit')
    if self.hpc_status == 'IDLE':
      self.hpc_label.config(text='HPC: Idle', fg='blue', bg='black')
    elif self.hpc_status == 'RUNNING':
      self.hpc_label.config(text='HPC: RUNNING', fg='green', bg='black')
    elif self.hpc_status == 'DEVIATE':
      self.hpc_label.config(text='HPC: DEVIATE', fg='yellow', bg='black')
    elif self.hpc_status == 'ERROR':
      self.hpc_label.config(text='HPC: ERROR', fg='yellow', bg='red')


  #____________________________________________________________________________
  def update_hallprobe(self):
    if (not self.hallprobe.socket.is_open or
        not self.hallprobe.thread.is_alive):
      self.hpc_status = 'ERROR'
      return
    mag_txt = ''
    for key in hall_probe.HallProbeController.CHANNEL_LIST:
      val = self.hallprobe.field[key][0]
      unit = self.hallprobe.field[key][1]
      dev = self.hallprobe.field_dev[key]
      mag_txt += f'B{key} {val:10.5f} [{unit}] ({dev*100:9.4f}%)\n'
    self.lfield.config(text=mag_txt)
    if self.hallprobe.dev_status:
      self.hpc_status = 'RUNNING'
    else:
      self.hpc_status = 'DEVIATE'

  #____________________________________________________________________________
  def update_mover(self):
    self.mover_good = False
    self.mover_status = 'IDLE'
    if self.mover.device is None:
      self.mover_status = 'ERROR'
      # utility.print_error(f'MVC  failed to update (device is None)')
      return
    count = self.n_enable()
    self.config_normal(self.menu1, 'Print mover parameter')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        continue
      if not self.set_manual[key]:
        self.set_manual[key] = self.mover.set_manual(val)
        if not self.set_manual[key]:
          self.mover_status = 'ERROR'
          # utility.print_warning(f'MVC  failed to update (set manual)')
          return
        self.mover.device_info(val)
        self.mover.version(val)
        if self.set_manual[key]:
          utility.print_info(f'MVC  ID = {val} initialized')
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        continue
      o_status = self.mover.io_status(val)
      if o_status is None:
        self.mover_status = 'ERROR'
        utility.print_debug(f'MVC  failed to update (io status)')
        return
      is_moving = (o_status >> 6) & 0x1
      alarm_off = (o_status >> 15) & 0x1
      if is_moving == 1 and self.mover_status != 'ERROR':
        self.mover_status = 'MOVING'
      if alarm_off == 0:
        self.mover_status = 'ERROR'
    alarm_status = dict()
    alarm_status_all = 0
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        self.lalarm_status[key].config(text='Alarm N/A', fg='gray25')
        continue
      alarm_status[key] = self.mover.alarm_status(val)
      alarm_status_all += alarm_status[key]
      if alarm_status[key] == 0:
        self.lalarm_status[key].config(text='Alarm OFF', fg='blue')
      else:
        self.mover_status = 'ERROR'
        self.lalarm_status[key].config(text=f'Alarm #{alarm_status[key]}',
                                       fg='red')
    if alarm_status_all == 0:
      self.config_disabled(self.menu1, 'Alarm reset')
    else:
      self.config_normal(self.menu1, 'Alarm reset')
    # if count == 0:
    #   self.mover_good = True
    #   return
    servo_status_all = 0
    self.zero_return_status_all = 0
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if not self.mover_enable[key].get():
        self.lservo_status[key].config(text='Servo N/A', fg='gray25')
        continue
      self.servo_status[key] = self.mover.servo_status(val)
      servo_status_all += self.servo_status[key]
      self.zero_return_status[key] = self.mover.zero_return_status(val)
      self.zero_return_status_all += self.zero_return_status[key]
      if self.servo_status[key] == 1:
        self.lservo_status[key].config(text=f'Servo ON', fg='green')
      elif self.servo_status[key] == 0:
        self.lservo_status[key].config(text=f'Servo OFF', fg='blue')
    pos_txt = f'   {"mon":^8}  {"set":^8}  {"mag":^8}\n'
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      zero = ' ' if self.zero_return_status[key] == 1 else '*'
      if val is not None: #self.mover_enable[key].get():
        vmon, vset = self.mover.get_position(val)
        center = float(param_manager.get(f'center_{key}'))
        if 'x' in key:
          vmag = vmon - center
        else:
          vmag = center - vmon
        self.mover_position_mon[key] = vmon
        self.mover_position_set[key] = vset
        if (abs(vmon - vset) >
            int(param_manager.get('position_dev')) and
            self.servo_status[key] == 1):
          self.mover_status = 'MOVING'
        if vmon != -999999. and vset != -999999.:
          pos_txt += (f'{zero}{key.upper()} {vmon:9.1f}({vset:9.1f})' +
                      f'{vmag:9.1f}\n')
        else:
          pos_txt += f'{zero}{key.upper()} {"-"*9}({"-"*9}){"-"*9}\n'
      else:
        pos_txt += f'{zero}{key.upper()} {"-"*9:9}({"-"*9:9}){"-"*9}\n'
    self.lmover_position.config(text=pos_txt)
    if not self.mover.check_limit():
      self.mover_status = 'ERROR'
    if count == servo_status_all:
      self.config_disabled(self.bservo_on)
      # if count == zero_return_status_all and count > 0:
      if self.mover_status == 'MOVING':# or count != zero_return_status_all:
        # self.config_disabled(self.menu1, 'Zero return')
        self.config_disabled(self.menu1, 'Go to center')
        self.config_disabled(self.bservo_off)
      else:
        if count > 0:
          # self.config_normal(self.menu1, 'Zero return')
          if count == self.zero_return_status_all:
            self.config_normal(self.menu1, 'Go to center')
          self.config_normal(self.bservo_off)
    else:
      if alarm_status_all == 0:
        self.config_normal(self.bservo_on)
      else:
        self.config_disabled(self.bservo_on)
      if servo_status_all == 0:
        self.config_disabled(self.bservo_off)
      else:
        self.config_normal(self.bservo_off)
      # self.config_disabled(self.menu1, 'Zero return')
      self.config_disabled(self.menu1, 'Go to center')
    self.set_speed()
    self.set_manual_inching()
    if (alarm_status_all == 0 and #count == zero_return_status_all and
        self.mover_status != 'ERROR'):
      self.mover_good = True
      if (count == servo_status_all and count > 0 and
          self.mover_status != 'MOVING' and
          self.daq_status == 'IDLE'):
        self.config_normal(self.binching_up)
        self.config_normal(self.binching_dw)
      else:
        self.config_disabled(self.binching_up)
        self.config_disabled(self.binching_dw)
    else:
      self.config_disabled(self.binching_up)
      self.config_disabled(self.binching_dw)
    if self.mover_status == 'MOVING' or self.daq_status == 'RUNNING':
      self.config_disabled(self.bservo_on)
      self.config_disabled(self.bservo_off)
      # self.config_disabled(self.menu1, 'Zero return')
      self.config_disabled(self.menu1, 'Go to center')
      self.config_normal(self.bstop)
      self.config_disabled(self.speed_e)
      self.config_disabled(self.manual_inching_e)
    else:
      self.config_disabled(self.bstop)
      self.config_normal(self.speed_e)
      self.config_normal(self.manual_inching_e)

  #____________________________________________________________________________
  def update_nmr(self):
    if (not self.nmr.socket.is_open or
        self.nmr.thread_state != 'RUNNING'):
      self.nmr_status = 'ERROR'
      return
    if self.nmr.hold:
      mag_txt = f'{self.nmr.field:8.6f} [T]'
    else:
      mag_txt = 'UNDETECTABLE [T]'
    self.lnmr.config(text=mag_txt)

  #____________________________________________________________________________
  def update_ref(self):
    if (self.ref.device is None or
        not self.ref.thread.is_alive):
      self.ref_status = 'ERROR'
      return
    else:
      self.ref_status = 'IDLE'
    if self.ref.status:
      mag_txt = f'{self.ref.field:10.7f} [T]'
    else:
      mag_txt = 'UNDETECTABLE [T]'
    self.lref.config(text=mag_txt)

  #____________________________________________________________________________
  def update_step(self):
    if self.mover_status == 'ERROR':
      self.stop()
      return
    if self.free_daq_mode.get():
      return
    self.set_step()
    step_manager.step_number = self.get_step()
    device_list = mover_controller.MoverController.DEVICE_LIST
    if self.daq_status == 'RUNNING':
      if (self.mover_status == 'IDLE' and self.step_status == 'IDLE' and
          self.hallprobe.dev_status and self.ref.status):
        self.config_disabled(self.step_e)
        self.last_step = step_manager.step()
        if self.last_step is not None:
          self.config_normal(self.step_e)
          self.step_e.delete(0, tkinter.END)
          self.step_e.insert(0, str(step_manager.step_number))
          self.config_disabled(self.step_e)
          for key, val in device_list.items():
            if self.mover_enable[key].get():
              self.mover.go_to(val, float(self.last_step[key]))
              self.step_status = 'STEPPING'
          self.last_step_time = time.time()
        else:
          self.stop()
      else:
        status = True
        for key, val in device_list.items():
          if self.mover_enable[key].get():
            if (abs(self.mover_position_set[key] - self.last_step[key]) >=
                float(param_manager.get('position_dev'))*1e-3):
              status = False
              if self.mover_status == 'IDLE':
                utility.print_warning(f'STP  ID = {val} ' +
                                      'step might be failed -> RE-ADJUST')
                self.mover.go_to(val, float(self.last_step[key]))
        if (status and self.hallprobe.dev_status and self.ref.status and
            time.time() - self.last_step_time > 3.0):
          # for i in range(10):
          now = str(datetime.datetime.now())#[:19]
          # utility.print_info(f'DAQ  save step : {self.get_step()}')
          self.step_status = 'IDLE'
          buf = f'{now} {self.get_step():>6} '
          # for key, val in device_list.items():
          #   buf += f'{self.last_step[key]:9.1f} '
          for key, val in device_list.items():
            buf += f'{self.mover_position_mon[key]:9.3f} '
          for key in hall_probe.HallProbeController.CHANNEL_LIST:
            field = self.hallprobe.field_mean[key]
            # field = self.hallprobe.field[key][0]
            if 'mT' in self.hallprobe.field[key][1]:
              field *= 1e-3
            buf += f'{field:13.8f} '
          if USE_NMR:
            buf += f'{self.nmr.field:10.5f}'
          else:
            buf += f'{self.ref.field:10.7f}'
          # utility.print_info(f'STP  step#{step_manager.step_number} {buf}')
          buf += f'{self.temp.temp[0]:6.1f}'
          buf += f'{self.temp.temp[1]:6.1f}'
          self.output_file.write(buf + '\n')
          self.output_file.flush()
        elif time.time() - self.last_step_time > 180:
          utility.print_warning('STP  too long time to step?')
    else:
      self.config_normal(self.step_e)

  #____________________________________________________________________________
  def zero_return(self):
    for key, val in mover_controller.MoverController.DEVICE_LIST.items():
      if self.mover_enable[key].get():
        self.mover.zero_return(val)

#______________________________________________________________________________
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('param_file', nargs='?', default='param/param.txt',
                      help='param file')
  parsed, unparsed = parser.parse_known_args()
  lock_file = '/tmp/magfield.lock'
  with open(lock_file, 'w') as lock:
    try:
      fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
      app = Controller(parsed.param_file)
      app.updater()
      app.mainloop()
    except IOError:
      print('process is already running -> exit')
