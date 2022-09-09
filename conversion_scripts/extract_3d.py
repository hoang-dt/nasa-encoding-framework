import mmap
import struct
import numpy

# Parameters
data = 'llc2160-u-[2160-6480-32]-float32.raw'
dim_x = 2160
dim_y = 6480
dim_z = 32
sample_size = 4 # float64 = 8 bytes
output = 'llc2160-u-[2160-6480-1]-float32.raw'

with open(data, 'r+b') as f:
    with open(output, 'w+b') as g:
        mm = mmap.mmap(f.fileno(), 0)
        for z in range(0, 1, 1):
          for y in range(0, dim_y, 1):
            for x in range(0, dim_x, 1):
                  offset = x + y * dim_x + z * dim_x * dim_y
                  mm.seek(sample_size * offset)
                  sample = mm.read(sample_size)
                  g.write(sample)
        mm.close()
