# Running Jupyter on NAS
Create new local environment in ~/myenv
https://www.nas.nasa.gov/hecc/support/kb/using-virtualenv-to-manage-your-own-python-environment_540.html

Install numpy, matplotlib, jupyter, notebook, ipywidgets

```
source ~/myenv/bin/activate

qsub -q devel -I -l select=1:ncpus=24:model=has
jupyter lab --no-browser

ssh -l dthoang -o "StrictHostKeyChecking ask" -L 8008:localhost:8888 -o ProxyJump=sfe,pfe21 r509i0n17
```

Go to http://localhost:8008/lab
