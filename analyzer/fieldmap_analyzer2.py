#!/usr/bin/env python3

import argparse
import datetime
import math
import numpy
import os

import fieldmap_manager2
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
  harray.append(ROOT.TH1F('h_by', 'Bx', 50, -1.0035, -0.99805)) # 4
  harray.append(ROOT.TH1F('h_cby', 'cBy', 50, -1.0035, -0.99805)) # 5
  harray.append(ROOT.TH1F('h_dummy2', 'dummy2', 200, -0.2, 0.2)) # 6
  harray.append(ROOT.TH1F('h_dummy3', 'dummy3', 200, 0.8, 1.2)) # 7
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
    harray[-1].GetZaxis().SetRangeUser(0.9, 1.1)
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
  harray.append(ROOT.TH2F('h_center_temp1', 'Cent. Field Y % Temp. Coil',
                          200, 20.05, 40.05, 50, -1.0020, -0.997)) # 44
  harray.append(ROOT.TH2F('h_center_temp2', 'Cent. Field Y % Temp. Valve',
                          200, 20.05, 40.05, 50, -1.0020, -0.997)) # 45
  harray.append(ROOT.TH2F('h_cor_center_temp1', 'Cor Cent. Field Y % Temp. Coil',
                          200, 20.05, 40.05, 50, -1.0020, -0.997)) # 46
  harray.append(ROOT.TH2F('h_cor_center_temp2', 'Cor Cent. Field Y % Temp. Valve',
                          200, 20.05, 40.05, 50, -1.0020, -0.997)) # 47
  harray.append(ROOT.TH2F('h_ref_Bx', 'Ref % Bx',
                          35, -0.7145, -0.711, 200, 0.0071, 0.0073)) # 48
  harray.append(ROOT.TH2F('h_ref_By', 'Ref % By',
                          35, -0.7145, -0.711, 50, -1.0020, -0.9970)) # 49
  harray.append(ROOT.TH2F('h_ref_Bz', 'Ref % Bz',
                          35, -0.7145, -0.711, 300, -0.0164, -0.0161)) # 50

  for i in range(4):
    harray[i + 8].GetXaxis().SetTitle('[T/mm]')
  for h in harray:
    h.SetLineWidth(2)
  harray[3].SetLineColor(ROOT.kRed + 1)
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray.append(ROOT.TGraph())
  garray[0].SetTitle('Ref. Field')
  garray[0].GetYaxis().SetTitle('[T]')
  garray[0].SetMarkerColor(ROOT.kBlue + 1)
  garray[1].SetTitle('Ref. Field Corrected Coil')
  garray[1].GetYaxis().SetTitle('[T]')
  garray[1].SetMarkerColor(ROOT.kRed + 1)
  garray[2].SetTitle('Temp. Coil')
  garray[2].GetYaxis().SetTitle('[degC]')
  garray[2].SetMarkerColor(ROOT.kRed + 1)
  garray[3].SetTitle('Temp. Valve')
  garray[3].GetYaxis().SetTitle('[degC]')
  garray[3].SetMarkerColor(ROOT.kGreen + 1)
  # garray[3].SetTitle('Ref. Field % Temp. Coil')
  # garray[3].GetXaxis().SetTitle('[degC]')
  # garray[3].GetYaxis().SetTitle('[T]')
  # garray[4].SetTitle('Ref. Field % Temp. Valve')
  # garray[4].GetXaxis().SetTitle('[degC]')
  # garray[4].GetYaxis().SetTitle('[T]')
  garray[4].SetTitle('Center. Field (x)')
  garray[4].GetYaxis().SetTitle('[T]')
  garray[4].SetMarkerColor(ROOT.kBlue + 1)
  garray[5].SetTitle('Center. Field (y)')
  garray[5].GetYaxis().SetTitle('[T]')
  garray[5].SetMarkerColor(ROOT.kBlue + 1)
  garray[6].SetTitle('Center. Field (z)')
  garray[6].GetYaxis().SetTitle('[T]')
  garray[6].SetMarkerColor(ROOT.kBlue + 1)
  garray[7].SetTitle('Center. Field Corrected Coil')
  garray[7].GetYaxis().SetTitle('[T]')
  garray[7].SetMarkerColor(ROOT.kRed + 1)
  garray[8].SetTitle('Ref. Field Corrected Valve')
  garray[8].GetYaxis().SetTitle('[T]')
  garray[8].SetMarkerColor(ROOT.kGreen + 1)
  garray[9].SetTitle('Center. Field Corrected Valve')
  garray[9].GetYaxis().SetTitle('[T]')
  garray[9].SetMarkerColor(ROOT.kGreen + 1)


  for g in garray:
    g.SetMarkerSize(0.8)
    g.SetMarkerStyle(8)
    xa = g.GetXaxis()
    xa.SetTimeDisplay(True)
    xa.SetLabelOffset(0.04)
    # xa.SetLabelSize(0.04)
    xa.SetTimeFormat('#splitline{%Y/%m/%d}{  %H:%M:%S}')
    xa.SetNdivisions(-503)
    xa.SetTimeOffset(0, 'jpn')
  ''' first loop '''
  ipoint = 0
  for key, elm in field_man.field_map.items():
    #print("elm.data " + str(elm.data))
    if len(elm.data) >= 13:
      garray[0].SetPoint(ipoint, elm.unix_time, elm.bref)
      garray[2].SetPoint(ipoint, elm.unix_time, elm.temp1)
      garray[3].SetPoint(ipoint, elm.unix_time, elm.temp2)
      # garray[3].SetPoint(ipoint, elm.temp1, elm.bref)
      # garray[4].SetPoint(ipoint, elm.temp2, elm.bref)
      garray[4].SetPoint(ipoint, elm.unix_time, elm.b[0])
      garray[5].SetPoint(ipoint, elm.unix_time, elm.b[1])
      garray[6].SetPoint(ipoint, elm.unix_time, elm.b[2])
      harray[0].Fill(elm.temp1, elm.bref)
      harray[1].Fill(elm.temp2, elm.bref)
      harray[44].Fill(elm.temp1, elm.b[1])
      harray[45].Fill(elm.temp2, elm.b[1])

      harray[48].Fill(elm.bref, elm.b[0])
      harray[49].Fill(elm.bref, elm.b[1])
      harray[50].Fill(elm.bref, elm.b[2])


