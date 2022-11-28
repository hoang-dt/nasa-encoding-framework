# Convert atmosphere simulation data from raw to IDX

See the notebook to convert netcdf files to idx:  https://github.com/hoang-dt/nasa-encoding-framework/blob/main/notebooks/testing_atmosphere_idx_conversion.ipynb We have created an individual idx file for each face, and wrote the values to them. This code can be further optimized.

# Convert ocean simulation data from raw to IDX
See the script https://github.com/hoang-dt/nasa-encoding-framework/blob/main/conversion_scripts/convert_ocean_to_idx.py for how to extract each depths and faces properly, and write them all together to a single idx file.


# Convert ocean simulation data from raw to IDX2

See the script
https://github.com/hoang-dt/nasa-encoding-framework/blob/main/conversion_scripts/convert_llc_x_y_depth.py
for how to extract individual faces, convert them to little endian, rotate faces 3 and 4 90  degrees counterclockwise, then stitch together faces 1 and 2 from field U with faces 3 and 4 from field V to form the final field U.
