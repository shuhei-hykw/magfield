#!/usr/bin/env python3

#______________________________________________________________________________
def make_test_step():
  with open('test_step.txt', 'w') as f:
    for ix in range(50):
      for iy in range(50):
        for iz in range(50):
      # val = 0 if (i % 2) == 0 else 10
      #f.write(f'{val}\t{-val}\t{-val}\n')
      f.write(f'0\t0\t{-i*10}\n')

#______________________________________________________________________________
if __name__ == '__main__':
  make_test_step()
