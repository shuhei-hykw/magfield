#!/usr/bin/env python3

import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np

#______________________________________________________________________________
class ProgressWindow(tkinter.Toplevel):

  #____________________________________________________________________________
  def __init__(self):
    tkinter.Toplevel.__init__(self)
    self.title('Alarm list')
    self.resizable(0, 0)
    self.__make_layout()
    self.protocol('WM_DELETE_WINDOW', self.withdraw)
    self.withdraw()

  #____________________________________________________________________________
  def __make_layout(self):
    frame = tkinter.Frame(self)
    frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
    # fig = Figure(figsize=(5, 4), dpi=100)
    # t = np.arange(0, 3, .01)
    # fig.add_subplot(111).plot(t, 2*np.sin(2*np.pi*t))
    # canvas = FigureCanvasTkAgg(fig, master=frame)
    # canvas.draw()
    # canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH,
    #                             expand=True)
    # toolbar = NavigationToolbar2Tk(canvas, frame)
    # toolbar.update()
    # canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH,
    #                             expand=True)

  #____________________________________________________________________________
  def deiconify(self):
    tkinter.Toplevel.deiconify(self)


#______________________________________________________________________________
if __name__ == '__main__':
  root = tkinter.Tk()
  alwin = AlarmListWindow()
  alwin.deiconify()
  alwin.mainloop()