#      print("ipoint=" + str(ipoint) + ", step=" +str(elm.data[2]) + ", b[2]=" +str(elm.b[2]))
      ipoint += 1
    harray[2].Fill(elm.bref)
    harray[4].Fill(elm.b[1])
  ''' fit '''
  bref_mean = harray[2].GetMean()
  by_mean = harray[4].GetMean()
  print("bymean " + str(by_mean))
  harray[0].Draw()
  harray[1].Draw()
  f0 = ROOT.TF1('f0', 'pol2')
  harray[0].Fit('f0', 'Q')
  ROOT.gPad.Clear()
  f1 = ROOT.TF1('f1', 'pol2')
  harray[1].Fit('f1', 'Q')
  ROOT.gPad.Clear()
  ''' second loop '''
  ipoint = 0
  for key, elm in field_man.field_map.items():
    if len(elm.data) >= 13:
      cbref1 = (elm.bref - f0.GetParameter(2) * (elm.temp1**2)
                - f0.GetParameter(1) * elm.temp1
                - f0.GetParameter(0) + bref_mean)
#      cby1 = (elm.b[1] - f0.GetParameter(2) * (elm.temp1**2)
#              - f0.GetParameter(1) * elm.temp1
#              - f0.GetParameter(0)  + bref_mean)

      cby1 = (elm.b[1] +(-1.* f0.GetParameter(2) * (elm.temp1**2)
                         - f0.GetParameter(1) * elm.temp1
                         - f0.GetParameter(0)  + bref_mean)*(by_mean/bref_mean))

      cbref2 = (elm.bref - f1.GetParameter(2) * (elm.temp2**2)
                - f1.GetParameter(1) * elm.temp2
                - f1.GetParameter(0) + bref_mean)
