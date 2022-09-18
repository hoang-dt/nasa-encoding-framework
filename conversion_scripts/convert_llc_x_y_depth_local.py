# Put all the time steps for a certain face (at a certain depth) into a single volume
# To run this file, provide the config file: python convert_llc.py config.py

import glob
import numpy as np
import os
import shutil
import sys
from time import sleep
from multiprocessing import Process

# import the config file
if len(sys.argv) != 3:
  print('need 2 argument: time_begin time_end')
  exit()
#config = __import__(sys.argv[1])

time_begin = int(sys.argv[1])
time_end   = int(sys.argv[2])

# Parameters
n_square_faces = 13
n_faces        = 5 # [0, 1, 2, 3, 4]
n_depths       = 90
nx             = 2160
ny             = 2160
type_bytes     = 4 # float322 = 4 bytes
dfx            = [nx  , nx  , nx, nx*3, nx*3] # x dimension of the 5 faces
dfy            = [ny*3, ny*3, ny, ny  , ny  ] # y dimension of the 5 faces
file_u         = 'files-u.txt'
file_v         = 'files-v.txt'
dataset_name   = 'llc2160_x_y_depth_bpt_64'
field_name     = 'u'
idx2_exe       = '/home1/dthoang/idx2/build/Source/Applications/idx2App'
idx2_exe       = 'F:/Workspace/idx2/build/Source/Applications/Release/idx2App.exe'
out_dir        = '/nobackupp19/vpascucc/converted_files'
out_dir        = 'J:/nasa'

#from config import n_faces, n_depths, nx, ny, type_bytes, dfx, dfy

def convert_to_idx2(raw_file, dataset_name, long_field_name, dimensions):
  command = (
    idx2_exe + ' --encode '
    + ' --input ' + raw_file + ' '
    + ' --name ' + dataset_name + ' '
    + ' --field ' + long_field_name + ' '
    + ' --type float32 '
    + ' --dims ' + repr(dimensions[0]) + ' ' + repr(dimensions[1]) + ' ' + repr(dimensions[2]) + ' '
    + ' --accuracy 1e-7 '
    + ' --num_levels 4 ' # TODO: move to input param
    + ' --brick_size 32 32 32 ' # TODO: move to input param #aashish: maybe either do 32 32 32 or 64 64 64
    + ' --bricks_per_tile 64 '
    + ' --tiles_per_file 512 '
    + ' --files_per_dir 512 '
    + ' --out_dir ' + out_dir)
  print(command)
  os.system(command)
  os.remove(raw_file)

# Form the name of the .raw output file from a list of parameters
def form_output_file_name(field_name, time):
  long_field_name = field_name + '-time-' + repr(time)
  dimensions = (nx * 4, nx * 3, n_depths)
  output_file = long_field_name
  return output_file, long_field_name, dimensions

if __name__ == '__main__':
  files_u = []
  with open(file_u) as s:
    files_u = [f.strip('\n') for f in s]
  files_v = []
  with open(file_v) as s:
    files_v = [f.strip('\n') for f in s]
  n_time_steps = len(files_u)

  for t in range(time_begin, time_end):
    output_file, long_field_name, dimensions = form_output_file_name(field_name, t)
    idx2_file_name = out_dir + '/' + dataset_name + '/' + output_file + '.idx2'

    # check if the .idx2 file already existed (meaning this has been converted)
    print(idx2_file_name)
    if os.path.exists(idx2_file_name):
      print('found')
      continue
    # check if the file is partially converted
    dir_name = out_dir + '/' + dataset_name + '/' + output_file
    if os.path.exists(dir_name): # the directory exists without a matching .idx2 file (file converted halfway)
      shutil.rmtree(dir_name) # remove the dir first to avoid writing a corrupted file
    print(output_file)

    # put all the faces (except face 2) and all the depths into one 3D volume
    raw_name = out_dir + '/' + dataset_name + '-' + output_file + '.raw'
    slice = np.empty((ny * 3, nx * 4), dtype='<f')
    with open(files_u[t], "rb") as fu, open(files_v[t], "rb") as fv, open(raw_name, 'wb') as fout:
      for d in range(0, n_depths):
        skip_bytes = d * nx * ny * n_square_faces * type_bytes
        x_from = 0
        for f in range(0, n_faces):
          if f == 2:
            skip_bytes += dfx[f] * dfy[f] * type_bytes
            continue
          face_bytes = type_bytes * dfx[f] * dfy[f]
          if f < 2:
            fu.seek(skip_bytes)
          else:
            fv.seek(skip_bytes)
          buf = fu.read(face_bytes) if f <= 2 else fv.read(face_bytes)
          dt = np.dtype('>f')
          array = np.frombuffer(buf, dtype=dt)
          #array_le = array_be.byteswap()
          array = array.reshape(dfy[f], dfx[f])
          if f < 2:
            slice[:, x_from:x_from+nx] = array
          else:
            slice[:, x_from:x_from+nx] = np.rot90(array)
          # copy data from a face to a slice

          #array_le = np.ascontiguousarray(array_le)
          #print(array_le.size * array_le.itemsize)
          skip_bytes += dfx[f] * dfy[f] * type_bytes
          x_from += nx
        fout.write(slice)
    convert_to_idx2(raw_name, dataset_name, long_field_name, dimensions)
