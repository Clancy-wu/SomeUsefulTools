import os, time
from concurrent.futures import ThreadPoolExecutor

workspace = os.getcwd()
def SubDicom2bids(sub):
    subdir = os.path.join(workspace, 'BIDS', sub)
    # run dcm2niix - special for 2021 dcm2niix in mrcrogl
    subtarget = os.path.join(workspace, 'fmriprep', sub)
    os.makedirs(subtarget)
    Dcm2nii = '~/MRIcroGL/Resources/dcm2niix -f "%f_%p_%z_%s" -p y -z n -o ' + subtarget + ' '+ subdir
    os.system(Dcm2nii)
    time.sleep(2)


######## single
start = time.ctime()
sub = 'sub131'
SubDicom2bids(sub)
end = time.ctime()
print('single running: \n    start: %s, end: %s' %(start, end))
## 14:00:12 - 14:00:13

#### multiple subs
start = time.ctime()
subs = os.listdir(os.path.join(workspace, 'BIDS'))
pool=ThreadPoolExecutor(12)
for sub in subs:
    pool.submit(SubDicom2bids, sub)
pool.shutdown()
end = time.ctime()
print('single running: \n    start: %s, end: %s' %(start, end))

# thread = 1, time: 14:07:52 - 14:08:12   20s
# thread = 2, time: 14:05:32 - 14:05:42   10s
# thread = 8, time: 14:06:49 - 14:06:54   5s
# thread = 12, time: 14:09:36 - 14:09:41  5s
