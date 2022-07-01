# Parameters
n_faces = 5 # [0, 1, 2, 3, 4]
n_depths = 90
nx = 2160
ny = 2160
type_bytes = 4 # float322 = 4 bytes
dfx = [nx  , nx  , nx, nx*3, nx*3] # x dimension of the 5 faces
dfy = [ny*3, ny*3, ny, ny  , ny  ] # y dimension of the 5 faces
idx2_exe = 'idx2.exe'
