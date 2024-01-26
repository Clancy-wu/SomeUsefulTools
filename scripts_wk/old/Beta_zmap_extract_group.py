#!/bin/python310
####################################################################
##  beta value and z_score value extract based on individual mask
####################################################################

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import re
import os
import numpy as np
import pandas as pd
from nilearn import image, masking
from glob import glob
    
def get_mask(mask):
    mask_full = os.path.basename(mask)
    mask_pos_full = re.findall(r'(^\w*_\w*)_', mask_full)[0]
    mask_pos = mask_pos_full.replace('_', '')
    mask_size = re.findall(r'_(\d+.*mm).nii.gz', mask_full)[0]
    return mask_pos, mask_size

def get_file(file):
    file_base = os.path.basename(file)
    file_pos = re.findall(r'_(.*).nii.gz', file_base)[0]
    file_name = file.split('/')[-2]
    return file_pos, file_name

def extract_group(file, mask):
    mask_pos, mask_size = get_mask(mask)
    file_pos, file_name = get_file(file)
    try:
        Image = image.load_img(file)
        mask_affined = image.resample_to_img(source_img=mask, target_img=Image, interpolation='nearest')
        All = masking.apply_mask(Image, mask_affined, dtype='f', smoothing_fwhm=None) 
        Percent = round(sum(All != 0 ) / len(All), 4)
        Mean = round(np.nanmean(All), 4)
        return file_name, file_pos, mask_pos, mask_size, Percent, Mean
    except:
        All = 0
        Percent = 0
        Mean = 0    
        return file_name, file_pos, mask_pos, mask_size, Percent, Mean   

def call_func_job_simple(args):
    return extract_group(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=14) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    #### beta
    masks = glob(os.path.join('mask/TMS_sites_Env', '*.nii.gz' ))
    beta_files = glob(os.path.join('Results/glm/simple/beta_files', '*','beta_*' ))

    import itertools
    zip_args = itertools.product(beta_files, masks)
    this_iter = list(zip_args)
    future_results = run(call_func_job_simple, this_iter)

    Subject = []
    Position = []
    Mask_position = []
    Mask_size = []
    Beta_percentage = []
    Beta_mean = []

    for Result in future_results:
        sub_name, sub_pos, mask_pos, mask_size, percent, meanvalue = Result
        Subject.append(sub_name)
        Position.append(sub_pos)
        Mask_position.append(mask_pos)
        Mask_size.append(mask_size)
        Beta_percentage.append(percent)
        Beta_mean.append(meanvalue)
    
    df_simple = pd.DataFrame(columns=Subject)
    df_simple.loc[0] = Position
    df_simple.loc[1] = Mask_position
    df_simple.loc[2] = Mask_size
    df_simple.loc[3] = Beta_percentage
    df_simple.loc[4] = Beta_mean
    df_simple.to_csv(os.path.join('Results','glm', 'simple', 'Beta_group_Results.csv'), header=True, index=None)

    #### zmap
    masks = glob(os.path.join('mask/TMS_sites_Env', '*.nii.gz' ))
    zmap_files = glob(os.path.join('Results/glm/simple/zmap_files', '*','zmap_*' ))

    zip_args = itertools.product(zmap_files, masks)
    this_iter = list(zip_args)
    future_results = run(call_func_job_simple, this_iter)

    Subject = []
    Position = []
    Mask_position = []
    Mask_size = []
    Zmap_percentage = []
    Zmap_mean = []

    for Result in future_results:
        sub_name, sub_pos, mask_pos, mask_size, percent, meanvalue = Result
        Subject.append(sub_name)
        Position.append(sub_pos)
        Mask_position.append(mask_pos)
        Mask_size.append(mask_size)
        Zmap_percentage.append(percent)
        Zmap_mean.append(meanvalue)
    
    df_simple = pd.DataFrame(columns=Subject)
    df_simple.loc[0] = Position
    df_simple.loc[1] = Mask_position
    df_simple.loc[2] = Mask_size
    df_simple.loc[3] = Zmap_percentage
    df_simple.loc[4] = Zmap_mean
    df_simple.to_csv(os.path.join('Results','glm', 'simple', 'Zmap_group_Results.csv'), header=True, index=None)

## end. @author: clancy wu.