#      cby2 = (elm.b[1] - f1.GetParameter(2) * (elm.temp2**2)
#              - f1.GetParameter(1) * elm.temp2
#              - f1.GetParameter(0)  + bref_mean)

      cby2 = (elm.b[1] +(-1.* f1.GetParameter(2) * (elm.temp2**2)
                         - f1.GetParameter(1) * elm.temp2
                         - f1.GetParameter(0)  + bref_mean)*(by_mean/bref_mean))

      garray[1].SetPoint(ipoint, elm.unix_time, cbref1)
      garray[7].SetPoint(ipoint, elm.unix_time, cby1)
      garray[8].SetPoint(ipoint, elm.unix_time, cbref2)
      garray[9].SetPoint(ipoint, elm.unix_time, cby2)
      harray[46].Fill(elm.temp1, cby1)
      harray[47].Fill(elm.temp2, cby2)

      harray[3].Fill(cbref1)
      harray[5].Fill(cby1)
      ipoint += 1
  #   bscale = elm.bref/bref_mean
  #   harray[4].Fill(elm.b.X())
  #   harray[5].Fill(elm.b.Y())
  #   harray[6].Fill(elm.b.Z())
  #   harray[7].Fill(elm.b.Mag())
  #   harray[8].Fill(elm.divB)
  #   harray[9].Fill(elm.rotBx)
  #   harray[10].Fill(elm.rotBy)
  #   harray[11].Fill(elm.rotBz)
  #   if abs(elm.p.Z())<0.1:
  #     harray[12].Fill(elm.p.X(), elm.p.Y(), elm.b.X())
  #     harray[13].Fill(elm.p.X(), elm.p.Y(), elm.b.Y())
  #     harray[14].Fill(elm.p.X(), elm.p.Y(), elm.b.Z())
  #     harray[15].Fill(elm.p.X(), elm.p.Y(), elm.b.Mag())
  #   if abs(elm.p.X())<0.1:
  #     harray[16].Fill(elm.p.Z(), elm.p.Y(), elm.b.X())
  #     harray[17].Fill(elm.p.Z(), elm.p.Y(), elm.b.Y())
  #     harray[18].Fill(elm.p.Z(), elm.p.Y(), elm.b.Z())
  #     harray[19].Fill(elm.p.Z(), elm.p.Y(), elm.b.Mag())
  #   if abs(elm.p.Y())<0.1:
  #     harray[20].Fill(elm.p.X(), elm.p.Z(), elm.b.X())
  #     harray[21].Fill(elm.p.X(), elm.p.Z(), elm.b.Y())
  #     harray[22].Fill(elm.p.X(), elm.p.Z(), elm.b.Z())
  #     harray[23].Fill(elm.p.X(), elm.p.Z(), elm.b.Mag())
  #   harray[24].Fill(elm.temp2, elm.divB)
  #   harray[25].Fill(elm.temp2, elm.rotBx)
  #   harray[26].Fill(elm.temp2, elm.rotBy)
  #   harray[27].Fill(elm.temp2, elm.rotBz)
  #   harray[28].Fill(elm.bref, elm.divB)
  #   harray[29].Fill(elm.bref, elm.rotBx)
  #   harray[30].Fill(elm.bref, elm.rotBy)
  #   harray[31].Fill(elm.bref, elm.rotBz)
  #   for i in range(3):
  #     harray[32 + i*4].Fill(elm.p[i], elm.divB)
  #     harray[33 + i*4].Fill(elm.p[i], elm.rotBx)
  #     harray[34 + i*4].Fill(elm.p[i], elm.rotBy)
  #     harray[35 + i*4].Fill(elm.p[i], elm.rotBz)
  #     # if abs(elm.p.X() - 90)<0.1:
  #     #   utility.print_info(f'{elm.b.Z()}')
  # ''' Draw '''
  pdf_name = param_man.get('output_pdf')
  carray[0].Print(pdf_name + '[')
  carray[0].Divide(1, 3)
  carray[0].cd(1).SetGrid()
  #garray[0].GetYaxis().SetRangeUser(-0.715, -0.710)
  garray[0].Draw('AP')
  garray[1].Draw('P')
  garray[8].Draw('P')

  carray[0].cd(2).SetGrid()
  #garray[5].GetYaxis().SetRangeUser(-1.002, -0.998)
  garray[5].Draw('AP')
  garray[7].Draw('P')
  garray[9].Draw('P')



  carray[0].cd(3).SetGrid()
  garray[2].GetYaxis().SetRangeUser(20., 35.)
  garray[2].Draw('AP')
  garray[3].Draw('P')
  ROOT.gPad.Modified()
  ROOT.gPad.Update()

  carray[0].Print(pdf_name)

  carray[1].Divide(1, 3)
  carray[1].cd(1).SetGrid()
  garray[4].Draw('AP')

  carray[1].cd(2).SetGrid()
  garray[6].Draw('AP')

  carray[1].cd(3).SetGrid()
  garray[2].GetYaxis().SetRangeUser(20., 35.)
  garray[2].Draw('AP')
  garray[3].Draw('P')
  ROOT.gPad.Modified()
  ROOT.gPad.Update()

  carray[1].Print(pdf_name)





  carray[2].Divide(1, 2)
  for i in range(2):
    carray[2].cd(i + 1).SetGrid()
    harray[i].Draw('colz')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[2].Print(pdf_name)

  carray[3].Divide(1, 2)
  for i in range(2):
    carray[3].cd(i + 1).SetGrid()
    harray[44+i].Draw('colz')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[3].Print(pdf_name)


  carray[4].Divide(1, 2)
  for i in range(2):
    carray[4].cd(i + 1).SetGrid()
    harray[46+i].Draw('colz')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[4].Print(pdf_name)

  carray[5].Divide(1, 3)
  for i in range(3):
    carray[5].cd(i + 1).SetGrid()
    harray[48+i].Draw('colz')
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
  carray[5].Print(pdf_name)

  carray[5].Print(pdf_name + ']')
  # #carray[2].Divide(1, 2)
  # carray[2].cd(0).SetGrid()
  # # ymax = max(harray[2].GetMaximum(), harray[3].GetMaximum())
  # # harray[2].SetMaximum(ymax * 1.05)
  # harray[3].Draw()
  # harray[2].Draw('same')
  # for i in range(2):
  #   stddev = harray[i + 2].GetStdDev()
  #   mean = harray[i + 2].GetMean()
  #   #    utility.print_info(f'ANA  ref field stddev = {stddev:.3e} ' +
  #   #                       f'({abs(stddev/mean)*100:.4f}%)')
  # # harray[3].Fit('gaus', '', '')
  # carray[2].Print(pdf_name)
  # carray[3].Divide(2, 2)
  # for i in range(4):
  #   carray[3].cd(i + 1).SetGrid()
  #   harray[i + 4].Draw()
  # carray[3].Print(pdf_name)
  # carray[4].Divide(2, 2)
  # for i in range(4):
  #   carray[4].cd(i + 1).SetGrid()
  #   # ROOT.gPad.SetLogy()
  #   harray[i + 8].Draw()
  #   # harray[i + 8].Fit('gaus')
  #   text = ROOT.TText()
  # carray[4].Print(pdf_name)
  # carray[8].Divide(2, 2)
  # for i in range(4):
  #   carray[8].cd(i + 1).SetGrid()
  #   harray[i + 24].Draw('colz')
  # carray[8].Print(pdf_name)
  # carray[9].Divide(2, 2)
  # for i in range(4):
  #   carray[9].cd(i + 1).SetGrid()
  #   harray[i + 28].Draw('colz')
  # carray[9].Print(pdf_name)
  # for j in range(3):
  #   carray[10 + j].Divide(2, 2)
  #   for i in range(4):
  #     carray[10 + j].cd(i + 1).SetGrid()
  #     harray[i + 32 + j * 4].Draw('colz')
  #   carray[10 + j].Print(pdf_name)
  # for j in range(3):
  #   carray[j + 5].Divide(2, 2)
  #   for i in range(4):
  #     carray[j + 5].cd(i + 1).SetGrid()
  #     ROOT.gPad.SetRightMargin(0.15)
  #     # harray[i + 12].GetZaxis().SetTitle('[T]')
  #     harray[i + j * 4 + 12].SetStats(False)
  #     harray[i + j * 4 + 12].Draw('colz')
  #   carray[j + 5].Print(pdf_name)
  #carray[-1].Print(pdf_name + ']')
  #carray[0].Print(pdf_name + ']')
  if not ROOT.gROOT.IsBatch():
    ROOT.TPython.Prompt()

