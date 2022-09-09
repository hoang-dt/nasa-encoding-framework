# This program converts the endianess of a raw binary file
# WARNING: the conversion will be in-place (so the original file will be changed)
# TODO: add a flushing call to write all data

import numpy as np
import sys

#data = 'llc_4320-field_U-90_levels-13_faces-4320_4320-float32be.raw'
#output = 'llc_4320-field_U-90_levels-13_faces-4320_4320-float32.raw' 
input = sys.argv[1]
array = np.memmap(input, dtype = np.dtype('>f4'))
array.byteswap(inplace = True)
array.flush()
#array.tofile(output)
