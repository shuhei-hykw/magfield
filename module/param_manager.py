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
  global param_list
  param_list['param_file'] = param_file
  with open(param_file, 'r') as f:
    for line in f:
      columns = line.split()
      if len(columns) < 2 or '#' in columns[0]:
        continue
      param_list[columns[0]] = columns[1]
      utility.print_info(f'PRM  key = {columns[0] + ",":16} ' +
                         f'val = {columns[1]}')
  utility.print_info(f'PRM  initialized')
