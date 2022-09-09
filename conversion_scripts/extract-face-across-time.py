# Put all the time steps for a certain face (at a certain depth) into a single volume

import mmap
import numpy as np
import sys

if len(sys.argv) != 5:
  print('need 4 arguments: input_file face depth output_prefix')
  print('  input_file is a file that contains a list of files each storing one time step')
  print('  face is a number between 0 and 4 (inclusive)')
  print('  depth is a number between 0 and 90 (inclusive)')
  print('  output_prefix is a string that will be prefixed to the output file name')
  print('example: python extract-face-across-time.py llc2160-32.txt 0 0 llc2160')
  exit()

input_file    = sys.argv[1]
face          = int(sys.argv[2])
depth         = int(sys.argv[3])
output_prefix = sys.argv[4]

# Put the file names into an array (each file supposely contains a time step)
files = []
with open(input_file) as s:
  files = [f.strip('\n') for f in s]
n_time_steps = len(files)

# print(files)
# exit()

# Parameters
nx = 2160
ny = 2160
s = 4 # float322 = 4 bytes
dfx = [nx    , nx    , nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny    , ny    ] # y dimension of the 5 faces

output_file = (
  output_prefix + '-'
  + 'face-' + repr(face)
  + '-depth-' + repr(depth)
  + '-[' + repr(dfx[face])
  + '-'  + repr(dfy[face])
  + '-'  + repr(n_time_steps) + '].raw')

# print(output_file)
# exit()

with open(output_file, 'w+b') as g:
  skip_bytes = depth * nx * ny * 13 * s
  for f in range(0, face):
    skip_bytes += dfx[f] * dfy[f] * s
  face_bytes = s * dfx[face] * dfy[face]
  for t in range(1, n_time_steps):
    with open(files[t], "r+b") as f:
      mm = mmap.mmap(f.fileno(), 0)
      mm.seek(skip_bytes)
      buf = mm.read(face_bytes)
      #dt = np.dtype(float)
      #dt = dt.newbyteorder('>')
      dt = np.dtype('>')
      np_array_be = np.frombuffer(buf, dtype = dt)
      np_array_le = np_array_be.byteswap()
      g.write(np_array_le)
      mm.close()
    #break # NOTE: comment this to write all time steps
