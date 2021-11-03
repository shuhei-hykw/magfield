#!/usr/bin/env python3

import argparse
import datetime
import math
import numpy
import os

import calculation_map
import fieldmap_manager
import param_manager
import utility

parsed = None
carray = dict()
harray = dict()

cut_for_nmr = False

#______________________________________________________________________________
def add_canvas(key):
  import ROOT
  global carray
  carray[key] = ROOT.TCanvas(key, key, 0, 0, 1000, 800)

#______________________________________________________________________________
def add_hist(key, hset):
  import ROOT
  global harray
  if len(hset) == 1:
    harray[key] = ROOT.TH1F(key, key,
                            hset[0][0], hset[0][1], hset[0][2])
  elif len(hset) == 2:
    harray[key] = ROOT.TH2F(key, key,
                            hset[0][0], hset[0][1], hset[0][2],
                            hset[1][0], hset[1][1], hset[1][2])
  else:
    raise Exception(f'add_hist() invalid args: key = {key}, hset = {hset}')

#______________________________________________________________________________
def analyze():
  import ROOT
  ROOT.gROOT.SetBatch(parsed.batch)
  ROOT.gErrorIgnoreLevel = ROOT.kFatal
  # ROOT.gStyle.SetOptStat(1111110)
  ROOT.gStyle.SetPadLeftMargin(0.15)
  ROOT.gStyle.SetOptStat(1110)
  # ROOT.gStyle.SetOptFit(1)
  ROOT.gStyle.SetStatX(0.9)
  ROOT.gStyle.SetStatY(0.9)
  ROOT.gStyle.SetStatW(0.3)
  ROOT.gStyle.SetStatH(0.2)
  ROOT.gStyle.SetPalette(ROOT.kBird)
  # ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator)
  # ROOT.gStyle.SetPalette(ROOT.kGreyScale)
  ROOT.gStyle.SetNumberContours(255)
  garray = dict()
  add_canvas('raw_trend_1')
  add_canvas('raw_trend_2')
  add_canvas('temp_corr_1')
  add_canvas('temp_corr_2')
  add_canvas('temp_corr_3')
  add_canvas('temp_corr_4')
  add_canvas('Corrected Ref. Field')
  add_canvas('maxwell')
  add_canvas('Ref. Field % NMR')
  add_canvas('Maxwell Equation%Temp')
  add_canvas('Maxwell Equation%Ref')
  add_canvas('dStep')
  add_canvas('temp dep')
  add_canvas('B Step')
  add_canvas('Ref ')
  add_canvas('Residual')
  add_canvas('ResidualRatio')
  range_nmr = [50, 1.0011, 1.00145]
  # range_ref = [50, -0.71505, -0.71005]
  range_ref = [20, -0.7135, -0.7115]
  # range_temp = [200, 20.05, 40.05]
  range_temp = [100, 24.05, 34.05]
  range_bx = [200, -0.2, 0.2]
  range_by = [50, -1.0055, -1.0032]
  # range_by = [1600, -1.006, -0.990]
  range_bz = [200, -0.2, 0.2]
  add_hist('Ref. Field % NMR', [range_nmr, range_ref])
  add_hist('Ref. Field % Temp. Coil', [range_temp, range_ref])
  add_hist('Ref. Field % Temp. Room', [range_temp, range_ref])
  add_hist('Ref. Field % B_{y}', [range_by, range_ref])
  add_hist('NMR % Temp. Coil', [range_temp, range_nmr])
  add_hist('NMR % Temp. Room', [range_temp, range_nmr])
  add_hist('B_{x} % NMR', [range_nmr, range_bx])
  add_hist('B_{y} % NMR', [range_nmr, range_by])
  add_hist('B_{z} % NMR', [range_nmr, range_bz])
  add_hist('B_{x} % Temp. Coil', [range_temp, range_bx])
  add_hist('B_{y} % Temp. Coil', [range_temp, range_by])
  add_hist('B_{z} % Temp. Coil', [range_temp, range_bz])
  add_hist('B_{x} % Temp. Room', [range_temp, range_bx])
  add_hist('B_{y} % Temp. Room', [range_temp, range_by])
  add_hist('B_{z} % Temp. Room', [range_temp, range_bz])
  # harray.append(ROOT.TH1F('h_ref_field', 'Ref. Field',
  #                         50, -0.71505, -0.71005)) # 2
  # harray.append(ROOT.TH1F('h_bx', 'Bx', 200, -0.2, 0.2)) # 4
  # harray.append(ROOT.TH1F('h_by', 'By', 200, -1.2, -0.8)) # 5
  # harray.append(ROOT.TH1F('h_bz', 'Bz', 200, -0.2, 0.2)) # 6
  # harray.append(ROOT.TH1F('h_bv', 'Bv', 200, 0.8, 1.2)) # 7
  maxwell_range = [200, -0.01, 0.01]
  add_hist('divB', [maxwell_range])
  add_hist('(rotB)_{x}', [maxwell_range])
  add_hist('(rotB)_{y}', [maxwell_range])
  add_hist('(rotB)_{z}', [maxwell_range])
  range_res = [200, -0.1, 0.1]
  add_hist('Res B_{x}', [range_res])
  add_hist('Res B_{y}', [range_res])
  add_hist('Res B_{z}', [range_res])
  add_hist('Res B', [[100,0,0.1]])
  range_res = [200, -0.1, 0.1]
  add_hist('Res/Calc B_{x}', [range_res])
  add_hist('Res/Calc B_{y}', [range_res])
  add_hist('Res/Calc B_{z}', [range_res])
  add_hist('Res/Calc B', [[100,0,0.1]])
  # harray.append(ROOT.TH1F('h_rotBx', '(rotB)_{x}', 160, -tmm, tmm)) # 9
  # harray.append(ROOT.TH1F('h_rotBy', '(rotB)_{y}', 160, -tmm, tmm)) # 10
  # harray.append(ROOT.TH1F('h_rotBz', '(rotB)_{z}', 160, -tmm, tmm)) # 11
  for i, t in enumerate(['Y%X', 'Y%Z', 'Z%X']):
    add_canvas(f'B Field {t}')
    # harray.append(ROOT.TH2F(f'h_bx_{t}', f'Bx {t}',
    #                         80, -400-5, 400-5, 80, -400-5, 400-5)) # 12,16,20
    # harray.append(ROOT.TH2F(f'h_by_{t}', f'By {t}',
    #                         80, -400-5, 400-5, 80, -400-5, 400-5)) # 13,17,21
    # # harray[-1].GetZaxis().SetRangeUser(-1.1, -0.9)
    # harray.append(ROOT.TH2F(f'h_bz_{t}', f'Bz {t}',
    #                         80, -400-5, 400-5, 80, -400-5, 400-5)) # 14,18,22
    # # harray[-1].GetZaxis().SetRangeUser(-0.016, -0.006)
    # harray.append(ROOT.TH2F(f'h_b_{t}', f'B {t}',
    #                         80, -400-5, 400-5, 80, -400-5, 400-5)) # 15,19,23
    # # harray[-1].GetZaxis().SetRangeUser(0.9, 1.1)
  # harray.append(ROOT.TH2F('h_divB_temp2', 'divB%Temp',
  #                         100, 20.05, 40.05, 160, -tmm, tmm)) # 24
  # harray.append(ROOT.TH2F('h_rotBx_temp2', '(rotB)_{x}%Temp',
  #                         100, 20.05, 40.05, 160, -tmm, tmm)) # 25
  # harray.append(ROOT.TH2F('h_rotBy_temp2', '(rotB)_{y}%Temp',
  #                         100, 20.05, 40.05, 160, -tmm, tmm)) # 26
  # harray.append(ROOT.TH2F('h_rotBz_temp2', '(rotB)_{z}%Temp',
  #                         100, 20.05, 40.05, 160, -tmm, tmm)) # 27
  # harray.append(ROOT.TH2F('h_divB_ref', 'divB%Ref',
  #                         50, -0.71505, -0.71005,  80, -tmm, tmm)) # 28
  # harray.append(ROOT.TH2F('h_rotBx_ref', '(rotB)_{x}%Ref',
  #                         50, -0.71505, -0.71005,  80, -tmm, tmm)) # 29
  # harray.append(ROOT.TH2F('h_rotBy_ref', '(rotB)_{y}%Ref',
  #                         50, -0.71505, -0.71005,  80, -tmm, tmm)) # 30
  # harray.append(ROOT.TH2F('h_rotBz_ref', '(rotB)_{z}%Ref',
  #                         50, -0.71505, -0.71005,  80, -tmm, tmm)) # 31
  range_pos = [80, -400-5, 400-5]
  for i, t in enumerate(['X', 'Y', 'Z']):
    add_canvas(f'Maxwell Equation%{t}')
    add_canvas(f'B_Field_{t}')
    for ii, tt in enumerate(['Y%X', 'Y%Z', 'Z%X']):
      add_hist(f'B_{t} [{tt}]', [range_pos, range_pos])
    # harray.append(ROOT.TH2F(f'h_divB_{t}', f'divB%{t}',
    #                         80, -400-5, 400-5,  80, -tmm, tmm)) # 32
    # harray.append(ROOT.TH2F(f'h_rotBx_{t}', f'(rotB)_{{x}}%{t}',
    #                         80, -400-5, 400-5,  80, -tmm, tmm)) # 33
    # harray.append(ROOT.TH2F(f'h_rotBy_{t}', f'(rotB)_{{y}}%{t}',
    #                         80, -400-5, 400-5,  80, -tmm, tmm)) # 34
    # harray.append(ROOT.TH2F(f'h_rotBz_{t}', f'(rotB)_{{z}}%{t}',
    #                         80, -400-5, 400-5,  80, -tmm, tmm)) # 35
  bmin = [0.0065, -1.002, -0.0165]
  bmax = [0.0075, -0.997, -0.0155]
  # for i, t in enumerate(['X', 'Y', 'Z']):
  #   harray.append(ROOT.TH2F(f'h_b{t}_temp1', f'B_{{{t}}} % Temp. Coil',
  #                           200, 20.05, 40.05, 50, bmin[i], bmax[i])) # 44
  # for i, t in enumerate(['X', 'Y', 'Z']):
  #   harray.append(ROOT.TH2F(f'h_b{t}_temp2', f'B_{{{t}}} % Temp. Room',
  #                           200, 20.05, 40.05, 50, bmin[i], bmax[i])) # 45
  # for i in range(4):
  #   harray[i + 8].GetXaxis().SetTitle('[T/mm]')
  # harray[3].SetLineColor(ROOT.kRed + 1)
  garray['Ref. Field'] = ROOT.TGraph()
  garray['NMR'] = ROOT.TGraph()
  garray['Temp. Coil'] = ROOT.TGraph()
  garray['Temp. Room'] = ROOT.TGraph()
  garray['Hall Probe B_{x}'] = ROOT.TGraph()
  garray['Hall Probe B_{y}'] = ROOT.TGraph()
  garray['Hall Probe B_{z}'] = ROOT.TGraph()
  # garray[0].SetMarkerColor(ROOT.kBlue + 1)
  # garray[1].SetTitle('Ref. Field Corrected')
  # garray[1].SetMarkerColor(ROOT.kRed + 1)
  # garray[2].GetYaxis().SetTitle('[degC]')
  # garray[2].SetMarkerColor(ROOT.kRed + 1)
  # garray[3].SetMarkerColor(ROOT.kRed + 1)
  # garray[4].SetTitle('Ref. Field')
  # garray[4].SetMarkerColor(ROOT.kBlue + 1)
  # garray[5].SetTitle('Temp. Room')
  # garray[5].GetYaxis().SetTitle('[degC]')
  # garray[5].SetMarkerColor(ROOT.kRed + 1)
  # garray[6].SetTitle('B_{x}')
  # garray[7].SetTitle('B_{y}')
  # garray[8].SetTitle('B_{z}')
  # garray[9].SetTitle('B_{x}')
  # garray[10].SetTitle('B_{y}')
  # garray[11].SetTitle('B_{z}')
  # garray[12].SetTitle('dB_{x}')
  # garray[13].SetTitle('dB_{y}')
  # garray[14].SetTitle('dB_{z}')
  # garray[16].SetTitle('Hall Probe B_{x}')
  # garray[17].SetTitle('Hall Probe B_{y}')
  # garray[18].SetTitle('Hall Probe B_{z}')
  # garray[19].SetTitle('Ref. Field % NMR')
  for key, h in harray.items():
    h.SetLineColor(ROOT.kBlue + 1)
    h.SetLineWidth(2)
    xa = h.GetXaxis()
    ya = h.GetYaxis()
    if '% Temp' in key:
      xa.SetTitle('[#circC]')
      ya.SetTitle('[T]')
    elif 'divB' in key or 'rotB' in key:
      xa.SetTitle('[T/mm]')
    elif '[Z%X]' in key:
      xa.SetTitle('x [mm]')
      ya.SetTitle('z [mm]')
    elif '[Y%Z]' in key:
      xa.SetTitle('z [mm]')
      ya.SetTitle('y [mm]')
    elif '[Z%X]' in key:
      xa.SetTitle('x [mm]')
      ya.SetTitle('z [mm]')
    elif '%' in key:
      xa.SetTitle('[T]')
      ya.SetTitle('[T]')
    elif 'B' in key:
      xa.SetTitle('[T]')
  for key, g in garray.items():
    g.SetTitle(key)
    g.SetLineWidth(2)
    g.SetMarkerSize(0.4)
    g.SetMarkerStyle(8)
    xa = g.GetXaxis()
    ya = g.GetYaxis()
    if '%' not in key:
      xa.SetTimeDisplay(True)
      xa.SetLabelOffset(0.04)
      # xa.SetLabelSize(0.04)
      xa.SetTimeFormat('#splitline{%Y/%m/%d}{  %H:%M:%S}')
      xa.SetNdivisions(-503)
      xa.SetTimeOffset(0, 'jpn')
      if 'temp' in key.lower():
        ya.SetTitle('[#circC]')
      else:
        ya.SetTitle('[T]')
    if 'Temp' in key:
      g.SetLineColor(ROOT.kRed + 1)
      g.SetMarkerColor(ROOT.kRed + 1)
    if 'ref' in key.lower():
      g.SetMarkerColor(ROOT.kBlack)
    if 'hall' in key.lower():
      g.SetLineColor(ROOT.kBlue + 1)
      g.SetMarkerColor(ROOT.kBlue + 1)
  ''' cut '''
  field_map = field_man.field_map
  # if cut_for_nmr:
  #   field_map = { k:v for k, v in field_map.items()
  #                 if v.bref < -0.7125 }
  ''' first loop '''
  ipoint = 0
  for key, elm in field_map.items():
    if len(elm.data) >= 13:
      garray['Ref. Field'].SetPoint(ipoint, elm.unix_time, elm.bref)
      garray['Temp. Coil'].SetPoint(ipoint, elm.unix_time, elm.temp1)
      garray['Temp. Room'].SetPoint(ipoint, elm.unix_time, elm.temp2)
      if cut_for_nmr and elm.bref > -0.71245:
        continue
      harray['Ref. Field % NMR'].Fill(elm.nmr, elm.bref)
      harray['Ref. Field % B_{y}'].Fill(elm.b.Y(), elm.bref)
      harray['Ref. Field % Temp. Coil'].Fill(elm.temp1, elm.bref)
      harray['Ref. Field % Temp. Room'].Fill(elm.temp2, elm.bref)
      harray['NMR % Temp. Coil'].Fill(elm.temp1, elm.nmr)
      harray['NMR % Temp. Room'].Fill(elm.temp2, elm.nmr)
      harray['B_{x} % NMR'].Fill(elm.nmr, elm.b.X())
      harray['B_{y} % NMR'].Fill(elm.nmr, elm.b.Y())
      harray['B_{z} % NMR'].Fill(elm.nmr, elm.b.Z())
      harray['B_{x} % Temp. Coil'].Fill(elm.temp1, elm.b.X())
      harray['B_{x} % Temp. Room'].Fill(elm.temp2, elm.b.X())
      harray['B_{y} % Temp. Coil'].Fill(elm.temp1, elm.b.Y())
      harray['B_{y} % Temp. Room'].Fill(elm.temp2, elm.b.Y())
      harray['B_{z} % Temp. Coil'].Fill(elm.temp1, elm.b.Z())
      harray['B_{z} % Temp. Room'].Fill(elm.temp2, elm.b.Z())
      ipoint += 1
    # harray[2].Fill(elm.bref)
  ''' fit '''
  key = 'Ref. Field % Temp. Room'
  f1 = ROOT.TF1('f1', 'pol2')
  harray[key].Draw()
  harray[key].Fit('f1', '')
  key = 'Ref. Field % B_{y}'
  f2 = ROOT.TF1('f2', 'pol1')
  # f2.FixParameter(0, 0)
  # f2.SetParameter(1, 1.16)
  # f2.SetParameter(2, -1.8)
  # nmr_mean = harray[key].GetMean(1)
  bref_mean = harray[key].GetMean(2)
  print(f'bref_neam = {bref_mean}')
  harray[key].Draw()
  # harray[key].Fit('f2', '')
  key = 'B_{y} % NMR'
  f3 = ROOT.TF1('f3', 'pol1')
  harray[key].Draw()
  #f3.FixParameter(0, 0)
  # harray[key].Fit('f3', '')
  ROOT.gPad.Clear()
  ''' second loop '''
  ipoint = 0
  second_data = False
  for key, elm in field_map.items():
    if len(elm.data) >= 13:
      if cut_for_nmr and elm.bref > -0.71245:
        continue
      garray['NMR'].SetPoint(ipoint, elm.unix_time, elm.nmr)
      garray['Hall Probe B_{x}'].SetPoint(ipoint, elm.unix_time, elm.b.X())
      garray['Hall Probe B_{y}'].SetPoint(ipoint, elm.unix_time, elm.b.Y())
      garray['Hall Probe B_{z}'].SetPoint(ipoint, elm.unix_time, elm.b.Z())
      harray['B_X [Y%X]'].Fill(elm.p.X(), elm.p.Y(), elm.b.X())
      harray['B_X [Y%Z]'].Fill(elm.p.Z(), elm.p.Y(), elm.b.X())
      harray['B_X [Z%X]'].Fill(elm.p.X(), elm.p.Z(), elm.b.X())

      if abs(elm.p.Z()) < 0.1:
        harray['B_Y [Y%X]'].Fill(elm.p.X(), elm.p.Y(), elm.b.Y())
      if abs(elm.p.X()) < 0.1:
        harray['B_Y [Y%Z]'].Fill(elm.p.Z(), elm.p.Y(), elm.b.Y())
      if abs(elm.p.Y()) < 0.1:
        harray['B_Y [Z%X]'].Fill(elm.p.X(), elm.p.Z(), elm.b.Y())

      harray['B_Z [Y%X]'].Fill(elm.p.X(), elm.p.Y(), elm.b.Z())
      harray['B_Z [Y%Z]'].Fill(elm.p.Z(), elm.p.Y(), elm.b.Z())
      harray['B_Z [Z%X]'].Fill(elm.p.X(), elm.p.Z(), elm.b.Z())
      bcalc = numpy.array(calc_map.get_field(elm.p))
      cb = elm.b #* abs(elm.bref / 0.713)
      res = cb - bcalc
      harray['Res B_{x}'].Fill(res[0])
      harray['Res B_{y}'].Fill(res[1])
      harray['Res B_{z}'].Fill(res[2])
      harray['Res B'].Fill(numpy.linalg.norm(res))
      harray['Res/Calc B_{x}'].Fill(res[0]/bcalc[0])
      harray['Res/Calc B_{y}'].Fill(res[1]/bcalc[1])
      harray['Res/Calc B_{z}'].Fill(res[2]/bcalc[2])
      harray['Res/Calc B'].Fill(numpy.linalg.norm(res)/numpy.linalg.norm(bcalc))

      # garray[19].SetPoint(ipoint, elm.nmr, elm.bref)
      # if not second_data:
      #   garray[6].SetPoint(elm.step, elm.step, elm.b.X())
      #   garray[7].SetPoint(elm.step, elm.step, elm.b.Y())
      #   garray[8].SetPoint(elm.step, elm.step, elm.b.Z())
      #   if elm.step == 1067:
      #     second_data = True
      # else:
      #   garray[9].SetPoint(ipoint-1070, 1068-elm.step, elm.b.X())
      #   garray[10].SetPoint(ipoint-1070, 1068-elm.step, elm.b.Y())
      #   garray[11].SetPoint(ipoint-1070, 1068-elm.step, elm.b.Z())
        # garray[12].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.X() - garray[6].GetY()[1068-elm.step])
        # garray[13].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.Y() - garray[7].GetY()[1068-elm.step])
        # garray[14].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.Z() - garray[8].GetY()[1068-elm.step])
      # harray[3].Fill(cbref)
      # harray[44].Fill(elm.temp1, elm.b.X())
      # harray[45].Fill(elm.temp1, elm.b.Y())
      # harray[46].Fill(elm.temp1, elm.b.Z())
      # harray[47].Fill(elm.temp2, elm.b.X())
      # harray[48].Fill(elm.temp2, elm.b.Y())
      # harray[49].Fill(elm.temp2, elm.b.Z())
      ipoint += 1
    # bscale = elm.bref/bref_mean
    # harray[4].Fill(elm.b.X())
    # harray[5].Fill(elm.b.Y())
    # harray[6].Fill(elm.b.Z())
    # harray[7].Fill(elm.b.Mag())
    harray['divB'].Fill(elm.divB)
    harray['(rotB)_{x}'].Fill(elm.rotBx)
    harray['(rotB)_{y}'].Fill(elm.rotBy)
    harray['(rotB)_{z}'].Fill(elm.rotBz)
    # harray[9].Fill(elm.rotBx)
    # harray[10].Fill(elm.rotBy)
    # harray[11].Fill(elm.rotBz)
    # if abs(elm.p.Z())<0.1:
    #   harray[12].Fill(elm.p.X(), elm.p.Y(), elm.b.X())
    #   harray[13].Fill(elm.p.X(), elm.p.Y(), elm.b.Y())
    #   harray[14].Fill(elm.p.X(), elm.p.Y(), elm.b.Z())
    #   harray[15].Fill(elm.p.X(), elm.p.Y(), elm.b.Mag())
    # if abs(elm.p.X())<0.1:
    #   harray[16].Fill(elm.p.Z(), elm.p.Y(), elm.b.X())
    #   harray[17].Fill(elm.p.Z(), elm.p.Y(), elm.b.Y())
    #   harray[18].Fill(elm.p.Z(), elm.p.Y(), elm.b.Z())
    #   harray[19].Fill(elm.p.Z(), elm.p.Y(), elm.b.Mag())
    # if abs(elm.p.Y())<0.1:
    #   harray[20].Fill(elm.p.X(), elm.p.Z(), elm.b.X())
    #   harray[21].Fill(elm.p.X(), elm.p.Z(), elm.b.Y())
    #   harray[22].Fill(elm.p.X(), elm.p.Z(), elm.b.Z())
    #   harray[23].Fill(elm.p.X(), elm.p.Z(), elm.b.Mag())
    # harray[24].Fill(elm.temp2, elm.divB)
    # harray[25].Fill(elm.temp2, elm.rotBx)
    # harray[26].Fill(elm.temp2, elm.rotBy)
    # harray[27].Fill(elm.temp2, elm.rotBz)
    # harray[28].Fill(elm.bref, elm.divB)
    # harray[29].Fill(elm.bref, elm.rotBx)
    # harray[30].Fill(elm.bref, elm.rotBy)
    # harray[31].Fill(elm.bref, elm.rotBz)
    # for i in range(3):
    #   harray[32 + i*4].Fill(elm.p[i], elm.divB)
    #   harray[33 + i*4].Fill(elm.p[i], elm.rotBx)
    #   harray[34 + i*4].Fill(elm.p[i], elm.rotBy)
    #   harray[35 + i*4].Fill(elm.p[i], elm.rotBz)
      # if abs(elm.p.X() - 90)<0.1:
      #   utility.print_info(f'{elm.b.Z()}')
  ''' Draw '''
  pdf_name = param_man.get('output_pdf')
  # pdf_dir = os.path.dirname(pdf_name)
  # ROOT.gPad.Print(pdf_name + '[')
  # key = 'raw_trend_1'
  # carray[key].Divide(2, 2)
  # for i in range(7):
  #   carray[key].cd(i + 1).SetGrid()
  #   if i == 0: garray['Ref. Field'].Draw('AL')
  #   if i == 1: garray['NMR'].Draw('AL')
  #   if i == 2: garray['Temp. Coil'].Draw('AL')
  #   if i == 3: garray['Temp. Room'].Draw('AL')
  #   ROOT.gPad.Modified()
  #   ROOT.gPad.Update()
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'raw_trend_2'
  # carray[key].Divide(2, 2)
  # for i in range(7):
  #   carray[key].cd(i + 1).SetGrid()
  #   if i == 0: garray['Hall Probe B_{x}'].Draw('AL')
  #   if i == 1: garray['Hall Probe B_{y}'].Draw('AL')
  #   if i == 2: garray['Hall Probe B_{z}'].Draw('AL')
  #   ROOT.gPad.Modified()
  #   ROOT.gPad.Update()
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'temp_corr_1'
  # carray[key].Divide(2, 3)
  # carray[key].cd(1).SetGrid()
  # harray['Ref. Field % NMR'].Draw('colz')
  # carray[key].cd(2).SetGrid()

  # carray[key].cd(3).SetGrid()
  # harray['Ref. Field % B_{y}'].Draw('colz')
  # carray[key].cd(4).SetGrid()

  # # carray[key].cd(5).SetGrid()
  # # harray['Ref. Field % Temp. Coil'].Draw('colz')
  # # carray[key].cd(6).SetGrid()
  # # harray['CRef. Field % Temp. Coil'].Draw('colz')
  # carray[key].cd(5).SetGrid()
  # harray['Ref. Field % Temp. Room'].Draw('colz')
  # carray[key].cd(6).SetGrid()

  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'temp_corr_2'
  # carray[key].Divide(1, 2)
  # carray[key].cd(1).SetGrid()
  # harray['NMR % Temp. Coil'].Draw('colz')
  # carray[key].cd(2).SetGrid()
  # harray['NMR % Temp. Room'].Draw('colz')
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'temp_corr_3'
  # carray[key].Divide(2, 3)
  # carray[key].cd(1).SetGrid()
  # harray['B_{y} % NMR'].Draw('colz')
  # carray[key].cd(2).SetGrid()

  # carray[key].cd(3).SetGrid()
  # harray['B_{y} % Temp. Coil'].Draw('colz')
  # carray[key].cd(4).SetGrid()

  # carray[key].cd(5).SetGrid()
  # harray['B_{y} % Temp. Room'].Draw('colz')
  # carray[key].cd(6).SetGrid()

  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'temp_corr_4'
  # carray[key].Divide(2, 3)
  # carray[key].cd(1).SetGrid()
  # harray['B_{x} % NMR'].Draw('colz')
  # carray[key].cd(2).SetGrid()

  # carray[key].cd(3).SetGrid()
  # harray['B_{x} % Temp. Coil'].Draw('colz')
  # carray[key].cd(4).SetGrid()

  # carray[key].cd(5).SetGrid()
  # harray['B_{x} % Temp. Room'].Draw('colz')
  # carray[key].cd(6).SetGrid()

  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'maxwell'
  # carray[key].Divide(2, 2)
  # carray[key].cd(1).SetGrid()
  # harray['divB'].Draw('colz')
  # carray[key].cd(2).SetGrid()
  # harray['(rotB)_{x}'].Draw('colz')
  # carray[key].cd(3).SetGrid()
  # harray['(rotB)_{y}'].Draw('colz')
  # carray[key].cd(4).SetGrid()
  # harray['(rotB)_{z}'].Draw('colz')
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # for i, t in enumerate(['X', 'Y', 'Z']):
  #   key = f'B_Field_{t}'
  #   carray[key].Divide(2, 2)
  #   carray[key].cd(1).SetGrid()
  #   harray[f'B_{t} [Y%X]'].Draw('colz')
  #   carray[key].cd(2).SetGrid()
  #   harray[f'B_{t} [Y%Z]'].Draw('colz')
  #   carray[key].cd(3).SetGrid()
  #   harray[f'B_{t} [Z%X]'].Draw('colz')
  #   carray[key].Print(pdf_name)
  #   carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'Residual'
  # carray[key].Divide(2, 2)
  # carray[key].cd(1).SetGrid()
  # harray['Res B_{x}'].Draw('colz')
  # carray[key].cd(2).SetGrid()
  # harray['Res B_{y}'].Draw('colz')
  # carray[key].cd(3).SetGrid()
  # harray['Res B_{z}'].Draw('colz')
  # # carray[key].cd(4).SetGrid()
  # # harray['Res B'].Draw('colz')
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # key = 'ResidualRatio'
  # carray[key].Divide(2, 2)
  # carray[key].cd(1).SetGrid()
  # harray['Res/Calc B_{x}'].Draw('colz')
  # carray[key].cd(2).SetGrid()
  # harray['Res/Calc B_{y}'].Draw('colz')
  # carray[key].cd(3).SetGrid()
  # harray['Res/Calc B_{z}'].Draw('colz')
  # # carray[key].cd(4).SetGrid()
  # # harray['Res. B'].Draw('colz')
  # carray[key].Print(pdf_name)
  # carray[key].Print(os.path.join(pdf_dir, key + '.pdf'))
  # # for i in range(3):
  # #   carray[15].cd(2*i + 1).SetGrid()
  # #   garray[i + 6].Draw('AL')
  # #   garray[i + 9].Draw('L')
  # #   ROOT.gPad.Modified()
  # #   ROOT.gPad.Update()
  # #   carray[15].cd(2*i + 2).SetGrid()
  # #   garray[i + 12].Draw('AL')
  # #   ROOT.gPad.Modified()
  # #   ROOT.gPad.Update()
  # # carray[15].Print(pdf_name)
  # # for j in range(2):
  # #   carray[j + 14].Divide(2, 2)
  # #   for i in range(4):
  # #     carray[j + 14].cd(i + 1).SetGrid()
  # #     harray[j if i == 3 else i + 44 + j*3].Draw('colz')
  # #     ROOT.gPad.Modified()
  # #     ROOT.gPad.Update()
  # #   carray[j + 14].Print(pdf_name)
  # # #carray[2].Divide(1, 2)
  # # carray[2].cd(0).SetGrid()
  # # # ymax = max(harray[2].GetMaximum(), harray[3].GetMaximum())
  # # # harray[2].SetMaximum(ymax * 1.05)
  # # harray[3].Draw()
  # # harray[2].Draw('same')
  # # for i in range(2):
  # #   stddev = harray[i + 2].GetStdDev()
  # #   mean = harray[i + 2].GetMean()
  # #   if mean != 0:
  # #     utility.print_info(f'ANA  ref field stddev = {stddev:.3e} ' +
  # #                        f'({abs(stddev/mean)*100:.4f}%)')
  # # # harray[3].Fit('gaus', '', '')
  # # carray[2].Print(pdf_name)
  # # carray[3].Divide(2, 2)
  # # for i in range(4):
  # #   carray[3].cd(i + 1).SetGrid()
  # #   harray[i + 4].Draw()
  # # carray[3].Print(pdf_name)
  # # carray[4].Divide(2, 2)
  # # for i in range(4):
  # #   carray[4].cd(i + 1).SetGrid()
  # #   # ROOT.gPad.SetLogy()
  # #   harray[i + 8].Draw()
  # #   # harray[i + 8].Fit('gaus')
  # #   text = ROOT.TText()
  # # carray[4].Print(pdf_name)
  # # carray[8].Divide(2, 2)
  # # for i in range(4):
  # #   carray[8].cd(i + 1).SetGrid()
  # #   harray[i + 24].Draw('colz')
  # # carray[8].Print(pdf_name)
  # # carray[9].Divide(2, 2)
  # # for i in range(4):
  # #   carray[9].cd(i + 1).SetGrid()
  # #   harray[i + 28].Draw('colz')
  # # carray[9].Print(pdf_name)
  # # for j in range(3):
  # #   carray[10 + j].Divide(2, 2)
  # #   for i in range(4):
  # #     carray[10 + j].cd(i + 1).SetGrid()
  # #     harray[i + 32 + j * 4].Draw('colz')
  # #   carray[10 + j].Print(pdf_name)
  # # for j in range(3):
  # #   carray[j + 5].Divide(2, 2)
  # #   for i in range(4):
  # #     carray[j + 5].cd(i + 1).SetGrid()
  # #     ROOT.gPad.SetRightMargin(0.15)
  # #     # harray[i + 12].GetZaxis().SetTitle('[T]')
  # #     harray[i + j * 4 + 12].SetStats(False)
  # #     harray[i + j * 4 + 12].Draw('colz')
  # #   carray[j + 5].Print(pdf_name)
  # ROOT.gPad.Print(pdf_name + ']')
  f = ROOT.TFile('bfield.root', 'RECREATE')
  c1 = ROOT.TCanvas('c1', 'c1', 1600, 400);
  c1.Divide(4, 1)
  c1.cd(1)
  harray['B_Y [Z%X]'].Draw('colz')
  harray['B_Y [Z%X]'].Clone('h1').Write()
  c1.cd(2)
  harray['B_Y [Y%Z]'].Draw('colz')
  harray['B_Y [Y%Z]'].Clone('h2').Write()
  c1.cd(3)
  harray['divB'].Draw('colz')
  harray['divB'].Clone('h3').Write()
  c1.cd(4)
  harray['(rotB)_{x}'].Draw('colz')
  harray['(rotB)_{x}'].Clone('h4').Write()
  f.Write()
  f.Close()
  c1.Print(pdf_name)
  if not ROOT.gROOT.IsBatch():
    ROOT.TPython.Prompt()

