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
if len(sys.argv) != 2:
  print('need 1 argument: the config file')
  exit()
config = __import__(sys.argv[1])

#from config import n_faces, n_depths, nx, ny, type_bytes, dfx, dfy

def convert_to_idx2(raw_file, dataset_name, long_field_name, dimensions):
  command = (
    config.idx2_exe + ' --encode '
    + ' --input ' + raw_file + ' '
    + ' --name ' + dataset_name + ' '
    + ' --field ' + long_field_name + ' '
    + ' --type float32 '
    + ' --dims ' + repr(dimensions[0]) + ' ' + repr(dimensions[1]) + ' ' + repr(dimensions[2]) + ' '
    + ' --accuracy 1e-7 '
    + ' --num_levels 4 ' # TODO: move to input param
    + ' --brick_size 32 32 32 ' # TODO: move to input param #aashish: maybe either do 32 32 32 or 64 64 64
    + ' --bricks_per_tile 512 '
    + ' --tiles_per_file 4096 '
    + ' --files_per_dir 4096 '
    + ' --out_dir .')
  print(command)
  os.system(command)
  os.remove(raw_file)

# Form the name of the .raw output file from a list of parameters
def form_output_file_name(field_name, time_from, time_to, face, depth):
  long_field_name = (
    field_name + '-'
    + 'face-' + repr(face)
    + '-depth-' + repr(depth)
    + '-time-' + repr(time_from) + '-' + repr(time_to))
  dimensions = (config.dfx[face], config.dfy[face], time_to-time_from)
  output_file = long_field_name
  return output_file, long_field_name, dimensions


# Put a certain face (at a certain depth) across time steps [time_from, time_to] into a single volume
# We go fetch each face at each depth (level) from [time_from, time_to) and put them into a single raw file
# aashish: "merge" 1024 raw files into a single raw file
# level_0_face_0_time_0.raw
# level_0_face_1_time_0.raw
#....
# merge level_i_face_j_time_0.raw ... level_i_face_j_time_1023.raw -> into a single raw file for every i,j
def extract_face_across_time(files, time_from, time_to, face, depth, output_file):
  # For each time step, skip to the face of interest and copy out the bytes
  print(output_file)
  with open(output_file, 'w+b') as g:
    skip_bytes = depth * config.nx * config.ny * config.n_square_faces * config.type_bytes
    for f in range(0, face):
      skip_bytes += config.dfx[f] * config.dfy[f] * config.type_bytes
    face_bytes = config.type_bytes * config.dfx[face] * config.dfy[face]
    for t in range(time_from, time_to):
      with open(files[t], "rb") as f:
        f.seek(skip_bytes)
        buf = f.read(face_bytes)
        dt = np.dtype('>f')
        np_array_be = np.frombuffer(buf, dtype=dt)
        np_array_le = np_array_be.byteswap() # aashish: do not do the byteswap (to convert big endian to little endian)
        g.write(np_array_le)
        f.close()


if __name__ == '__main__':
  files = []
  with open(config.input_file) as s:
    files = [f.strip('\n') for f in s]
  n_time_steps = len(files)

  # For each time block, we first write a raw file, then convert it to idx2
  time_begin = config.time_range[0]
  time_end   = config.time_range[1]
  if time_begin == time_end:
    time_begin = 0
    time_end = n_time_steps
  face_begin = config.face_range[0]
  face_end = config.face_range[1]
  if face_begin == face_end:
    face_begin = 0
    face_end = config.n_faces
  depth_begin = config.depth_range[0]
  depth_end = config.depth_range[1]
  if depth_begin == depth_end:
    depth_begin = 0
    depth_end = config.n_depths
  for t in range(time_begin, time_end, config.time_block):
    t_from = t
    t_to = min(t + config.time_block, n_time_steps)
    #print(t, time_block, t_to)
    for d in range(depth_begin, depth_end):
      for f in range(face_begin, face_end):
        # check if the file has been converted and stored
        output_file, long_field_name, dimensions = form_output_file_name(config.field_name, t_from, t_to, f, d)
        idx2_file_name = config.dataset_name + '/' + output_file + '.idx2'
        print(idx2_file_name)
        if os.path.exists(idx2_file_name):
          print('found')
          continue
        dir_name = config.dataset_name + '/' + output_file
        if os.path.exists(dir_name):
          shutil.rmtree(config.dataset_name + '/' + output_file) # remove the dir first to avoid writing a corrupted file
        extract_face_across_time(files, t_from, t_to, f, d, output_file + '.raw')
        while len(glob.glob1('./', '*.raw')) >= config.n_processes:
          continue
          sleep(1)
        p = Process(target = convert_to_idx2, args = (output_file + '.raw', config.dataset_name, long_field_name, dimensions))
        p.start()
