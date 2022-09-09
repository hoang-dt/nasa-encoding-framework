# Put all the time steps for a certain face (at a certain depth) into a single volumeimport mmap

import mmap
import numpy as np
import sys

files = [ 'U.0000817920.data' ]

# Parameters
nx = 2160
ny = 2160
s = 4 # float322 = 4 bytes
dfx = [nx    , nx    , nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny    , ny    ] # y dimension of the 5 faces

face   = int(sys.argv[1])
depth  = int(sys.argv[2])
output = sys.argv[3]
with open(output, 'w+b') as g:
  skip_bytes = depth * nx * ny * 13 * s 
  for f in range(0, face):
    skip_bytes += dfx[f] * dfy[f] * s
  print(skip_bytes)
  face_bytes = s * dfx[face] * dfy[face]
  for t in range(0, 1):
    with open(files[t], "r+b") as f:
      mm = mmap.mmap(f.fileno(), 0)
      mm.seek(skip_bytes)
      buf = mm.read(face_bytes)
      dt = np.dtype(float)
      dt = dt.newbyteorder('>')
      np_array_be = np.frombuffer(buf, dtype = dt) 
      np_array_le = np_array_be.byteswap()
      g.write(np_array_le)
      mm.close()
    #break # NOTE: comment this to write all time steps