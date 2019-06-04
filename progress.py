#!/usr/bin/env python3

import datetime
import numpy
import os
import ROOT

data_dir = 'data'
data = dict()
c1 = None
hist = []
graph = None
text1 = None
text2 = None
#npoints = 123390
#npoints = 131154
#npoints = 442
npoints = 1067
#npoints = 556
speed = 5.84

#______________________________________________________________________________
def get_magnet_coordinate(x, y, z):
  xx = x - 298.1
  yy = - 215.7 - y
  zz = - 212.1 - z
  return xx, yy, zz

#______________________________________________________________________________
def get_timestamp(data):
  y = int(data[0][:4])
  m = int(data[0][5:7])
  d = int(data[0][8:10])
  H = int(data[1][:2])
  M = int(data[1][3:5])
  S = int(data[1][6:8])
  us = int(data[1][9:])
  dt = datetime.datetime(y, m, d, H, M, S, us)
  return dt.timestamp()

#______________________________________________________________________________
def update():
  update_data()
  update_hist()

#______________________________________________________________________________
def update_data():
  global data
  global speed
  process_time_array = []
  flist = sorted(os.listdir(data_dir))
  for fname in flist:
    fname = os.path.join(data_dir, fname)
    if not os.path.isfile(fname):
      continue
    mtime = os.stat(fname).st_mtime
    if mtime < 1557990000:
      continue
    # if ('20190520_061450' in fname or
    #     '20190520_063540' in fname or
    #     '20190527_060958' in fname or
    #     '20190527_061237' in fname or
    #     '20190529_074612' in fname or
    #     '20190529_075358' in fname or
    #     '20190530_02' in fname):
    # if '20190531_183253' not in fname:
    # if ('20190531_191821' not in fname and
    #     '20190531_193258' not in fname):
    if flist[-3] not in fname:
      continue
    prev_time = None
    with open(fname) as f:
      for line in f:
        columns = line.split()
        if '#' in line or len(columns) < 10:
          continue
        key = columns[0] + columns[1]
        data[key] = columns
        curr_time = get_timestamp(columns)
        if prev_time is not None:
          process_time = curr_time - prev_time
          process_time_array.append(process_time)
        prev_time = curr_time
  speed = numpy.mean(process_time_array)
  print(f'average speed = {speed}')

#______________________________________________________________________________
def update_hist():
  global c1
  global graph
  global text1
  global text2
  for i in range(3):
    hist[i].Reset()
  graph.Set(0)
  nevent = len(data)
  ipoint = 0
  curr_step = 0
  for d in data.values():
    x, y, z = get_magnet_coordinate(float(d[3]),
                                    float(d[4]),
                                    float(d[5]))
    hist[0].Fill(x, y)
    hist[1].Fill(z, y)
    hist[2].Fill(x, z)
    step = int(d[2])
    curr_step = max(step, curr_step)
    graph.SetPoint(ipoint, get_timestamp(d), step)
    ipoint += 1
  step = curr_step
  try:
    rems = (npoints - step)*speed
  #  rems = (npoints - curr_step)*speed
    remd = int(rems/3600/24)
    remh = int((rems - remd*24*3600)/3600)
    remm = int((rems - remd*24*3600 - remh*3600)/60)
    rems = int(rems - remd*24*3600 - remh*3600 - remm*60)
    rem = f'{remd}d {remh}h {remm}m {rems}s'
    text1.SetText(0.2, 0.82, f'{step}/{npoints} = {step/npoints:.3f}')
    text2.SetText(0.2, 0.77, f'Rem = {rem}')
  except ValueError:
    pass
  line = ROOT.TLine(graph.GetXaxis().GetXmin(), npoints,
                    graph.GetXaxis().GetXmax(), npoints)
  line.SetLineColor(ROOT.kRed + 1)
  line.Draw()
  graph.GetYaxis().SetRangeUser(0, npoints*1.04)
  for i in range(4):
    c1.cd(i + 1)
    ROOT.gPad.Modified()
    ROOT.gPad.Update()

#______________________________________________________________________________
def main():
  global c1
  global hist
  global graph
  global text1
  global text2
  nbins = int(800/10)
  xmin = -400 - 0.1
  xmax = 400 - 0.1
  hist.append(ROOT.TH2F('hxy', 'Magnet Coordinate XY',
                        nbins, xmin, xmax, nbins, xmin, xmax))
  xa = hist[-1].GetXaxis()
  ya = hist[-1].GetYaxis()
  xa.SetTitle('X')
  ya.SetTitle('Y')
  xa.SetTitleOffset(0.8)
  ya.SetTitleOffset(0.8)
  hist.append(ROOT.TH2F('hyz', 'Magnet Coordinate ZY',
                        nbins, xmin, xmax, nbins, xmin, xmax))
  xa = hist[-1].GetXaxis()
  ya = hist[-1].GetYaxis()
  xa.SetTitle('Z')
  ya.SetTitle('Y')
  xa.SetTitleOffset(0.8)
  ya.SetTitleOffset(0.8)
  hist.append(ROOT.TH2F('hzx', 'Magnet Coordinate XZ',
                        nbins, xmin, xmax, nbins, xmin, xmax))
  xa = hist[-1].GetXaxis()
  ya = hist[-1].GetYaxis()
  xa.SetTitle('X')
  ya.SetTitle('Z')
  xa.SetTitleOffset(0.8)
  ya.SetTitleOffset(0.8)
  # for h in hist:
  #   h.SetMarkerStyle(8)
  graph = ROOT.TGraph()
  graph.SetTitle('Progress')
  xa = graph.GetXaxis()
  graph.GetYaxis().SetTitle('Step')
  xa.SetTimeDisplay(True)
  xa.SetLabelOffset(0.04)
  xa.SetTimeFormat('#splitline{%Y/%m/%d}{  %H:%M:%S}')
  xa.SetNdivisions(-503)
  xa.SetTimeOffset(0, 'jpn')
  graph.SetLineWidth(2)
  graph.SetPoint(0, 0, 0)
  c1 = ROOT.TCanvas('c1', 'Mapping Progress Monitor', 800, 800)
  c1.Divide(2, 2)
  for i in range(3):
    c1.cd(i + 1).SetGrid()
    hist[i].Draw('colz')
  c1.cd(4).SetGrid()
  ROOT.gPad.SetLeftMargin(0.13)
  graph.Draw('AL')
  text1 = ROOT.TText()
  text2 = ROOT.TText()
  text1.SetNDC(True)
  text2.SetNDC(True)
  text1.Draw()
  text2.Draw()
  while not ROOT.gSystem.ProcessEvents():
    update()

#______________________________________________________________________________
if __name__ == '__main__':
  ROOT.gStyle.SetOptStat(10)
  ROOT.gStyle.SetStatX(0.9)
  ROOT.gStyle.SetStatY(0.9)
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
  ROOT.gStyle.SetPalette(ROOT.kCool)
  try:
    main()
  except KeyboardInterrupt:
    pass
