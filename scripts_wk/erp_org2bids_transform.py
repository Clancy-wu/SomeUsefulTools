import re
import os
from glob import glob
from shutil import copy

# dcm2niix -f "%t_%c_%d_%n" -z y -ba n -o 403/ 403/
all_subs = [x for x in os.listdir('.') if os.path.isdir(x) and 'BIDS' not in x]

for sub in all_subs:
    os.system(f'/home/clancy/MRIcroGL/Resources/dcm2niix -f "%t_%c_%d_%n" -z y -ba n -o {sub}/ {sub}/')

from nilearn import image
def time_remove(func_nii, remove_time):
    func_img = image.load_img(func_nii)
    func_img_remove = image.index_img(func_img, slice(int(remove_time), func_img.shape[3]) )
    return func_img_remove

for sub in all_subs:
    out_func = os.path.join('BIDS', 'sub-'+sub, 'func')
    out_anat = os.path.join('BIDS', 'sub-'+sub, 'anat')
    os.system(f'mkdir -p {out_func}')
    os.system(f'mkdir -p {out_anat}')
    # func
    func_file = glob(os.path.join(sub, '20*REST*'))
    if len(func_file)==0:
        func_file = glob(os.path.join(sub, '20*rest*'))
    func_niis = [x for x in func_file if '.nii.gz' in x]
    func_niis.sort(key=lambda x: int("".join(re.findall("\d+",x))))
    nii_num = 1
    for func_nii in func_niis:
        func_nii_new = os.path.join(out_func, f'sub-{sub}_task-rest_run-0{nii_num}_bold.nii.gz')
        time_remove(func_nii, remove_time=3).to_filename(func_nii_new)
        func_json_old = func_nii.replace('nii.gz', 'json')
        func_json_new = func_nii_new.replace('nii.gz', 'json')
        copy(func_json_old, func_json_new)
        nii_num += 1
    # anat
    anat_file = glob(os.path.join(sub, '20*Cor*'))
    if len(anat_file)==0:
        anat_file = glob(os.path.join(sub, '20*COR*'))
    anat_nii = [x for x in anat_file if 'nii.gz' in x][0]
    anat_nii_new = os.path.join(out_anat, f'sub-{sub}_T1w.nii.gz')
    copy(anat_nii, anat_nii_new)
    anat_json = anat_nii.replace('nii.gz', 'json')
    anat_json_new = anat_nii_new.replace('nii.gz', 'json')
    copy(anat_json, anat_json_new)
    print(f'{sub} done')

import json
# dataset_description
dataset_description = {
    "Name": "ERP dataset",
    "BIDSVersion": "1.4.1",
    "Author": "Kang Wu",
    "Acknowledgements": "No",
    "Time": "Aug 8 2024"
    }
with open(os.path.join('BIDS', 'dataset_description.json'), 'w') as json_file:
    json.dump(dataset_description, json_file)


#!/bin/bash

#$ -N sub_fmriprep
#$ -pe smp 14
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/
#$ -t 1-31:1
OMP_NUM_THREADS=10

subject=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/eyetrack/2_eyegazefMRI_noise_speech_emotion_all/sublist | head -n+${SGE_TASK_ID} | tail -n-1`

#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

export TEMPLATEFLOW_HOME=${singularityDir}/TemplateFlow
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

##########

#Run fmriprep
singularity run --cleanenv \
-B /Users/kangwu/work:/work \
-B ${TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/templateflow \
${singularityDir}/fmriprep_v2314_kw.sif \
/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/eyetrack/2_eyegazefMRI_noise_speech_emotion_all/BIDS/ /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/eyetrack/2_eyegazefMRI_noise_speech_emotion_all/fmriprep/ participant --participant-label ${subject} \
--fs-license-file ${singularityDir}/license.txt \
--fs-no-reconall \
--skip_bids_validation \
--ignore fieldmaps \
--output-space MNI152NLin6Asym:res-2 \
--output-layout bids \
--nprocs 10 --omp-nthreads 10 --mem 32000 \
-w work \
--resource-monitor \
--notrack \
--stop-on-first-crash