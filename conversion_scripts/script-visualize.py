# This program visualizes the 5 faces of LLC_2160

import matplotlib.pyplot as plt
from matplotlib import transforms
from scipy import ndimage
import numpy as np
import sys


# show one file
def show_one():
  m = sys.float_info.max
  M = sys.float_info.min
  f = np.fromfile('llc_4320-level_0-face_3-4320_4320-float32.raw', dtype = np.float32, count = -1)
  m = min(m, np.min(f))
  M = max(M, np.max(f))
  f = f.reshape(4320, 4320)
  fig = plt.figure(frameon = False)
  # plt.imshow(f, vmin = m, vmax = M)
  ax = plt.Axes(fig, [0., 0., 1., 1.])
  ax.set_axis_off()
  fig.add_axes(ax)
  ax.imshow(f)
  fig.savefig('out.png', bbox_inches = 'tight', transparent = True, pad_inches = 0)
  plt.show()
  print('min = {}, max = {}'.format(m, M))

# show 4 faces in 4 files in a 4 x 1 grid (last two files are rotated)
nx = 2160
ny = 2160
nfaces = 5
s = 4 # float322 = 4 bytes
dfx = [nx, nx, nx, nx * 3, nx * 3] # x dimension of the 5 faces
dfy = [ny * 3, ny * 3, ny, ny, ny] # y dimension of the 5 faces

def show_all():
  mapping = [0, 1, 3, 4]
  fs = [np.fromfile('llc_2160' + '-level_0' + '-face_' + str(i) + '-' + str(dfx[i]) + '-' + str(dfy[i]) + '-float32.raw', dtype = np.float32, count = -1) for i in range(0, nfaces)]
  m = sys.float_info.max
  M = sys.float_info.min
  for i in range(0, nfaces):
    fs[i] = fs[i].reshape(dfy[i], dfx[i])
    m = min(m, np.min(fs[i]))
    M = max(M, np.max(fs[i]))
  ncols = 4
  fig, axes = plt.subplots(1, ncols, frameon = False)
  #fig.set_size_inches(18.5, 10.5)
  plt.subplots_adjust(wspace = 0, hspace = 0)  
  for c in range(ncols):
    ax = axes[c]
    ax.xaxis.label.set_visible(False)
    ax.yaxis.label.set_visible(False)
    ax.axes.xaxis.set_ticklabels([])
    ax.axes.yaxis.set_ticklabels([])
    #ax.set_axis_off()
    i = mapping[c]
    if i > 2:
      rotated_img = ndimage.rotate(fs[i], 90) # TODO: we can use numpy.rot90 instead
      ax.imshow(rotated_img, vmin = m, vmax = M, cmap = 'prism')
      #ax.imshow(fs[i], vmin = m, vmax = M, cmap = 'prism')
    else:
      ax.imshow(fs[i], vmin = m, vmax = M, cmap = 'prism')
  plt.show()
  print('min = {}, max = {}'.format(m, M))

show_all()
