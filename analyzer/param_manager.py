#!/usrbin/env python3

import os
import sys
import threading

import utility

initialized = False

#______________________________________________________________________________
class ParamManager():
  __instance = None
  __lock = threading.Lock()

  #____________________________________________________________________________
  def __init__(self):
    utility.print_debug('PRM  __init__')

  #____________________________________________________________________________
  def __new__(cls):
    with cls.__lock:
      if cls.__instance is None:
        cls.__instance = super().__new__(cls)
        utility.print_debug('PRM  __new__')
    return cls.__instance

  #____________________________________________________________________________
  def initialize(self, param_file):
    self.param_file = param_file
    self.param_list = dict()
    utility.print_info(f'PRM  read {self.param_file}')
    if os.path.isfile(self.param_file):
      self.param_list['param_file'] = self.param_file
      with open(self.param_file, 'r') as f:
        for line in f:
          columns = line.split()
          if len(columns) < 2 or '#' in columns[0]:
            continue
          self.param_list[columns[0]] = columns[1]
          utility.print_info(f'PRM  key = {columns[0] + ",":18} ' +
                             f'val = {columns[1]}')
        utility.print_info(f'PRM  initialized')
      self.initialized = True
    else:
      utility.print_error(f'PRM  NOT initialized')
      self.initialized = False

  #____________________________________________________________________________
  def get(self, key):
    if not self.initialized:
      utility.print_error(f'PRM  NOT initialized')
      raise Exception
    if key in self.param_list:
      return self.param_list[key]
    return None

  #____________________________________________________________________________
  def print_parameter(self):
    if not self.initialized:
      utility.print_error(f'PRM  NOT initialized')
      raise Exception
    utility.print_info(f'PRM  print parameter')
    for key, val in param_list.items():
      utility.print_info(f'PRM  key = {key + ",":18} ' +
                         f'val = {val}')
