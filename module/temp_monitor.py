#!/usr/bin/env python3

import bs4
import html.parser
import requests
import threading
import time

# from . import param_manager
# from . import utility

#______________________________________________________________________________
class TempMonitor():

  #____________________________________________________________________________
  def __init__(self):
    self.url = 'http://130.87.219.18/digital.cgi?chg=0'
    self.thread_state = 'RUNNING'
    self.temp = [0, 0]
    self.pres = [0, 0]
    self.thread = threading.Thread(target=self.run_thread)
    self.thread.setDaemon(True)
    self.thread.start()

  #____________________________________________________________________________
  def run_thread(self):
    while self.thread_state == 'RUNNING':
      self.update()
      time.sleep(2)

  #____________________________________________________________________________
  def update(self):
    while True:
      try:
        res = requests.get(self.url, timeout=1.0)
        break
      except (requests.exceptions.Timeout) as e:
        time.sleep(0.5)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    varray = []
    for i, s in enumerate(soup.find_all('font', size='6')):
      val = float(s.find('b').string.replace('-', '').replace('+', ''))
      if i == 4 or i == 5:
        val = 10 ** (2 * (val - 6.5))
      varray.append(val)
    if len(varray) >= 10:
      self.temp[0] = varray[8]
      self.temp[1] = varray[9]
      self.pres[0] = varray[4]
      self.pres[1] = varray[5]
