# Parameters
n_square_faces = 13
n_faces        = 5 # [0, 1, 2, 3, 4]
n_depths       = 1
nx             = 4320
ny             = 4320
type_bytes     = 4 # float322 = 4 bytes
dfx            = [nx  , nx  , nx, nx*3, nx*3] # x dimension of the 5 faces
dfy            = [ny*3, ny*3, ny, ny  , ny  ] # y dimension of the 5 faces
input_file     = 'files-v-4320.txt'
dataset_name   = 'llc4320'
field_name     = 'v'
time_block     = 64
time_range     = (0, 64) # set to (0, 0) to encode all time steps, otherwise set to (begin, end) to encode time steps begin..end-1
depth_range    = (0, 1)
face_range     = (0, 0)
idx2_exe       = '/home1/dthoang/idx2/build/Source/Applications/idx2App'
n_processes    = 8
out_dir        = '/nobackupp19/vpascucc/converted_files'
