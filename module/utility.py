#!/usr/bin/env python3

import datetime
import sys
import tkinter
from tkinter.scrolledtext import ScrolledText

log_widget = None
log_file = None
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
  if log_widget is None:
    return
  line += '\n'
  if log_file is not None:
    log_file.write(line)
    log_file.flush()
  log_widget.config(state=tkinter.NORMAL)
  log_widget.insert(tkinter.END, line)
  end_index = log_widget.index(tkinter.END)
  begin_index = f'{end_index}-{len(line) + 1}c'
  log_widget.tag_delete(tag_list[0], begin_index, end_index)
  tag_list.pop(0)
  tag_list.append(str(datetime.datetime.now()))
  log_widget.tag_add(tag_list[-1], begin_index, end_index)
  log_widget.tag_config(tag_list[-1], foreground=fgcolor, background=bgcolor)
  if end_index > f'{max_log_line}.0':
    log_widget.delete(1.0, end_index + f'-{max_log_line + 1}lines')
  log_widget.config(state=tkinter.DISABLED)
  log_widget.see(tkinter.END)

#______________________________________________________________________________
def close_log_file():
  global log_file
  log_file.close()
  log_file = None

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
def set_log_file(log):
  global log_file
  log_file = open(log, 'w')

#______________________________________________________________________________
def set_log_widget(widget):
  global log_widget
  log_widget = widget
