# To install IDX2 in NAS:
Load GCC9.3 and Cmake:
```
module load gcc/9.3 
module load pkgsrc/2018Q3 
```

Next: 
- Clone the idx2 from github: [sci-visus/idx2](https://github.com/sci-visus/idx2)
```
mkdir build && cd build
ccmake ..
c
c
g (generate)
make
```
The Idx2App will be inside ./Source/Application/Idx2App.

# To run IDX2:
- go to the python script and update your Idx2App location by changing 'idx2_exe'
- update where you want the output data by manipulating 'out_dir'
For timesteps 0 to 10:
- python3 convert_llc2160_x_y_depth.py 0 10

