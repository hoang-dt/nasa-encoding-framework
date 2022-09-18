import multiprocessing
import subprocess

files = [
  'xab',
  'xac',
  'xad',
  'xae',
  'xaf',
  'xag',
  'xah',
  'xai',
  'xaj',
  'xak',
  'xal',
  'xam',
  'xan',
  'xao',
  'xap',
  'xaq',
  'xar',
  'xas',
  'xat',
  'xau',
  'xav',
  'xaw',
  'xax',
  'xay',
  'xaz',
  'xba',
  'xbb',
  'xbc',
  'xbd',
  'xbe',
  'xbf'
]

def work(file):
    return subprocess.call('rsync -av --progress --files-from=' + file + ' -r / duong@shell.sci.utah.edu:/usr/sci/cedmav/hello/llc2160_v_32', shell=False)

if __name__ == '__main__':
    count = len(files)
    pool = multiprocessing.Pool(processes=count)
    print pool.map(work, files)