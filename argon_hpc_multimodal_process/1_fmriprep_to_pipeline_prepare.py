#!/bin/python310

# example
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import itertools
import pandas as pd
from nilearn import image

def smooth_six(img_file_name):
    img_file = image.load_img(img_file_name)
    img_file_smooth = image.smooth_img(img_file, fwhm = 6)
    return img_file_smooth

def fmriprep_to_glm_prepare(target_site, target_subject, output_dir):
    mod_site = target_site.replace('_', '') # L_Fp -> LFp
    sub_func = f'fmriprep/{target_subject}/func/{target_subject}_task-{mod_site}_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz'
    if os.path.exists(sub_func):
        sub_dir = f'{output_dir}/{target_site}/{target_subject}'
        os.makedirs(sub_dir)
        # smooth  
        Img_smooth = smooth_six(sub_func)
        Img_smooth_name = f'{sub_dir}/{target_subject}_task-{mod_site}_space-MNI152NLin6Asym_res-2_desc-preproc_bold_smooth.nii'
        Img_smooth.to_filename(Img_smooth_name)
    sub_head = f'fmriprep/{target_subject}/func/{target_subject}_task-{mod_site}_desc-confounds_timeseries.tsv'
    if os.path.exists(sub_head):
        six_motion_para = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z']
        motion_data = pd.read_csv(sub_head, sep='\t', header=0)
        motion_para_data = motion_data.loc[:, six_motion_para]
        output_file = os.path.join(sub_dir, f'{target_subject}_{mod_site}_head_motion.txt')
        with open(output_file, 'a') as f:
            df_motion = motion_para_data.to_string(header=False, index=False)
            f.write(df_motion)   

# end. author@kangwu, kang-wu@uiowa.edu
