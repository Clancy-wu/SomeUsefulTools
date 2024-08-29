# sort file
import pandas as pd
import os
from glob import glob
import re
import numpy as np
from nilearn import image
from shutil import copy, move

dicom_info = 'dicom_information.tsv'
org_data = 'org_data'
bids = 'BIDS'

dicom = pd.read_csv(dicom_info, sep='\t')
sub_list_all = dicom['Subject'].values
sub_remove = ['sub21', 'sub25']
sub_list = np.setdiff1d(sub_list_all, sub_remove)

# delete Func_id=8 in sub15 of org_data dictionary manually. Then continue process.
# DICOM_cmrr_mbep2d_lessvoids_mb3 is the functional name.

anatomy_abnormal = ['sub02', 'sub04', 'sub13']

def multi_rename(src, files, new_name):
    for file in files:
        full_file = os.path.join(src, file)
        old_name = file.split('.')[0]
        full_file_new = full_file.replace(old_name, new_name)
        move(full_file, full_file_new)

def multi_copy(src, files, desti):
    for file in files:
        full_file = os.path.join(src, file)
        copy(full_file, desti)

def sub_sort_to_bids(sub):
    # make dirs
    sub_func_dir = os.path.join(bids, sub, 'func')
    sub_anat_dir = os.path.join(bids, sub, 'anat')
    os.makedirs(sub_func_dir)
    os.makedirs(sub_anat_dir)    
    if not np.isin(sub, anatomy_abnormal):
        # anat
        org_anat_src = os.path.join(org_data, sub, 'anat')
        org_anat_files = os.listdir(org_anat_src)
        multi_copy(org_anat_src, org_anat_files, sub_anat_dir)
        anat_files = os.listdir(sub_anat_dir)
        multi_rename(sub_anat_dir, anat_files, sub+'_T1w') # redefine the file
        # func
        org_func_src = os.path.join(org_data, sub, 'func')
        org_func_files_full = glob(os.path.join(org_func_src, 'DICOM_cmrr_mbep2d_lessvoids_mb3_2016*'))
        org_func_files = [os.path.basename(x) for x in org_func_files_full]
        multi_copy(org_func_src, org_func_files, sub_func_dir)
        func_files = os.listdir(sub_func_dir)
        func_files.sort(key=lambda x:int("".join(re.findall("\d+",x))))
        if len(func_files)==8:
            multi_rename(sub_func_dir, func_files[0:2], sub+'_task-sess1_bold') # sess1
            multi_rename(sub_func_dir, func_files[2:4], sub+'_task-sess2_bold') # sess2
            multi_rename(sub_func_dir, func_files[4:6], sub+'_task-sess3_bold') # sess3
            multi_rename(sub_func_dir, func_files[6:8], sub+'_task-sess4_bold') # sess4
            return('success')
        else:
            return('error')   
    else: 
        # anat
        org_anat_src = os.path.join(org_data, sub, 'anat')
        org_anat_file_nii = ['ana.nii']
        multi_copy(org_anat_src, org_anat_file_nii, sub_anat_dir)            
        anat_file_img = image.load_img(os.path.join(sub_anat_dir, 'ana.nii'))
        anat_file_img.to_filename(os.path.join(sub_anat_dir, sub+'_T1w.nii.gz'))
        os.remove(os.path.join(sub_anat_dir, org_anat_file_nii[0]))
        # func
        org_func_src = os.path.join(org_data, sub, 'func')
        org_func_files_full = glob(os.path.join(org_func_src, 'DICOM_cmrr_mbep2d_lessvoids_mb3_2016*'))
        org_func_files = [os.path.basename(x) for x in org_func_files_full]
        multi_copy(org_func_src, org_func_files, sub_func_dir)
        func_files = os.listdir(sub_func_dir)
        func_files.sort(key=lambda x:int("".join(re.findall("\d+",x))))
        if len(func_files)==8:
            multi_rename(sub_func_dir, func_files[0:2], sub+'_task-sess1_bold') # sess1
            multi_rename(sub_func_dir, func_files[2:4], sub+'_task-sess2_bold') # sess2
            multi_rename(sub_func_dir, func_files[4:6], sub+'_task-sess3_bold') # sess3
            multi_rename(sub_func_dir, func_files[6:8], sub+'_task-sess4_bold') # sess4
            return('success')
        else:
            return('error')   

with open('sort_status.txt', 'w') as sst:
    for sub in sub_list:
        file_status = sub_sort_to_bids(sub)
        file_content = sub + ' ' + file_status + '\n'
        sst.write(file_content)
    sst.close()

# end.