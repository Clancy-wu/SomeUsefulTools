#!/bin/python3.10
import os
import glob
import shutil

work_dir = 'fmriprep_another'
subs = glob.glob(work_dir+'/sub*')
subs = [os.path.basename(x) for x in subs]
out_dir = 'fmriprep'

for sub in subs:
    Old_file = os.path.join(work_dir, sub, sub)
    New_file = os.path.join(out_dir, sub)
    shutil.move(Old_file, New_file)


# sort subdirs
for sub in subs:
    Old_html = glob.glob(work_dir + '/' + sub + '/*html')
    if len(Old_html)>0:
        Old_html = Old_html[0]
        New_html = out_dir + '/' + os.path.basename(Old_html)
        shutil.move(Old_html, New_html)

## end