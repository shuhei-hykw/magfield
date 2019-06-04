#!/usr/bin/env python3

import datetime
import sys

debug_on = False
info_on = True
warning_on = True
error_on = True

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
def close_log_file():
  global log_file
  log_file.close()
  log_file = None

#______________________________________________________________________________
def print_debug(arg):
  if debug_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.blue + Utility.bold + ' DEBUG' + Utility.end + '   ' + arg)

#______________________________________________________________________________
def print_error(arg):
  if error_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.red + Utility.bold + ' ERROR ' + Utility.end + '  ' + arg)

#______________________________________________________________________________
def print_info(arg):
  if info_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          ' INFO' + '    ' + arg)

#______________________________________________________________________________
def print_warning(arg):
  if warning_on:
    print(str(datetime.datetime.now())[:19] + ' ' +
          Utility.yellow + Utility.bold + 'WARNING' + Utility.end + '  ' + arg)

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
