#!/usr/bin/env python3

import math
import operator

import ROOT

center_x = 298.1
center_y = -215.7
#center_z = -213.3
center_z = -212.1
limit_r = 270
limit_z = 290
max_z = 47

#______________________________________________________________________________
def make_step():
  n = 61
  step_list = []
  for ix in range(n):
    x = center_x + 10 * (ix - int(n/2))
    for iy in range(n):
      y = center_y + 10 * (iy - int(n/2))
      r = math.hypot(x - center_x, y - center_y)
      phi = math.atan2(y - center_y, x - center_x)
      if limit_r <= r:
        continue
      for iz in range(n):
        z = center_z + 10 * (iz - int(n/2))
        if (iy % 2) == 1:
          z = center_z + 10 * (int(n/2) - iz)
        if limit_z <= abs(z - center_z):
          continue
        if max_z <= z:
          continue
        # if iz == 0 or iz == n - 1 or 45 < z or True:
        step_list.append([x, y, z, phi, r])
  # step_list.sort(key=operator.itemgetter(3))
  with open('test_step.txt', 'w') as f:
    for step in step_list:
      f.write(f'{step[0]:.1f}\t{step[1]:.1f}\t{step[2]:.1f}\t{step[3]:.1f}\t{step[4]:.1f}\n')
      # val = 0 if (i % 2) == 0 else 10
      #f.write(f'{val}\t{-val}\t{-val}\n')

#______________________________________________________________________________
def make_test_step():
  n = 61
  step_list = []
  for ix in range(n):
    x = center_x + 10 * (ix - int(n/2))
    for iy in range(n):
      y = center_y + 10 * (iy - int(n/2))
      r = math.hypot(x - center_x, y - center_y)
      phi = math.atan2(y - center_y, x - center_x)
      if limit_r <= r:
        continue
      if r <= limit_r - 10:
        continue
      for iz in range(n):
        z = center_z + 10 * (iz - int(n/2))
        if (iy % 2) == 1:
          z = center_z + 10 * (int(n/2) - iz)
        if limit_z <= abs(z - center_z):
          continue
        if max_z <= z:
          continue
        # if iz == 0 or iz == n - 1 or 45 < z or True:
        if iz == 2:
          step_list.append([x, y, z, phi, r])
  step_list.sort(key=operator.itemgetter(3))
  with open('test_step.txt', 'w') as f:
    for step in step_list:
      f.write(f'{step[0]:.1f}\t{step[1]:.1f}\t{step[2]:.1f}\t{step[3]:.1f}\t{step[4]:.1f}\n')
      # val = 0 if (i % 2) == 0 else 10
      #f.write(f'{val}\t{-val}\t{-val}\n')

#______________________________________________________________________________
def show_step():
  ROOT.gStyle.SetOptStat('1111110')
  ROOT.gStyle.SetPalette(ROOT.kCool);
  # ROOT.gStyle.SetCanvasColor(ROOT.kBlack);
  h_xy = ROOT.TH2F('h_xy', 'Step Position XY', 120,
                   center_x - 600, center_x + 600,
                   120,
                   center_y - 600, center_y + 600)
  with open('test_step.txt') as f:
    for line in f:
      columns = line.split()
      x = float(columns[0])
      y = float(columns[1])
      z = float(columns[2])
      h_xy.Fill(x, y)
  c1 = ROOT.TCanvas('c1', 'c1', 800, 800)
  h_xy.Draw('colz')
  #h_xy.Draw('box')
  c1.Modified()
  c1.Update()
  ROOT.TPython.Prompt()

#______________________________________________________________________________
if __name__ == '__main__':
  # make_test_step()
  make_step()
  show_step()
