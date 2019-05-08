#!/usrbin/env python3

import os
import sys

from . import utility

param_list = dict()

#______________________________________________________________________________
def get(key):
  if key in param_list:
    return param_list[key]
  return None

#______________________________________________________________________________
def initialize(param_file):
  utility.print_info(f'PRM  read {param_file}')
  if os.path.isfile(param_file):
    global param_list
    param_list['param_file'] = param_file
    with open(param_file, 'r') as f:
      for line in f:
        columns = line.split()
        if len(columns) < 2 or '#' in columns[0]:
          continue
        param_list[columns[0]] = columns[1]
        utility.print_info(f'PRM  key = {columns[0] + ",":18} ' +
                           f'val = {columns[1]}')
      utility.print_info(f'PRM  initialized')
  else:
    utility.print_error(f'PRM  NOT initialized')

#______________________________________________________________________________
def print_parameter():
  utility.print_info(f'PRM  print parameter')
  for key, val in param_list.items():
    utility.print_info(f'PRM  key = {key + ",":18} ' +
                       f'val = {val}')