#______________________________________________________________________________
def make_root_file():
  import ROOT
  ROOT.gROOT.SetBatch()
  # ROOT.gErrorIgnoreLevel = ROOT.kFatal
  f = ROOT.TFile('bfield.root', 'RECREATE')
  tree = ROOT.TTree('tree', 'tree of fieldmap')
  p = ROOT.TVector3()
  b = ROOT.TVector3()
  tree.Branch('p', p)
  tree.Branch('b', b)
  ''' cut '''
  field_map = field_man.field_map
  # if cut_for_nmr:
  #   field_map = { k:v for k, v in field_map.items()
  #                 if v.bref < -0.7125 }
  ''' first loop '''
  ipoint = 0
  for key, elm in field_map.items():
    if len(elm.data) >= 13:
      # garray['Ref. Field'].SetPoint(ipoint, elm.unix_time, elm.bref)
      # garray['Temp. Coil'].SetPoint(ipoint, elm.unix_time, elm.temp1)
      # garray['Temp. Room'].SetPoint(ipoint, elm.unix_time, elm.temp2)
      if cut_for_nmr and elm.bref > -0.71245:
        continue
      # harray['Ref. Field % NMR'].Fill(elm.nmr, elm.bref)
      # harray['Ref. Field % B_{y}'].Fill(elm.b.Y(), elm.bref)
      # harray['Ref. Field % Temp. Coil'].Fill(elm.temp1, elm.bref)
      # harray['Ref. Field % Temp. Room'].Fill(elm.temp2, elm.bref)
      # harray['NMR % Temp. Coil'].Fill(elm.temp1, elm.nmr)
      # harray['NMR % Temp. Room'].Fill(elm.temp2, elm.nmr)
      # harray['B_{x} % NMR'].Fill(elm.nmr, elm.b.X())
      # harray['B_{y} % NMR'].Fill(elm.nmr, elm.b.Y())
      # harray['B_{z} % NMR'].Fill(elm.nmr, elm.b.Z())
      # harray['B_{x} % Temp. Coil'].Fill(elm.temp1, elm.b.X())
      # harray['B_{x} % Temp. Room'].Fill(elm.temp2, elm.b.X())
      # harray['B_{y} % Temp. Coil'].Fill(elm.temp1, elm.b.Y())
      # harray['B_{y} % Temp. Room'].Fill(elm.temp2, elm.b.Y())
      # harray['B_{z} % Temp. Coil'].Fill(elm.temp1, elm.b.Z())
      # harray['B_{z} % Temp. Room'].Fill(elm.temp2, elm.b.Z())
      ipoint += 1
      if ipoint%100 == 0:
        print(ipoint)
      tree.Write()
  f.Write()
  f.Close()

#______________________________________________________________________________
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('param_file', help='analysis parameter file')
  parser.add_argument('-b', '--batch', action='store_true',
                      help='batch flag')
  # parser.add_argument('-o', '--online', action='store_true',
  #                     help='online flag')
  parsed, unparsed = parser.parse_known_args()
  try:
    param_man = param_manager.ParamManager()
    param_man.initialize(parsed.param_file)
    calc_map = calculation_map.CalcMap()
    field_man = fieldmap_manager.FieldMapManager()
    # analyze()
    make_root_file()
    # calc_map.draw()
  except KeyboardInterrupt:
    pass
