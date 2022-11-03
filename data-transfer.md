# Sequential file transferring
Create files `ocean-files.txt` and `atmosphere-files.txt` that contain the file names that you want to transfer, then run:

```
rsync -av --progress --files-from=ocean-files.txt /nobackupp17/dmenemen/DYAMOND/c1440_llc2160/mit_output/U duong@shell.sci.utah.edu:/usr/sci/cedmav/hello/nasa-ocean

rsync -av --progress --files-from=atmosphere-files.txt /nobackupp17/dmenemen/DYAMOND/c1440_llc2160/holding/inst_01hr_3d_U_Mv duong@shell.sci.utah.edu:/usr/sci/cedmav/hello/nasa-atmosphere
```

# Multithreaded file transferring
Make sure SSH is set up to log in to the destination without typing a password.
See https://www.thegeekstuff.com/2008/11/3-steps-to-perform-ssh-login-without-password-using-ssh-keygen-ssh-copy-id for instructions on how to set up SSH.
Create a bunch of .txt files containing names of files you want to transfer (using `ls`), then run the following script:

```
run_rsync() {
  # e.g. copies /main/files/blah to /main/filesTest/blah
  rsync -av --progress --files-from="$1" -r /nobackupp19/vpascucc/converted_files/llc2160 duong@shell.sci.utah.edu:/usr/sci/cedmav/hello/llc2160
}
export -f run_rsync
parallel -j16 run_rsync ::: ./*.txt
```

# Resources
The above is what I do personally.
NAS has their own instructions.
See:
https://www.nas.nasa.gov/hecc/support/kb/remote-transfers-115/
https://www.nas.nasa.gov/hecc/support/kb/inbound-file-transfer-through-sfes-examples_144.html
https://www.nas.nasa.gov/hecc/support/kb/remote-transfers-115/
