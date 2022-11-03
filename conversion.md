# Convert atmosphere simulation data from raw to IDX
Aashish: please fill in here

# Convert ocean simulation data from raw to IDX
Aashish: please fill in here

# Convert ocean simulation data from raw to IDX2

See the script
https://github.com/hoang-dt/nasa-encoding-framework/blob/main/conversion_scripts/convert_llc_x_y_depth.py
for how to extract individual faces, convert them to little endian, rotate faces 3 and 4 90  degrees counterclockwise, then stitch together faces 1 and 2 from field U with faces 3 and 4 from field V to form the final field U.
