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
    sub_name_full = os.path.basename(mask)
    sub_name = 'sub-' + re.findall(r'(\d*)_', sub_name_full)[0]
    mask_size = re.findall(r'_(.*mm).nii.gz', sub_name_full)[0]
    sub_pos_full = mask.split('/')[-2]
    sub_pos = sub_pos_full.replace('_', '')
    return sub_name, sub_pos, mask_size

def beta_extract_ind(mask):
    sub_name, sub_pos, mask_size = get_mask(mask)
    beta_file = os.path.join('Results/glm_gm/simple/beta_files', sub_name, 'beta_' + sub_pos + '.nii.gz')
    if os.path.exists(beta_file):
        try:
            Image = image.load_img(beta_file)
            mask_affined = image.resample_to_img(source_img=mask, target_img=Image, interpolation='nearest')
            beta_all = masking.apply_mask(Image, mask_affined, dtype='f', smoothing_fwhm=None) 
            beta_percent = round(sum(beta_all != 0 ) / len(beta_all), 4)
            beta_mean = round(np.nanmean(beta_all), 4)
            return sub_name, sub_pos, mask_size, beta_percent, beta_mean
        except:
            beta_all = 0
            beta_percent = 0
            beta_mean = 0
            return sub_name, sub_pos, mask_size, beta_percent, beta_mean
    else:
        beta_all = 0
        beta_percent = 0
        beta_mean = 0
        return sub_name, sub_pos, mask_size, beta_percent, beta_mean      

def zmap_extract_ind(mask):
    sub_name, sub_pos, mask_size = get_mask(mask)
    zmap_file = os.path.join('Results/glm_gm/simple/zmap_files', sub_name, 'zmap_' + sub_pos + '.nii.gz')
    if os.path.exists(zmap_file):
        try:
            Image = image.load_img(zmap_file)
            mask_affined = image.resample_to_img(source_img=mask, target_img=Image, interpolation='nearest')
            zmap_all = masking.apply_mask(Image, mask_affined, dtype='f', smoothing_fwhm=None) 
            zmap_percent = round(sum(zmap_all != 0 ) / len(zmap_all), 4)
            zmap_mean = round(np.nanmean(zmap_all), 4)
            return sub_name, sub_pos, mask_size, zmap_percent, zmap_mean
        except:
            zmap_all = 0
            zmap_percent = 0
            zmap_mean = 0
            return sub_name, sub_pos, mask_size, zmap_percent, zmap_mean
    else:
        zmap_all = 0
        zmap_percent = 0
        zmap_mean = 0
        return sub_name, sub_pos, mask_size, zmap_percent, zmap_mean   


def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=14) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    #### beta
    masks = glob(os.path.join('mask/TMS_sites_Env_ind', '*', '*.nii.gz' ))
    future_results = run(beta_extract_ind, masks)

    Subject = []
    Position = []
    Mask_size = []
    Beta_percentage = []
    Beta_mean = []

    for Result in future_results:
        sub_name, sub_pos, mask_size, percent, meanvalue = Result
        Subject.append(sub_name)
        Position.append(sub_pos)
        Mask_size.append(mask_size)
        Beta_percentage.append(percent)
        Beta_mean.append(meanvalue)
    
    df_simple = pd.DataFrame(columns=Subject)
    df_simple.loc[0] = Position
    df_simple.loc[1] = Mask_size
    df_simple.loc[2] = Beta_percentage
    df_simple.loc[3] = Beta_mean
    df_simple.to_csv(os.path.join('Results','glm_gm', 'simple', 'Beta_Individual_Results.csv'), header=True, index=None)

    #### zmap
    masks = glob(os.path.join('mask/TMS_sites_Env_ind', '*', '*.nii.gz' ))
    future_results = run(zmap_extract_ind, masks)

    Subject = []
    Position = []
    Mask_size = []
    Zmap_percentage = []
    Zmap_mean = []

    for Result in future_results:
        sub_name, sub_pos, mask_size, percent, meanvalue = Result
        Subject.append(sub_name)
        Position.append(sub_pos)
        Mask_size.append(mask_size)
        Zmap_percentage.append(percent)
        Zmap_mean.append(meanvalue)
    
    df_simple = pd.DataFrame(columns=Subject)
    df_simple.loc[0] = Position
    df_simple.loc[1] = Mask_size
    df_simple.loc[2] = Zmap_percentage
    df_simple.loc[3] = Zmap_mean
    df_simple.to_csv(os.path.join('Results','glm_gm', 'simple', 'Zmap_Individual_Results.csv'), header=True, index=None)

## end. @author: clancy wu.