#!/usr/bin/env python3

import time

from . import mover_controller
from . import param_manager
from . import utility

step_number = 0
step_list = []

#______________________________________________________________________________
def get(key):
  if key in param_list:
    return param_list[key]
  return None

#______________________________________________________________________________
def initialize(step_file):
  utility.print_info(f'STP  read {step_file}')
  global step_list
  with open(step_file, 'r') as f:
    i = 0
    for line in f:
      columns = line.split()
      if len(columns) < 3 or '#' in columns[0]:
        continue
      # cmd_pos = [int]
      step_list.append({'x': int(columns[0]),
                        'y': int(columns[1]),
                        'z': int(columns[2])})
      utility.print_info(f'STP  step#{i} {step_list[-1]}')
  utility.print_info(f'STP  initialized')

#______________________________________________________________________________
def set_step(step):
  global step_number
  utility.print_info(f'STP  set step: {step_number}')
  step_number = step

#______________________________________________________________________________
def step():
  global step_number
  if step_number >= len(step_list):
    return None
  utility.print_info(f'STP  step#{step_number} {step_list[step_number]}')
  step_number += 1
  return step_list[step_number-1]