#______________________________________________________________________________
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('param_file', help='analysis parameter file')
  parser.add_argument('-b', '--batch', action='store_true',
                      help='batch flag')
  parser.add_argument('-o', '--online', action='store_true',
                      help='online flag')
  parsed, unparsed = parser.parse_known_args()
  param_man = param_manager.ParamManager()
  param_man.initialize(parsed.param_file)
  field_man = fieldmap_manager2.FieldMapManager()
  analyze()
  exit()

  # b = ROOT.kGray
  # ROOT.gStyle.SetCanvasColor(b)
  # ROOT.gStyle.SetTitleFillColor(b)
  # ROOT.gStyle.SetStatColor(b)
  # f = ROOT.kWhite
  # ROOT.gStyle.SetFrameLineColor(f)
  # ROOT.gStyle.SetGridColor(f)
  # ROOT.gStyle.SetStatTextColor(f)
  # ROOT.gStyle.SetTitleTextColor(f)
  # ROOT.gStyle.SetLabelColor(f,"xyz")
  # ROOT.gStyle.SetTitleColor(f,"xyz")
  # ROOT.gStyle.SetAxisColor(f,"xyz")
  # ROOT.gStyle.SetPalette(ROOT.kDarkBodyRadiator)
  try:
    if parsed.online:
      while True:
        main()
    else:
      main()
  except KeyboardInterrupt:
    pass
