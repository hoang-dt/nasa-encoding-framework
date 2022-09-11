# put each face into its own file

import numpy as np
import sys

input_file    = sys.argv[1]
# Put the file names into an array (each file supposely contains a time step)
files = []
with open(input_file) as s:
  files = [f.strip('\n') for f in s]

field = sys.argv[2]

# Parameters
nx = 4320
ny = 4320
s = 4 # float322 = 4 bytes
dfx = [nx    , nx    , nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny    , ny    ] # y dimension of the 5 faces
nfaces = 5
ndepths = 1
ntimes = len(files)

for t in range(0, ntimes):
  with open(files[t], "rb") as F:
    for d in range(0, ndepths):
      skip_bytes = d * nx * ny * 13 * s # skip to the depth
      for f in range(0, nfaces):
        face_bytes = s * dfx[f] * dfy[f]
        F.seek(skip_bytes)
        buf = F.read(face_bytes)
        skip_bytes += dfx[f] * dfy[f] * s # skip to the face
        dt = np.dtype('>f')
        np_array_be = np.frombuffer(buf, dtype = dt)
        np_array_le = np_array_be.byteswap()
        output = field + '-time-' + repr(t) + '-depth-' + repr(d) + '-face-' + repr(f) + '.raw'
        with open(output, 'w+b') as g:            
          if f <= 2:
            g.write(np_array_le)    
          else:
            g.write(np.rot90(np_array_le))
          