import mmap
import numpy as np
import sys

files = [ 'U.0000817920.data', 'U.0000818000.data', 'U.0000818080.data', 'U.0000818160.data', 'U.0000818240.data', 'U.0000818320.data', 'U.0000818400.data', 'U.0000818480.data',
          'U.0000818560.data', 'U.0000818640.data', 'U.0000818720.data', 'U.0000818800.data', 'U.0000818880.data', 'U.0000818960.data', 'U.0000819040.data', 'U.0000819120.data',
          'U.0000819200.data', 'U.0000819280.data', 'U.0000819360.data', 'U.0000819440.data', 'U.0000819520.data', 'U.0000819600.data', 'U.0000819680.data', 'U.0000819760.data',
          'U.0000819840.data', 'U.0000819920.data', 'U.0000820000.data', 'U.0000820080.data', 'U.0000820160.data', 'U.0000820240.data', 'U.0000820320.data', 'U.0000820400.data' ]

# Parameters
nx = 2160
ny = 2160
s = 4 # float322 = 4 bytes
dfx = [nx    , nx    , nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny    , ny    ] # y dimension of the 5 faces

face   = int(sys.argv[1])
time   = int(sys.argv[2])
output = sys.argv[3]
with open(output, 'w+b') as g:
  skip_bytes = 0 
  for f in range(0, face):
    skip_bytes += dfx[f] * dfy[f] * s                              
  face_bytes = s * dfx[face] * dfy[face]   
  with open(files[time], "r+b") as f:
    mm = mmap.mmap(f.fileno(), 0)
  for d in range(0, 90):          
    mm.seek(nx * ny * 13 * d + skip_bytes)
    buf = mm.read(face_bytes)
    dt = np.dtype(float)
    dt = dt.newbyteorder('>')
    np_array_be = np.frombuffer(buf, dtype = dt) 
    np_array_le = np_array_be.byteswap()
    g.write(np_array_le)
    #break # NOTE: comment this to write all time steps