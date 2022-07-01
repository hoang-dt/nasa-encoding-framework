# Put all the time steps for a certain face (at a certain depth) into a single volume

import glob
import mmap
import numpy as np
import os
import sys
from time import sleep
from config import n_faces, n_depths, nx, ny, type_bytes, dfx, dfy
import config
from convert_to_idx2 import *
from multiprocessing import Process


# Form the name of the .raw output file from a list of parameters
def form_output_file_name(dataset_name, field_name, time_from, time_to, face, depth):
  long_field_name = (
    field_name + '-'
    + 'face-' + repr(face)
    + '-depth-' + repr(depth)
    + '-time-' + repr(time_from) + '-' + repr(time_to))
  dimensions = (dfx[face], dfy[face], time_to-time_from)
  output_file = dataset_name + '-' + long_field_name
  return output_file, long_field_name, dimensions


# Put a certain face (at a certain depth) across time steps [time_from, time_to] into a single volume
def extract_face_across_time(files, time_from, time_to, face, depth, output_file):
  # For each time step, skip to the face of interest and copy out the bytes
  print(output_file)
  with open(output_file, 'w+b') as g:
    skip_bytes = depth * nx * ny * 13 * type_bytes
    for f in range(0, face):
      skip_bytes += dfx[f] * dfy[f] * type_bytes
    face_bytes = type_bytes * dfx[face] * dfy[face]
    for t in range(time_from, time_to):
      with open(files[t], "rb") as f:
        f.seek(skip_bytes)
        buf = f.read(face_bytes)
        dt = np.dtype(float)
        dt = dt.newbyteorder('>')
        np_array_be = np.frombuffer(buf, dtype=dt)
        np_array_le = np_array_be.byteswap()
        g.write(np_array_le)
        f.close()


if __name__ == '__main__':
  # Main program
  # --------------------------------------------------------------
  if len(sys.argv) != 5:
    print('need 4 arguments: input_file dataset_name field_name time_block')
    print('  input_file is a file that contains a list of files each storing one time step')
    print('  dataset_name is the name of the dataset (no space)')
    print('  field_name is the name of the field (no space)')
    print('  time_block indicates the number of time steps that will be grouped in one idx2 file')
    print('example: python convert_llc.py files.txt llc2160 u 64')
    exit()

  input_file    = sys.argv[1]
  dataset_name  = sys.argv[2]
  field_name    = sys.argv[3]
  time_block    = int(sys.argv[4])

  files = []
  with open(input_file) as s:
    files = [f.strip('\n') for f in s]

  n_time_steps = len(files)


  # For each time block, we first write a raw file, then convert it to idx2
  for t in range(0, n_time_steps, time_block):
    t_from = t
    t_to = min(t + time_block, n_time_steps)
    #print(t, time_block, t_to)
    for d in range(0, n_depths):
      for f in range(0, n_faces):
        output_file, long_field_name, dimensions = form_output_file_name(dataset_name, field_name, t_from, t_to, f, d)
        # extract_face_across_time(files, t_from, t_to, f, d, output_file)
        while len(glob.glob1('./', '*.raw')) >= 8: # do not spawn more than 8 processes
          continue
          sleep(1)
        # check if the file has been converted and stored
        idx2_file_name = dataset_name + '/' + output_file + '.id2'
        if os.path.exists(idx2_file_name):
          continue
        p = Process(target = convert_to_idx2, args = (output_file, dataset_name, long_field_name, dimensions))
        p.start()
