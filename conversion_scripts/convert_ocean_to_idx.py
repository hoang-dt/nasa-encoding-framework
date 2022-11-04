import glob
import numpy as np
import os
import shutil
import sys
import numpy as np
import pandas as pd
from OpenVisus import *
import os, sys
from tqdm import tqdm
from time import sleep

time_begin=int(sys.argv[1])

time_end=int(sys.argv[2])
n_square_faces = 13
n_faces        = 5 # [0, 1, 2, 3, 4]
n_depths       = 90
nx             = 2160
ny             = 2160
type_bytes     = 4 # float322 = 4 bytes
dfx            = [nx  , nx  , nx, nx*3, nx*3] # x dimension of the 5 faces
dfy            = [ny*3, ny*3, ny, ny  , ny  ] # y dimension of the 5 faces
file_u         = '/home1/apanta/files-u.txt'
file_v         = '/home1/apanta/files-v.txt'
dataset_name   = 'llc2160_x_y_depth'
field_name     = 'u'
out_dir='/nobackupp19/vpascucc/IDX1-files/mit_output/ocean_data'


#from config import n_faces, n_depths, nx, ny, type_bytes, dfx, dfy

# Form the name of the .raw output file from a list of parameters
def form_output_file_name(field_name):
    long_field_name = field_name + '_llc2160_x_y_depth'
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
idx_file_name = '/nobackupp19/vpascucc/IDX1-files/mit_output/ocean_data/llc2160_x_y_depth.idx'

field=[Field('u','float32')]
db=CreateIdx(url=idx_file_name,dims=[8640,6480,90],fields=field,time=[0,10366,'time%0000d/'])
depth_data=[]
for t in range(time_begin, time_end):
    output_file, long_field_name, dimensions = form_output_file_name(field_name)
    

    # put all the faces (except face 2) and all the depths into one 3D volume
    raw_name = out_dir + '/' + output_file + '.raw'
    all_depth_faces=np.empty((90,ny * 3, nx * 4), dtype='<f');
    slice = np.empty((ny * 3, nx * 4), dtype='<f')
    with open('/nobackupp17/dmenemen/DYAMOND/c1440_llc2160/mit_output/U/'+files_u[t], "rb") as fu, open('/nobackupp17/dmenemen/DYAMOND/c1440_llc2160/mit_output/V/'+files_v[t], "rb") as fv, open(raw_name, 'wb') as fout:
        #print(files_u[t])
        #print(files_v[t])
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
                skip_bytes += dfx[f] * dfy[f] * type_bytes

                x_from+=nx
            all_depth_faces[d]=slice
                    
        for f in db.getFields():
            db.write(all_depth_faces,field=f,time=t)
       
