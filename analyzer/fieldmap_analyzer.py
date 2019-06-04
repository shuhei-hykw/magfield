#!/usr/bin/env python3

import argparse
import datetime
import math
import numpy
import os

import fieldmap_manager
import param_manager
import utility

parsed = None

#______________________________________________________________________________
def analyze():
  import ROOT
  ROOT.gROOT.SetBatch(parsed.batch)
  ROOT.gErrorIgnoreLevel = ROOT.kFatal
  # ROOT.gStyle.SetOptStat(1111110)
  ROOT.gStyle.SetOptStat(1110)
  ROOT.gStyle.SetStatX(0.9)
  ROOT.gStyle.SetStatY(0.9)
  ROOT.gStyle.SetStatW(0.3)
  ROOT.gStyle.SetStatH(0.2)
  # ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator)
  # ROOT.gStyle.SetPalette(ROOT.kGreyScale)
  ROOT.gStyle.SetNumberContours(255)
  carray = []
  harray = []
  garray = []
  carray.append(ROOT.TCanvas('c1', 'Temp. Dependence', 0, 0, 800, 800))
  carray.append(ROOT.TCanvas('c2', 'Temp. Correction', 800, 0, 800, 800))
  carray.append(ROOT.TCanvas('c3', 'Corrected Ref. Field', 800, 0, 800, 800))
  carray.append(ROOT.TCanvas('c4', 'B Field', 800, 0, 800, 800))
  carray.append(ROOT.TCanvas('c5', 'Maxwell Equation', 800, 0, 800, 800))
  harray.append(ROOT.TH2F('h_ref_temp1', 'Ref. Field % Temp. Coil',
                          200, 20.05, 40.05, 50, -0.71505, -0.71005)) # 0
  harray.append(ROOT.TH2F('h_ref_temp2', 'Ref. Field % Temp. Valve',
                          200, 20.05, 40.05, 50, -0.71505, -0.71005)) # 1
  harray.append(ROOT.TH1F('h_ref_field', 'Ref. Field',
                          50, -0.71505, -0.71005)) # 2
  harray.append(ROOT.TH1F('h_ref_cfield', 'Ref. CField',
                          50*2, -0.71505, -0.71005)) # 3
  harray.append(ROOT.TH1F('h_bx', 'Bx', 200, -0.2, 0.2)) # 4
  harray.append(ROOT.TH1F('h_by', 'By', 200, -1.2, -0.8)) # 5
  harray.append(ROOT.TH1F('h_bz', 'Bz', 200, -0.2, 0.2)) # 6
  harray.append(ROOT.TH1F('h_bv', 'Bv', 200, 0.8, 1.2)) # 7
  tmm = 0.008
  harray.append(ROOT.TH1F('h_divB', 'divB', 160, -tmm, tmm)) # 8
  harray.append(ROOT.TH1F('h_rotBx', '(rotB)_{x}', 160, -tmm, tmm)) # 9
  harray.append(ROOT.TH1F('h_rotBy', '(rotB)_{y}', 160, -tmm, tmm)) # 10
  harray.append(ROOT.TH1F('h_rotBz', '(rotB)_{z}', 160, -tmm, tmm)) # 11
  for i, t in enumerate(['Y%X', 'Y%Z', 'Z%X']):
    carray.append(ROOT.TCanvas(f'c{i + 6}', f'B Field {t}', 800, 0, 800, 800))
    harray.append(ROOT.TH2F(f'h_bx_{t}', f'Bx {t}',
                            80, -400-5, 400-5, 80, -400-5, 400-5)) # 12,16,20
    harray.append(ROOT.TH2F(f'h_by_{t}', f'By {t}',
                            80, -400-5, 400-5, 80, -400-5, 400-5)) # 13,17,21
    # harray[-1].GetZaxis().SetRangeUser(-1.1, -0.9)
    harray.append(ROOT.TH2F(f'h_bz_{t}', f'Bz {t}',
                            80, -400-5, 400-5, 80, -400-5, 400-5)) # 14,18,22
    # harray[-1].GetZaxis().SetRangeUser(-0.016, -0.006)
    harray.append(ROOT.TH2F(f'h_b_{t}', f'B {t}',
                            80, -400-5, 400-5, 80, -400-5, 400-5)) # 15,19,23
    # harray[-1].GetZaxis().SetRangeUser(0.9, 1.1)
  carray.append(ROOT.TCanvas('c9', 'Maxwell Equation%Temp', 800, 0, 800, 800))
  harray.append(ROOT.TH2F('h_divB_temp2', 'divB%Temp',
                          100, 20.05, 40.05, 160, -tmm, tmm)) # 24
  harray.append(ROOT.TH2F('h_rotBx_temp2', '(rotB)_{x}%Temp',
                          100, 20.05, 40.05, 160, -tmm, tmm)) # 25
  harray.append(ROOT.TH2F('h_rotBy_temp2', '(rotB)_{y}%Temp',
                          100, 20.05, 40.05, 160, -tmm, tmm)) # 26
  harray.append(ROOT.TH2F('h_rotBz_temp2', '(rotB)_{z}%Temp',
                          100, 20.05, 40.05, 160, -tmm, tmm)) # 27
  carray.append(ROOT.TCanvas('c10', 'Maxwell Equation%Ref', 800, 0, 800, 800))
  harray.append(ROOT.TH2F('h_divB_ref', 'divB%Ref',
                          50, -0.71505, -0.71005,  80, -tmm, tmm)) # 28
  harray.append(ROOT.TH2F('h_rotBx_ref', '(rotB)_{x}%Ref',
                          50, -0.71505, -0.71005,  80, -tmm, tmm)) # 29
  harray.append(ROOT.TH2F('h_rotBy_ref', '(rotB)_{y}%Ref',
                          50, -0.71505, -0.71005,  80, -tmm, tmm)) # 30
  harray.append(ROOT.TH2F('h_rotBz_ref', '(rotB)_{z}%Ref',
                          50, -0.71505, -0.71005,  80, -tmm, tmm)) # 31
  for i, t in enumerate(['X', 'Y', 'Z']):
    carray.append(ROOT.TCanvas(f'c{i + 11}',
                               f'Maxwell Equation%{t}', 800, 0, 800, 800))
    harray.append(ROOT.TH2F(f'h_divB_{t}', f'divB%{t}',
                            80, -400-5, 400-5,  80, -tmm, tmm)) # 32
    harray.append(ROOT.TH2F(f'h_rotBx_{t}', f'(rotB)_{{x}}%{t}',
                            80, -400-5, 400-5,  80, -tmm, tmm)) # 33
    harray.append(ROOT.TH2F(f'h_rotBy_{t}', f'(rotB)_{{y}}%{t}',
                            80, -400-5, 400-5,  80, -tmm, tmm)) # 34
    harray.append(ROOT.TH2F(f'h_rotBz_{t}', f'(rotB)_{{z}}%{t}',
                            80, -400-5, 400-5,  80, -tmm, tmm)) # 35
  carray.append(ROOT.TCanvas('c14', 'dStep', 800, 0, 800, 800))
  carray.append(ROOT.TCanvas('c15', 'temp dep', 0, 0, 800, 800))
  bmin = [0.0065, -1.002, -0.0165]
  bmax = [0.0075, -0.997, -0.0155]
  for i, t in enumerate(['X', 'Y', 'Z']):
    harray.append(ROOT.TH2F(f'h_b{t}_temp1', f'B_{{{t}}} % Temp. Coil',
                            200, 20.05, 40.05, 50, bmin[i], bmax[i])) # 44
  for i, t in enumerate(['X', 'Y', 'Z']):
    harray.append(ROOT.TH2F(f'h_b{t}_temp2', f'B_{{{t}}} % Temp. Valve',
                            200, 20.05, 40.05, 50, bmin[i], bmax[i])) # 45
  for i in range(4):
    harray[i + 8].GetXaxis().SetTitle('[T/mm]')
  for h in harray:
    h.SetLineWidth(2)
  harray[3].SetLineColor(ROOT.kRed + 1)
  for i in range(18):
    garray.append(ROOT.TGraph())
  garray[0].SetTitle('Ref. Field')
  garray[0].GetYaxis().SetTitle('[T]')
  garray[0].SetMarkerColor(ROOT.kBlue + 1)
  garray[1].SetTitle('Ref. Field Corrected')
  garray[1].GetYaxis().SetTitle('[T]')
  garray[1].SetMarkerColor(ROOT.kRed + 1)
  garray[2].SetTitle('Temp. Coil')
  garray[2].GetYaxis().SetTitle('[degC]')
  garray[2].SetMarkerColor(ROOT.kRed + 1)
  garray[3].SetTitle('Temp. Valve')
  garray[3].GetYaxis().SetTitle('[degC]')
  garray[3].SetMarkerColor(ROOT.kRed + 1)
  garray[4].SetTitle('Ref. Field')
  garray[4].GetYaxis().SetTitle('[T]')
  garray[4].SetMarkerColor(ROOT.kBlue + 1)
  garray[5].SetTitle('Temp. Valve')
  garray[5].GetYaxis().SetTitle('[degC]')
  garray[5].SetMarkerColor(ROOT.kRed + 1)
  garray[6].SetTitle('B_{x}')
  garray[7].SetTitle('B_{y}')
  garray[8].SetTitle('B_{z}')
  garray[9].SetTitle('B_{x}')
  garray[10].SetTitle('B_{y}')
  garray[11].SetTitle('B_{z}')
  garray[12].SetTitle('dB_{x}')
  garray[13].SetTitle('dB_{y}')
  garray[14].SetTitle('dB_{z}')
  garray[15].SetTitle('NMR')
  garray[16].SetTitle('dB_{y}')
  carray.append(ROOT.TCanvas('c16', 'B Step', 0, 0, 800, 800))
  for i, g in enumerate(garray):
    g.SetMarkerSize(0.8)
    g.SetMarkerStyle(8)
    xa = g.GetXaxis()
    if i < 4 or i > 14:
      xa.SetTimeDisplay(True)
      xa.SetLabelOffset(0.04)
      # xa.SetLabelSize(0.04)
      xa.SetTimeFormat('#splitline{%Y/%m/%d}{  %H:%M:%S}')
      xa.SetNdivisions(-503)
      xa.SetTimeOffset(0, 'jpn')
    else:
      xa.SetTitle('Step#')
    if i > 11:
      pass
    elif i > 8:
      g.SetLineColor(ROOT.kRed + 1)
    elif i > 5:
      g.SetLineColor(ROOT.kBlue + 1)
  ''' first loop '''
  ipoint = 0
  for key, elm in field_man.field_map.items():
    if len(elm.data) >= 13:
      garray[0].SetPoint(ipoint, elm.unix_time, elm.bref)
      garray[2].SetPoint(ipoint, elm.unix_time, elm.temp1)
      garray[3].SetPoint(ipoint, elm.unix_time, elm.temp2)
      harray[0].Fill(elm.temp1, elm.bref)
      harray[1].Fill(elm.temp2, elm.bref)
      ipoint += 1
    harray[2].Fill(elm.bref)
  ''' fit '''
  bref_mean = harray[2].GetMean()
  harray[1].Draw()
  f1 = ROOT.TF1('f1', 'pol2')
  # harray[1].Fit('f1', 'Q')
  ROOT.gPad.Clear()
  ''' second loop '''
  ipoint = 0
  second_data = False
  for key, elm in field_man.field_map.items():
    if len(elm.data) >= 13:
      cbref = (elm.bref - f1.GetParameter(2) * (elm.temp2**2)
               - f1.GetParameter(1) * elm.temp2
               - f1.GetParameter(0) + bref_mean)
      garray[1].SetPoint(ipoint, elm.unix_time, cbref)
      garray[4].SetPoint(ipoint, elm.step, elm.bref)
      #garray[5].SetPoint(ipoint, elm.step, -0.7160 + 0.0001*elm.temp2)
      garray[5].SetPoint(ipoint, elm.step, cbref)
      garray[15].SetPoint(ipoint, elm.unix_time, elm.nmr)
      garray[16].SetPoint(ipoint, elm.unix_time, elm.b.Y())
      if not second_data:
        garray[6].SetPoint(elm.step, elm.step, elm.b.X())
        garray[7].SetPoint(elm.step, elm.step, elm.b.Y())
        garray[8].SetPoint(elm.step, elm.step, elm.b.Z())
        if elm.step == 1067:
          second_data = True
      else:
        garray[9].SetPoint(ipoint-1070, 1068-elm.step, elm.b.X())
        garray[10].SetPoint(ipoint-1070, 1068-elm.step, elm.b.Y())
        garray[11].SetPoint(ipoint-1070, 1068-elm.step, elm.b.Z())
        # garray[12].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.X() - garray[6].GetY()[1068-elm.step])
        # garray[13].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.Y() - garray[7].GetY()[1068-elm.step])
        # garray[14].SetPoint(ipoint-1070, 1068-elm.step,
        #                     elm.b.Z() - garray[8].GetY()[1068-elm.step])
      harray[3].Fill(cbref)
      harray[44].Fill(elm.temp1, elm.b.X())
      harray[45].Fill(elm.temp1, elm.b.Y())
      harray[46].Fill(elm.temp1, elm.b.Z())
      harray[47].Fill(elm.temp2, elm.b.X())
      harray[48].Fill(elm.temp2, elm.b.Y())
      harray[49].Fill(elm.temp2, elm.b.Z())
      ipoint += 1
    # bscale = elm.bref/bref_mean
    harray[4].Fill(elm.b.X())
    harray[5].Fill(elm.b.Y())
    harray[6].Fill(elm.b.Z())
    harray[7].Fill(elm.b.Mag())
    harray[8].Fill(elm.divB)
    harray[9].Fill(elm.rotBx)
    harray[10].Fill(elm.rotBy)
    harray[11].Fill(elm.rotBz)
    if abs(elm.p.Z())<0.1:
      harray[12].Fill(elm.p.X(), elm.p.Y(), elm.b.X())
      harray[13].Fill(elm.p.X(), elm.p.Y(), elm.b.Y())
      harray[14].Fill(elm.p.X(), elm.p.Y(), elm.b.Z())
      harray[15].Fill(elm.p.X(), elm.p.Y(), elm.b.Mag())
    if abs(elm.p.X())<0.1:
      harray[16].Fill(elm.p.Z(), elm.p.Y(), elm.b.X())
      harray[17].Fill(elm.p.Z(), elm.p.Y(), elm.b.Y())
      harray[18].Fill(elm.p.Z(), elm.p.Y(), elm.b.Z())
      harray[19].Fill(elm.p.Z(), elm.p.Y(), elm.b.Mag())
    if abs(elm.p.Y())<0.1:
      harray[20].Fill(elm.p.X(), elm.p.Z(), elm.b.X())
      harray[21].Fill(elm.p.X(), elm.p.Z(), elm.b.Y())
      harray[22].Fill(elm.p.X(), elm.p.Z(), elm.b.Z())
      harray[23].Fill(elm.p.X(), elm.p.Z(), elm.b.Mag())
    harray[24].Fill(elm.temp2, elm.divB)
    harray[25].Fill(elm.temp2, elm.rotBx)
    harray[26].Fill(elm.temp2, elm.rotBy)
    harray[27].Fill(elm.temp2, elm.rotBz)
    harray[28].Fill(elm.bref, elm.divB)
    harray[29].Fill(elm.bref, elm.rotBx)
    harray[30].Fill(elm.bref, elm.rotBy)
    harray[31].Fill(elm.bref, elm.rotBz)
    for i in range(3):
      harray[32 + i*4].Fill(elm.p[i], elm.divB)
      harray[33 + i*4].Fill(elm.p[i], elm.rotBx)
      harray[34 + i*4].Fill(elm.p[i], elm.rotBy)
      harray[35 + i*4].Fill(elm.p[i], elm.rotBz)
      # if abs(elm.p.X() - 90)<0.1:
      #   utility.print_info(f'{elm.b.Z()}')
  ''' Draw '''
  pdf_name = param_man.get('output_pdf')
  carray[0].Print(pdf_name + '[')
  carray[0].Divide(1, 5)
  for i in range(5):
    carray[0].cd(i + 1).SetGrid()
    if i == 0:
      # garray[0].GetYaxis().SetRangeUser(-0.715, -0.710)
      garray[0].Draw('AP')
      # garray[1].Draw('P')
    elif i == 1:
      garray[15].Draw('AP')
    elif i == 2:
      garray[16].Draw('AP')
    else:
      garray[i-1].Draw('AP')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[0].Print(pdf_name)
  # carray[13].Divide(1, 2)
  carray[13].cd().SetGrid()
  for i in range(2):
    # carray[13].cd(i + 1).SetGrid()
    garray[i + 4].Draw('AP' if i == 0 else 'P')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  # carray[13].Print(pdf_name)
  carray[15].Divide(2, 3)
  for i in range(3):
    carray[15].cd(2*i + 1).SetGrid()
    garray[i + 6].Draw('AL')
    garray[i + 9].Draw('L')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    carray[15].cd(2*i + 2).SetGrid()
    garray[i + 12].Draw('AL')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[15].Print(pdf_name)
  carray[1].Divide(1, 2)
  for i in range(2):
    carray[1].cd(i + 1).SetGrid()
    harray[i].Draw('colz')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  # carray[1].Print(pdf_name)
  for j in range(2):
    carray[j + 14].Divide(2, 2)
    for i in range(4):
      carray[j + 14].cd(i + 1).SetGrid()
      harray[j if i == 3 else i + 44 + j*3].Draw('colz')
      ROOT.gPad.Modified()
      ROOT.gPad.Update()
    carray[j + 14].Print(pdf_name)
  #carray[2].Divide(1, 2)
  carray[2].cd(0).SetGrid()
  # ymax = max(harray[2].GetMaximum(), harray[3].GetMaximum())
  # harray[2].SetMaximum(ymax * 1.05)
  harray[3].Draw()
  harray[2].Draw('same')
  for i in range(2):
    stddev = harray[i + 2].GetStdDev()
    mean = harray[i + 2].GetMean()
    if mean != 0:
      utility.print_info(f'ANA  ref field stddev = {stddev:.3e} ' +
                         f'({abs(stddev/mean)*100:.4f}%)')
  # harray[3].Fit('gaus', '', '')
  carray[2].Print(pdf_name)
  carray[3].Divide(2, 2)
  for i in range(4):
    carray[3].cd(i + 1).SetGrid()
    harray[i + 4].Draw()
  carray[3].Print(pdf_name)
  carray[4].Divide(2, 2)
  for i in range(4):
    carray[4].cd(i + 1).SetGrid()
    # ROOT.gPad.SetLogy()
    harray[i + 8].Draw()
    # harray[i + 8].Fit('gaus')
    text = ROOT.TText()
  carray[4].Print(pdf_name)
  carray[8].Divide(2, 2)
  for i in range(4):
    carray[8].cd(i + 1).SetGrid()
    harray[i + 24].Draw('colz')
  carray[8].Print(pdf_name)
  carray[9].Divide(2, 2)
  for i in range(4):
    carray[9].cd(i + 1).SetGrid()
    harray[i + 28].Draw('colz')
  carray[9].Print(pdf_name)
  for j in range(3):
    carray[10 + j].Divide(2, 2)
    for i in range(4):
      carray[10 + j].cd(i + 1).SetGrid()
      harray[i + 32 + j * 4].Draw('colz')
    carray[10 + j].Print(pdf_name)
  for j in range(3):
    carray[j + 5].Divide(2, 2)
    for i in range(4):
      carray[j + 5].cd(i + 1).SetGrid()
      ROOT.gPad.SetRightMargin(0.15)
      # harray[i + 12].GetZaxis().SetTitle('[T]')
      harray[i + j * 4 + 12].SetStats(False)
      harray[i + j * 4 + 12].Draw('colz')
    carray[j + 5].Print(pdf_name)
  carray[-1].Print(pdf_name + ']')
  if not ROOT.gROOT.IsBatch():
    ROOT.TPython.Prompt()

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
    field_man = fieldmap_manager.FieldMapManager()
    analyze()
  except KeyboardInterrupt:
    pass
