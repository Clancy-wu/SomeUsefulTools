from glob import glob
from os import path
import os
import re
from shutil import copy
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

data_dir = 'colorid'
out_dir = 'BIDS_colorid'

subs_file = glob(path.join(data_dir, 'CausCon_*_colorid_r1.nii.gz')) # 178
subs_name = [re.findall(r'CausCon_(.*)_colorid', path.basename(x))[0] for x in subs_file]

orig_json = '/home/clancy/Downloads/task/sub-1001/func/sub-1001_task-LFp_bold.json'

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def sort_from_subname(sub_name):
    sub_name_new = 'sub-'+re.findall(r'\d+', sub_name)[0]
    sub_func_dir = path.join(out_dir, sub_name_new, 'func')
    sub_anat_dir = path.join(out_dir, sub_name_new, 'anat')
    os.makedirs(sub_func_dir, exist_ok=True)
    os.makedirs(sub_anat_dir, exist_ok=True)
    #############################
    ## bold
    bold_run1 = f'{data_dir}/CausCon_{sub_name}_colorid_r1.nii.gz'
    bold_new1 = f'{sub_func_dir}/{sub_name_new}_task-colorid_run-01_bold.nii.gz'
    json_new1 = f'{sub_func_dir}/{sub_name_new}_task-colorid_run-01_bold.json'
    copy(bold_run1, bold_new1)
    copy(orig_json, json_new1)
    bold_run2 = f'{data_dir}/CausCon_{sub_name}_colorid_r2.nii.gz'
    bold_new2 = f'{sub_func_dir}/{sub_name_new}_task-colorid_run-02_bold.nii.gz'
    json_new2 = f'{sub_func_dir}/{sub_name_new}_task-colorid_run-02_bold.json'
    copy(bold_run2, bold_new2)
    copy(orig_json, json_new2)
    # unzip
    zip_file = f'/home/clancy/Downloads/task/colorid/CausCon_{sub_name}_colorid.colorid.zip'
    unzip_file = f'/home/clancy/Downloads/task/colorid/CausCon_{sub_name}_colorid.colorid'
    os.system(f'unzip {zip_file} -d {unzip_file}/')
    anat_run1 = f'/home/clancy/Downloads/task/colorid/CausCon_{sub_name}_colorid.colorid/CausCon_{sub_name}_colorid_r1.sess1/struct/orig.nii.gz'
    anat_run1_alt = f'/home/clancy/Downloads/task/colorid/CausCon_{sub_name}_colorid.colorid/CausCon_{sub_name}_colorid_r1.sess1/struct/orig.nii'
    if path.exists(anat_run1):
        anat_run = anat_run1
    else:
        anat_run = anat_run1_alt
    anat_new = f'{sub_anat_dir}/{sub_name_new}_T1w.nii.gz'
    copy(anat_run, anat_new)
    os.system(f'rm -r {unzip_file}')
    return 0

run(sort_from_subname, subs_name)

import json
# dataset_description
dataset_description = {
    "Name": "Task dataset",
    "BIDSVersion": "1.4.1",
    "Author": "Kang Wu",
    "Acknowledgements": "No",
    "Time": "Aug 31 2024",
    "Others": "Remember work life balance"
    }
with open(os.path.join(out_dir, 'dataset_description.json'), 'w') as json_file:
    json.dump(dataset_description, json_file, indent='\t')
