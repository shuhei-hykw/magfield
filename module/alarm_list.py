#!/usr/bin/env python3

import tkinter
import tkinter.ttk

alarm_list = [(1, 'Over voltage of motor power',
               'An overvoltage was applied to the motor power supply.'),
              (3, 'Voltage drop of control power supply',
               'The input power supply voltage is low.'),
              (4, 'Voltage drop of motor power supply',
               'The motor power supply voltage is low.'),
              (5, 'Serial communication error',
               'An error of serial communication on CN3.'),
              (11, 'Parameter error',
               'An invalid value is set for the parameter.'),
              (21, 'Movement with servo off',
               'Movement command was input with servo off.'),
              (22, 'Zero return unfinished',
               'Movement command was input with zero-return unfinished.'),
              (23, 'Zero return timeout',
               'Zero-return command was not finished in time.'),
              (24, 'Current position write error',
               'Write signal (PWRT) was input during the manual movement.'),
              (25, 'Position data error',
               'The program table is invalid.'),
              (31, 'Position command error',
               'The actual speed exceeded the maximum.'),
              (32, 'Position over-residual',
               'The position residual monitor/command exceeded param#30.'),
              (33, 'Software limit error',
               'The current position exceeded param#3, 4'),
              (34, 'Pressing range error',
               'The motor was pushed back while pressing.'),
              (35, 'Encoder communication error',
               'Communication error with the encoder happened.'),
              (36, 'Encoder error',
               'An error of the encoder itself happened.'),
              (37, 'Battery error',
               'The battery is disconnected or empty.'),
              (38, 'Battery low',
               'The battery voltage is low.'),
              (39, 'OT sensor error',
               'OT (Over Travel) sensor detected an error.'),
              (51, 'EPROM error',
               'EPROM error happened at the booting.'),
              (52, 'Excitation error',
               'No encoder feedback was found at the excitation detection.'),
              (53, 'Motor overload',
               'The motor was overloaded.'),
              (54, 'Servo error',
               'The motor was off more than 2 seconds while moving.'),
              (55, 'Driver controller overheat',
               'The temperature is too high in the driver controller.'),
              (56, 'Electronic thermal error',
               'High current was applied over the protection circuit.'),
              (57, 'Motor overcurrent',
               'Overcurrent was applied to the motor.'),
              (58, 'Movement error',
               'Thrust was detected in the opposite direction' +
               ' to the movement.'),
              (59, 'System alarm',
               'An error of micon in the driver controller happened.'),
              (61, 'Regenerative circuit overload',
               'Regenerative circuit was overloaded.'),
              (62, 'IPM modulde error',
               'An error of motor drive circuit happened.'),
              (63, 'Emergency stop',
               'Emergency stop is on.')]

#______________________________________________________________________________
class AlarmListWindow(tkinter.Toplevel):

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
    tree = tkinter.ttk.Treeview(frame, height=len(alarm_list))
    tree['columns'] = (1, 2, 3)
    tree['show'] = 'headings'
    tree.column(1, width=50, anchor=tkinter.CENTER)
    tree.column(2, width=300)
    tree.column(3, width=450)
    tree.heading(1, text='Code')
    tree.heading(2, text='Alarm name')
    tree.heading(3, text='Content')
    for i, e in enumerate(alarm_list):
      tree.insert('', 'end', tags=i+1, values=(f'{e[0]}', e[1], e[2]))
      if i%2 == 1:
        tree.tag_configure(i+1, background='#eeeeee')
    tree.config(selectmode='none')
    tree.state(('disabled',))
    tree.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

  #____________________________________________________________________________
  def deiconify(self):
    tkinter.Toplevel.deiconify(self)


#______________________________________________________________________________
if __name__ == '__main__':
  root = tkinter.Tk()
  alwin = AlarmListWindow()
  alwin.deiconify()
  alwin.mainloop()
