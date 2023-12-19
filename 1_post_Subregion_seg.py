#!/bin/bash
# This is the script for testing segmentation results between fsl and freesurfer.

## import packages from here
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from glob import glob
import re
import os
import pandas as pd
###########################################################
# clean env
class Cleaner:
    def __init__(self):
        self.reset()
    def reset(self):
        self.keep = set(globals());
    def clean(self):
        g = list(globals())
        for __i in g:
            if __i not in self.keep:
                # print("Removing", __i)      # uncomment for tracing what happens
                del globals()[__i]

clean_env = Cleaner() # set initial env
###########################################################
## 1. data prepare
org_data = '/home/clancy/data/test/BIDS/'
sub_list = glob(org_data+'sub*')
sub_list = [os.path.basename(x) for x in sub_list]
sub_list.sort(key=lambda x:int("".join(re.findall("\d+",x))))
sub_list.remove('sub-1021')
print("================================== Start fsl segmentation ==================================")
## 2. FSL segmentation (version 6.0.5)
fsl_data_dir = '/home/clancy/data/test/derivatives/fmriprep/'
fsl_data_prepare = [fsl_data_dir+x+'/anat/'+x+'_space-MNI152NLin6Asym_res-2_desc-preproc_T1w.nii.gz' for x in sub_list]
fsl_segment_logs = '/home/clancy/data/test/fsl_logs/'

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def fsl_segment(sub_file):
    # prepare
    sub_name = sub_file.split('/')[-3]
    output = fsl_segment_logs + sub_name
    try:
        os.system('run_first_all -m auto -s L_Amyg,R_Amyg -b -i %s -o %s' %(sub_file, output))

        return sub_name, 'success'
    except:
        return sub_name, 'error'

########################################
# run fsl segment
return_results = run(fsl_segment, fsl_data_prepare)
check_file = fsl_segment_logs + 'check_list.txt'
with open(check_file, 'w') as cf:
    check_file_head = 'SubjectID Status\n'
    cf.write(check_file_head)
    for return_result in return_results:
        return_one, return_two = return_result
        check_content = return_one + ' ' + return_two + '\n'
        cf.write(check_content)
    cf.close()

########################################
# compute volumes
# fslstats sub-1001_all_fast_firstseg.nii.gz -l 53.5 -u 54.5 -V
def get_amyg_volume(amyg_file):
    file_basename = os.path.basename(amyg_file)
    sub_name = re.findall('sub-\d+', file_basename)[0]
    lh_volume_info = os.popen('fslstats %s -l 17.5 -u 18.5 -V' %(amyg_file)).read()
    lh_volume = lh_volume_info.split(' ')[1]
    rh_volume_info = os.popen('fslstats %s -l 53.5 -u 54.5 -V' %(amyg_file)).read()
    rh_volume = rh_volume_info.split(' ')[1]
    return sub_name, lh_volume, rh_volume

amygdala_segment_files = glob(fsl_segment_logs + '*_all_fast_firstseg.nii.gz')
amygdala_segment_results = run(get_amyg_volume, amygdala_segment_files)
amygdala_results_file = os.path.join(fsl_segment_logs, 'amygdala_results.txt')
amygdala_results_file_headline = 'SubjectID LeftVolume RightVolume\n'
#txt_write(amygdala_results_file, amygdala_results_file_headline) # headline
with open(amygdala_results_file, 'w') as arf:
    arf.write(amygdala_results_file_headline) # headline
    for amygdala_segment_result in amygdala_segment_results:
        sub_name, lh_volume, rh_volume = amygdala_segment_result
        result_content = sub_name + ' ' + lh_volume + ' ' + rh_volume + '\n'
        arf.write(result_content)
    arf.close()

print("================================== Start freesurfer segmentation ==================================")
clean_env.clean() # clean env to initial env
## 2. Freesurfer segmentation (version 7.4.1)
freesurfer_data_dir = '/home/clancy/data/test/derivatives/fmriprep/sourcedata/freesurfer'
os.environ['SUBJECTS_DIR'] = '/home/clancy/data/test/derivatives/fmriprep/sourcedata/freesurfer'
freesurfer_segment_logs = '/home/clancy/data/test/freesurfer_logs/'
## 1. data prepare
sub_list = glob(os.environ.get('SUBJECTS_DIR')+'/sub*')
sub_list = [os.path.basename(x) for x in sub_list]
sub_list.sort(key=lambda x:int("".join(re.findall("\d+",x))))
sub_list.remove('sub-1021')
## 2. Freesurfer segmentation (version 7.4.1)
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=5) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def freesurfer_segment(sub_name):
    try:
        os.system('segment_subregions hippo-amygdala --cross %s --suffix .%s --out-dir %s' %(sub_name, sub_name, freesurfer_segment_logs))
        os.system('segment_subregions thalamus --cross %s --suffix .%s --out-dir %s' %(sub_name, sub_name, freesurfer_segment_logs))
        os.system('segment_subregions brainstem --cross %s --suffix .%s --out-dir %s' %(sub_name, sub_name, freesurfer_segment_logs))        
        return sub_name, 'success'
    except:
        return sub_name, 'error'

########################################
# run freesurfer segment
return_results = run(freesurfer_segment, sub_list)
check_file = freesurfer_segment_logs + 'check_list.txt'
with open(check_file, 'w') as cf:
    check_file_head = 'SubjectID Status\n'
    cf.write(check_file_head)
    for return_result in return_results:
        return_one, return_two = return_result
        check_content = return_one + ' ' + return_two + '\n'
        cf.write(check_content)
    cf.close()

########################################
# compute volumes
# mytxt = os.path.join(freesurfer_segment_logs, 'lh.amygNucVolumessub-1003.txt')
# df = pd.read_table(mypath, sep=' ')
# dfdf = df.iloc[8,1]
def get_amygdata_volume(sub_name):
    lh_file_name = 'lh.amygNucVolumes.' + sub_name + '.txt'
    lh_file = os.path.join(freesurfer_segment_logs, lh_file_name)
    df_lh = pd.read_table(lh_file, sep=' ')
    df_lh_value = df_lh.iloc[8, 1]
    rh_file_name = 'rh.amygNucVolumes.' + sub_name + '.txt'
    rh_file = os.path.join(freesurfer_segment_logs, rh_file_name)
    df_rh = pd.read_table(rh_file, sep=' ')
    df_rh_value = df_rh.iloc[8, 1]
    return sub_name, df_lh_value, df_rh_value

amygdala_results_file = os.path.join(freesurfer_segment_logs, 'amygdala_results.txt')
amygdala_results_file_headline = 'SubjectID LeftVolume RightVolume\n'

amygdala_results = run(get_amygdata_volume, sub_list)

with open(amygdala_results_file, 'w') as arf:
    arf.write(amygdala_results_file_headline) # headline
    for amygdala_result in amygdala_results:
        sub_name, lh_volume, rh_volume = amygdala_result
        result_content = sub_name + ' ' + str(lh_volume) + ' ' + str(rh_volume) + '\n'
        arf.write(result_content)
    arf.close()
