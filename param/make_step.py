#!/usr/bin/env python3

#______________________________________________________________________________
def make_test_step():
  with open('test_step.txt', 'w') as f:
    for i in range(100):
      val = 0 if (i % 2) == 0 else 10
      f.write(f'{val}\t{-val}\t{-val}\n')

#______________________________________________________________________________
if __name__ == '__main__':
  make_test_step()
