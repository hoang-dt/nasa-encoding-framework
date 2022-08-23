# Parameters
n_faces = 5 # [0, 1, 2, 3, 4] # aashish: change to [0, 1, 2, 3, 4, 5]
n_depths = 90 # aashish: change to 52
nx = 2160 # aashish: 1440
ny = 2160 # aashish: 1440
type_bytes = 4 # float322 = 4 bytes
dfx = [nx  , nx  , nx, nx*3, nx*3] # x dimension of the 5 faces # aashish: change to nx, nx, nx, nx, nx, nx
dfy = [ny*3, ny*3, ny, ny  , ny  ] # y dimension of the 5 faces # aashish: change to ny, ny, ny, ny, ny, ny
idx2_exe = './idx2'
