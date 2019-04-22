#!/usr/bin/env python3

import datetime
import sys
import tkinter
from tkinter.scrolledtext import ScrolledText

status_log = None
debug_on = False
info_on = True
warning_on = True
error_on = True
max_log_line = 500
tag_list = ['' for x in range(max_log_line)]

#______________________________________________________________________________
class Utility:
  escape = True
  black = '\033[30m'
  red = '\033[31m'
  green = '\033[32m'
  yellow = '\033[33m'
  blue = '\033[34m'
  magenta = '\033[35m'
  cyan = '\033[36m'
  white = '\033[37m'
  end = '\033[0m'
  bold = '\033[1m'
  underline = '\033[4m'
  invisible = '\033[08m'
  reverce = '\033[07m'

#______________________________________________________________________________
def add_text(line, fgcolor='black', bgcolor='white'):
  if status_log is None:
    return
  line += '\n'
  status_log.config(state=tkinter.NORMAL)
  status_log.insert(tkinter.END, line)
  end_index = status_log.index(tkinter.END)
  begin_index = f'{end_index}-{len(line) + 1}c'
  status_log.tag_delete(tag_list[0], begin_index, end_index)
  tag_list.pop(0)
  tag_list.append(str(datetime.datetime.now()))
  status_log.tag_add(tag_list[-1], begin_index, end_index)
  status_log.tag_config(tag_list[-1], foreground=fgcolor, background=bgcolor)
  if end_index > f'{max_log_line}.0':
    status_log.delete(1.0, end_index + f'-{max_log_line + 1}lines')
  status_log.config(state=tkinter.DISABLED)
  status_log.see(tkinter.END)

#______________________________________________________________________________
def print_debug(arg):
  if debug_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.blue + Utility.bold + ' DEBUG' + Utility.end + '   ' + arg)
    add_text(str(datetime.datetime.now())[:19] + '  DEBUG   ' + arg,
             fgcolor='blue')

#______________________________________________________________________________
def print_error(arg):
  if error_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.red + Utility.bold + ' ERROR ' + Utility.end + '  ' + arg)
    add_text(str(datetime.datetime.now())[:19] + '  ERROR   ' + arg,
             fgcolor='red')

#______________________________________________________________________________
def print_info(arg):
  if info_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          ' INFO' + '    ' + arg)
    add_text(str(datetime.datetime.now())[:19] + '  INFO    ' + arg)

#______________________________________________________________________________
def print_warning(arg):
  if warning_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.yellow + Utility.bold + 'WARNING' + Utility.end + '  ' + arg)
    add_text(str(datetime.datetime.now())[:19] + ' WARNING  ' + arg,
             fgcolor='orange3')

#______________________________________________________________________________
def set_debug(flag=True):
  global debug_on
  debug_on = flag

#______________________________________________________________________________
def set_error(flag=True):
  global error_on
  error_on = flag

#______________________________________________________________________________
def set_info(flag=True):
  global info_on
  info_on = flag

#______________________________________________________________________________
def set_warning(flag=True):
  global warning_on
  warning_on = flag

#______________________________________________________________________________
def set_log(text):
  global status_log
  status_log = text
