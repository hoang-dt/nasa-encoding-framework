# This program extracts the individual faces from a raw binary file produced by NASA simulation

import mmap
import struct
import numpy

# Parameters
data = 'llc_2160-field_U-90_levels-13_faces-2160_2160-float32be.raw'
nlevels = 90
nfaces = 5 # the first 3 and last 3 faces each consists of 3 smaller square faces
nx = 2160
ny = 2160
s = 4 # float322 = 4 bytes
dfx = [nx, nx, nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny, ny] # y dimension of the 5 faces

offset = 0
with open(data, 'r+b') as fp:
    mm = mmap.mmap(fp.fileno(), 0)
    for l in range(0, nlevels, 1): # level
        for f in range(0, nfaces, 1): # face
            output = 'llc_2160' + '-level_' + str(l) + '-face_' + str(f) + '-' + str(dfx[f]) + '-' + str(dfy[f]) + '-float32.raw'
            face_bytes = s * dfx[f] * dfy[f] # the size of the current face in bytes
            with open(output, 'w+b') as g:
                mm.seek(offset)
                offset += face_bytes
                face = mm.read(face_bytes)
                # next two lines are only needed if we are swapping the endianess
                # fbe = int.from_bytes(sample, byteorder = 'big')
                # fle = int.to_bytes(fbe, length = 4, byteorder = 'little')
                g.write(face)
            g.close()
    mm.close()