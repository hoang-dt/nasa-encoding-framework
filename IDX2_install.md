# To install IDX2 in NAS:
Load GCC9.3 and Cmake:
```
module load gcc/9.3 
module load pkgsrc/2018Q3 
```

Next: 
- Clone the idx2 from github: [sci-visus/idx2](https://github.com/sci-visus/idx2)
- mkdir build && cd build
- ccmake ..
- c
- c
- g (generate)

The Idx2App will be inside ./Source/Application/Idx2App.

# To run IDX2:
For timesteps 0 to 10:
- python3 convert_llc2160_x_y_depth.py 0 10

