#!/usr/bin/env python3

#______________________________________________________________________________
def make_test_step():
  with open('test_step.txt', 'w') as f:
    for ix in range(51):
      for iy in range(51):
        for iz in range(51):
          x = ix*10
          y = -iy*10
          z = -iz*10
          if (iy % 2) == 1:
            z = -500 - z
          # val = 0 if (i % 2) == 0 else 10
          #f.write(f'{val}\t{-val}\t{-val}\n')
          f.write(f'{x}\t{y}\t{z}\n')

#______________________________________________________________________________
if __name__ == '__main__':
  make_test_step()
