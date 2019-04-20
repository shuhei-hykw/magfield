#!/usr/bin/env python3

import datetime
import sys


#______________________________________________________________________________
class Utility:
  escape = True
  debug = False
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
def print_debug(arg):
  if Utility.debug:
    print('[' + str(datetime.datetime.now())[:19] + ' ' +
          Utility.blue + Utility.bold + ' DEBUG' + Utility.end + '  ] ' + arg)

#______________________________________________________________________________
def print_error(arg):
  print('[' + str(datetime.datetime.now())[:19] + ' ' +
        Utility.red + Utility.bold + ' ERROR ' + Utility.end + ' ] ' + arg)

#______________________________________________________________________________
def print_info(arg, sep=''):
  if '()' in arg:
    sep = '_'
  print('[' + str(datetime.datetime.now())[:19] + ' ' +
        #Utility.green + Utility.bold +
        ' INFO' + '   ] ' + arg)

#______________________________________________________________________________
def print_warning(arg):
  print('[' + str(datetime.datetime.now())[:19] + ' ' +
        Utility.yellow + Utility.bold + 'WARNING' + Utility.end + ' ] ' + arg)

#______________________________________________________________________________
def set_debug(flag=True):
  Utility.debug = flag

#______________________________________________________________________________
def ExitFailure( message ):
    sys.stderr.write('ERROR: ' + message + '\n')
    sys.exit( 1 )
    return None

#______________________________________________________________________________
def decodeTime( info ) :
    second = int( info['time'] )
    hour    = second // 3600
    second -= hour    * 3600
    minute  = second // 60
    second -= minute  * 60
    return '{}:{:02d}:{:02d}'.format( hour, minute, second )

#______________________________________________________________________________
def decodeStatus( info ) :
    buff = ''
    stat = info['stat']
    nseg = info['nseg']
    prog = info['prog']
    if stat is None :
        buff = 'init({})'.format( nseg )
    elif stat is 0 :
        buff = 'running({}/{})'.format( prog, nseg )
    elif stat is 1 :
        buff = 'running({}/{})'.format( prog, nseg )
    elif stat is 2 :
        buff = 'merging({})'.format( nseg )
    elif stat is 3 :
        buff = 'terminated({})'.format( nseg )
    elif stat is True :
        buff = 'done({})'.format( nseg )
    elif stat is False :
        buff = 'error({})'.format( nseg )
    else :
        buff = 'unknown({})'.format( nseg )
    return buff
