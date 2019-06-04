#!/usr/bin/env python3

import datetime
import numpy
import os
import threading
import ROOT

import param_manager
import utility

#______________________________________________________________________________
def magnet_coordinate(x, y, z):
  xx = - 215.7 - y
  yy = - 212.1 - z
  zz = - x + 298.1
  v = ROOT.TVector3(xx, yy, zz)
  # v.RotateZ(0.001)
  return v

#______________________________________________________________________________
def magnet_field(bx, by, bz):
  v = ROOT.TVector3(bx, bz, -by)
  return v

#______________________________________________________________________________
class FieldElement():

  #____________________________________________________________________________
  def __init__(self, data):
    self.data = data
    self.unix_time = data[-1]
    if len(data) >= 13:
      self.bref = float(data[10])
      self.temp1 = float(data[11])
      self.temp2 = float(data[12])
      self.bscale = abs(self.bref/0.7133)
    else:
      self.bref = -9999
      self.temp1 = 0
      self.temp2 = 0
      self.bscale = 1
    self.bscale = 1
    self.p = magnet_coordinate(float(data[3]),
                                 float(data[4]),
                                 float(data[5]))
    self.b = magnet_field(float(data[6]) * self.bscale,
                          float(data[7]) * self.bscale,
                          float(data[8]) * self.bscale)


#______________________________________________________________________________
class FieldMapManager():
  __instance = None
  __lock = threading.Lock()

  #____________________________________________________________________________
  def __init__(self):
    utility.print_debug('FLD  __init__')
    param_man = param_manager.ParamManager()
    data_path = param_man.get('data_path')
    center_x = float(param_man.get('center_x'))
    center_y = float(param_man.get('center_y'))
    center_z = float(param_man.get('center_z'))
    self.field_map = dict()
    self.bscale = 1.0
    process_time_array = []
    for fname in sorted(os.listdir(data_path)):
      fname = os.path.join(data_path, fname)
      if not os.path.isfile(fname):
        continue
      if ('2019051' in fname or
          '2019052' in fname or
          '20190530' in fname or
          '20190531_02' in fname or
          '20190531_03' in fname or
          '20190531_04' in fname or
          '20190531_05' in fname or
          '20190531_061407' in fname):
          #'20190530_021341' in fname):
        continue
      mtime = os.stat(fname).st_mtime
      if mtime < 1557990000:
        continue
      prev_time = None
      with open(fname) as f:
        utility.print_info(f'FLD  read {fname}')
        for line in f:
          columns = line.split()
          if '#' in line or len(columns) < 10:
            continue
          ix = int(numpy.round(float(columns[3]) - center_x) / 10 + 26)
          iy = int(numpy.round(float(columns[4]) - center_y) / 10 + 26)
          iz = int(numpy.round(float(columns[5]) - center_z) / 10 + 28)
          istep = int(float(columns[2]))
          if abs(float(columns[10])) < 0.5:
            continue
#          key = (ix, iy, iz)
          key = (ix, iy, istep)
          curr_time = self.__get_timestamp(columns)
          columns.append(curr_time)
          if key in self.field_map.keys() and False:
            print('exist', self.field_map[key].data, columns)

          else:
#            self.field_map[ix, iy, iz] = FieldElement(columns)
            self.field_map[ix, iy, istep] = FieldElement(columns)
            #print("2 step " + str(columns[2]))
          if prev_time is not None:
            process_time = curr_time - prev_time
            process_time_array.append(process_time)
            prev_time = curr_time
          speed = numpy.mean(process_time_array)
  #        utility.print_info(f'FLD  average speed = {speed:.3f} s')
          self.calculate_maxwell_equation()


  #____________________________________________________________________________
  def __new__(cls):
    with cls.__lock:
      if cls.__instance is None:
        cls.__instance = super().__new__(cls)
        utility.print_debug('FLD  __new__')
    return cls.__instance

  #____________________________________________________________________________
  def __divB(self, key):
    div = 0
    b = self.field_map[key].b
    for i in range(3):
      v = [key[0], key[1], key[2]]
      v[i] += 1
      vup = (v[0], v[1], v[2])
      v = [key[0], key[1], key[2]]
      v[i] -= 1
      vdw = (v[0], v[1], v[2])
      bup = self.__get_field(vup)
      bdw = self.__get_field(vdw)
      if bup is not None and bdw is not None:
        div += (bup[i] - bdw[i])/20
      elif bup is None and bdw is None:
#        utility.print_warning('FLD  this element is alone : ' +
#                              f'{i} {key} {self.field_map[key].p.Mag():.2f}')
        div += 0.
      elif bup is None:
        div += (b[i] - bdw[i])/10
      elif bdw is None:
        div += (bup[i] - b[i])/10
    return div

  #____________________________________________________________________________
  def __get_field(self, key):
    if key in self.field_map:
      return self.field_map[key].b
    else:
      return None

  #____________________________________________________________________________
  def __get_timestamp(self, data):
    y = int(data[0][:4])
    m = int(data[0][5:7])
    d = int(data[0][8:10])
    H = int(data[1][:2])
    M = int(data[1][3:5])
    S = int(data[1][6:8])
    us = int(data[1][9:])
    dt = datetime.datetime(y, m, d, H, M, S, us)
    return dt.timestamp()

  #____________________________________________________________________________
  def __rotB(self, key):
    rot = []
    b = self.field_map[key].b
    for i in range(3): # dB_i
      val = 0
      for j in range(3): # dx
        if i == j:
          continue
        v = [key[0], key[1], key[2]]
        v[j] += 1
        vup = (v[0], v[1], v[2])
        v = [key[0], key[1], key[2]]
        v[j] -= 1
        vdw = (v[0], v[1], v[2])
        bup = self.__get_field(vup)
        bdw = self.__get_field(vdw)
        sign = 1 if i == ((j + 1) % 3) else -1
        if bup is not None and bdw is not None:
          val += (bup[i] - bdw[i])/20 * sign
        elif bup is None and bdw is None:
 #         utility.print_warning('FLD  this element is alone : ' +
 #                               f'{i} {key} {self.field_map[key].p.Mag():.2f}')
          val += 0.
        elif bup is None:
          val += (b[i] - bdw[i])/10 * sign
        elif bdw is None:
          val += (bup[i] - b[i])/10 * sign
      rot.append(val)
    return rot

  #____________________________________________________________________________
  def calculate_maxwell_equation(self):
    for key, elm in self.field_map.items():
      elm.divB = self.__divB(key)
      rotB = self.__rotB(key)
      elm.rotBx = rotB[0]
      elm.rotBy = rotB[1]
      elm.rotBz = rotB[2]
