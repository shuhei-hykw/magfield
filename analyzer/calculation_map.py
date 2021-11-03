#!/usr/bin/python3

import threading

import numpy
import param_manager
import utility

ref_pos = numpy.array([0., 457. + 12. + 0.8, 0.])

#______________________________________________________________________________
class CalcMap():
  __instance = None
  __lock = threading.Lock()
  field_map = dict()

  #____________________________________________________________________________
  def __init__(self):
    utility.print_debug('CAL  __init__')
    param_man = param_manager.ParamManager()
    calc_map = param_man.get('field_map')
    min_dist = 1e10
    with open(calc_map, 'r') as f:
      for line in f:
        if '#' in line:
          continue
        # utility.print_info(f'CAL  {line}')
        columns = line.split()
        p = (numpy.round(float(columns[0])*1e3),
             numpy.round(float(columns[2])*1e3),
             numpy.round(-float(columns[1])*1e3))
        __class__.field_map[p] = [float(columns[3]),
                                  float(columns[5]),
                                  -float(columns[4])]
        p = numpy.array([float(columns[0])*1e3,
                         float(columns[2])*1e3,
                         -float(columns[1])*1e3])
        d = numpy.linalg.norm(p - ref_pos)
        if d < min_dist:
          min_dist = d
          min_pos = p
          ref_calc = [float(columns[3]),
                      float(columns[4]),
                      float(columns[5])]
    utility.print_info('CAL  initialized')

  #____________________________________________________________________________
  def __new__(cls):
    with cls.__lock:
      if cls.__instance is None:
        cls.__instance = super().__new__(cls)
        utility.print_debug('CAL  __new__')
    return cls.__instance

  #____________________________________________________________________________
  def draw(self):
    import ROOT
    # ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator)
    # ROOT.gStyle.SetPalette(ROOT.kBlueRedYellow)
    # ROOT.gStyle.SetPalette(ROOT.kColorPrintableOnGrey)
    ROOT.gStyle.SetPadRightMargin(0.15)
    harray = dict()
    for i, t in enumerate(['X', 'Y', 'Z']):
      for ii, tt in enumerate(['Y%X', 'Y%Z', 'Z%X']):
        key = f'B_{t} [{tt}]'
        nbin = 54
        pmin = -270-5
        pmax = 270-5
        harray[key] = ROOT.TH2F(key, key, nbin, pmin, pmax, nbin, pmin, pmax)
    barray = []
    for p, b in __class__.field_map.items():
      if abs(p[2]) < 0.001:
        harray['B_X [Y%X]'].Fill(numpy.round(p[0]), numpy.round(p[1]), b[0])
        harray['B_Y [Y%X]'].Fill(numpy.round(p[0]), numpy.round(p[1]), b[1])
        harray['B_Z [Y%X]'].Fill(numpy.round(p[0]), numpy.round(p[1]), b[2])
        barray.append(b[1])
      if abs(p[0]) < 0.001:
        harray['B_X [Y%Z]'].Fill(numpy.round(p[2]), numpy.round(p[1]), b[0])
        harray['B_Y [Y%Z]'].Fill(numpy.round(p[2]), numpy.round(p[1]), b[1])
        harray['B_Z [Y%Z]'].Fill(numpy.round(p[2]), numpy.round(p[1]), b[2])
        barray.append(b[1])
      if abs(p[1]) < 0.001:
        harray['B_X [Z%X]'].Fill(numpy.round(p[0]), numpy.round(p[2]), b[0])
        harray['B_Y [Z%X]'].Fill(numpy.round(p[0]), numpy.round(p[2]), b[1])
        harray['B_Z [Z%X]'].Fill(numpy.round(p[0]), numpy.round(p[2]), b[2])
        barray.append(b[1])
    for h in harray.values():
      h.SetStats(0)
      # h.GetZaxis().SetRangeUser(-1.112, -0.786)
    print(numpy.min(barray))
    print(numpy.max(barray))
    c1 = ROOT.TCanvas('c1', 'c1', 1200, 800)
    c1.Divide(2, 2)
    c1.cd(1).SetGrid()
    harray['B_X [Y%X]'].Draw('colz')
    c1.cd(2).SetGrid()
    harray['B_X [Y%Z]'].Draw('colz')
    c1.cd(3).SetGrid()
    harray['B_X [Z%X]'].Draw('colz')
    c1.Print('analyzer/calc_bx.pdf')
    c1.cd(1).SetGrid()
    harray['B_Y [Y%X]'].Draw('colz')
    c1.cd(2).SetGrid()
    harray['B_Y [Y%Z]'].Draw('colz')
    c1.cd(3).SetGrid()
    harray['B_Y [Z%X]'].Draw('colz')
    c1.Print('analyzer/calc_by.pdf')
    c1.cd(1).SetGrid()
    harray['B_Z [Y%X]'].Draw('colz')
    c1.cd(2).SetGrid()
    harray['B_Z [Y%Z]'].Draw('colz')
    c1.cd(3).SetGrid()
    harray['B_Z [Z%X]'].Draw('colz')
    c1.Print('analyzer/calc_bz.pdf')

  #____________________________________________________________________________
  def get_field(self, position):
    calc = __class__.field_map[(numpy.round(position[0]),
                                numpy.round(position[1]),
                                numpy.round(position[2]))]
    return calc
    min_dist = 1e10
    for elm in __class__.field_map:
      p = numpy.array(elm[:3])
      d = numpy.linalg.norm(p - position)
      if d < 0.1:
        print(position, p, d)
        return elm[3:]
      if d < min_dist:
        min_dist = d
        min_pos = p
        calc = elm[3:]
    print(min_dist, min_pos)
    return calc
