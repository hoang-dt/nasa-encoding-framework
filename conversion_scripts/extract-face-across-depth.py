import mmap
import numpy as np
import sys

# Put the file names into an array (each file supposely contains a time step)
files = []
with open(input_file) as s:
  files = [f.strip('\n') for f in s]
n_time_steps = len(files)

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