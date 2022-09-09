# This program rotates faces 3 and 4 90 degree counter-clockwise to align with faces 0 and 1

import numpy as np
#from scipy import ndimage

# Parameters
data = 'llc_2160-field_U-90_levels-13_faces-2160_2160-float32.raw'
nlevels = 90
nfaces = 5 # the first 3 and last 3 faces each consists of 3 smaller square faces
nx = 2160
ny = 2160
s = 4 # float322 = 4 bytes
dfx = [nx, nx, nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny, ny] # y dimension of the 5 faces

for l in range(0, nlevels):
  print('processing level ' + str(l))
  for f in range(3, 5):
    input_file  = 'llc_2160' + '-level_' + str(l) + '-face_' + str(f) + '-' + str(dfx[f]) + '-' + str(dfy[f]) + '-float32.raw'
    output_file = 'llc_2160' + '-level_' + str(l) + '-face_' + str(f) + '-' + str(dfy[f]) + '-' + str(dfx[f]) + '-float32.raw'
    img = np.fromfile(input_file, dtype = np.float32, count = -1)
    img = img.reshape(dfy[f], dfx[f])
    img = np.rot90(img)
    img.tofile(output_file)
    #TODO: delete the input files after processing