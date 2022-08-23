from config import idx2_exe
import config
import os

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
    + ' --brick_size 64 64 32 ' # TODO: move to input param #aashish: maybe either do 32 32 32 or 64 64 64
    + ' --bricks_per_tile 512 '
    + ' --tiles_per_file 4096 '
    + ' --files_per_dir 4096 '
    + ' --out_dir .')
  print(command)
  os.system(command)
  os.remove(raw_file)

