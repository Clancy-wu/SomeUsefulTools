import os
from nilearn import image, regions
from glob import glob
import numpy as np
import re
import pandas as pd
from scipy.stats import pearsonr
#################
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import product

work_dir = '/home/kangwu/tms_fmri_project/extract_for_bella'
os.chdir(work_dir)
#=====================================================================================================
# TMS-fMRI (3D)
#=====================================================================================================
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def get_tms_amyg(ind_mask, label_mask):
    # ind_mask: 'rest_fmriprep/mask/IndEnvMask_affined/R_pMFG/1049_10mm.nii'
    sub_name = 'sub-' + re.findall(r'(.*)_', os.path.basename(ind_mask))[0] # sub-1049
    sub_size = re.findall(r'_(.*).nii', os.path.basename(ind_mask))[0] # 10mm
    sub_site = ind_mask.split('/')[-2] # R_pMFG
    sub_datatype = 'tmsfmri_Amyg'
    #####################  Load mask
    mask_data = image.get_data(label_mask)
    #####################  TMS-fMRI
    try:
        # TMS-fMRI file
        # some subs haven't tms_file
        tms_file = glob(os.path.join(tmsfmri_dir, sub_site, '*', f'{sub_name}_tms_*'))[0]
        tms_data = image.get_data(tms_file)    
        L = np.nanmean(tms_data[mask_data==1])
        R = np.nanmean(tms_data[mask_data==2])
        Both = np.nanmean(tms_data[ (mask_data==1) | (mask_data==2) ])    
        ## output
        return (sub_datatype, sub_name, sub_site, sub_size, L, R, Both)
    except:
        sub_datatype = 'No_tmsfmri_Amyg'
        return (sub_datatype, sub_name, sub_site, sub_size, np.nan, np.nan, np.nan)

def get_tms_amyg_batch(args):
    return get_tms_amyg(*args)
#------------------------------------------------------------------------------------
label_mask = 'first_bn_amyg_reshape_tpl.nii.gz'
this_iters = list(product(all_files, [label_mask]))
future_results = run(get_tms_amyg_batch, this_iters)
df_out = pd.DataFrame(future_results, columns=['data_type', 'subject', 'tms_site', 'mask_size', 'lh_amyg', 'rh_amyg', 'total_amyg']) 
df_out.to_csv('tmsfmri_IndivMask_Amyg_First&BN.csv', index=None)
#=====================================================================================================
# rs-fMRI (4D)
#=====================================================================================================
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def split_label_mask(label_mask):
    mask_data = image.get_data(label_mask)
    L = np.zeros_like(mask_data); R = np.zeros_like(mask_data); Both = np.zeros_like(mask_data)
    # lh
    L[mask_data==1] = 1
    L_mask = image.new_img_like(ref_niimg=label_mask, data=L)
    # rh
    R[mask_data==2] = 1
    R_mask = image.new_img_like(ref_niimg=label_mask, data=R)
    # all
    Both[ (mask_data==1) | (mask_data==2)] = 1
    Both_mask = image.new_img_like(ref_niimg=label_mask, data=Both)
    return L_mask, R_mask, Both_mask
    
def get_fc_amyg(ind_mask, label_mask):
    # time elapse: 64.17s
    # ind_mask: 'rest_fmriprep/mask/IndEnvMask_affined/R_pMFG/1049_10mm.nii'
    sub_name = 'sub-' + re.findall(r'(.*)_', os.path.basename(ind_mask))[0] # sub-1049
    sub_size = re.findall(r'_(.*).nii', os.path.basename(ind_mask))[0] # 10mm
    sub_site = ind_mask.split('/')[-2] # R_pMFG
    sub_datatype = 'rest-fMRI_Amyg'
    #####################  Load mask
    lh_mask, rh_mask, both_mask = split_label_mask(label_mask)
    #####################  rs-fMRI
    rest_file = os.path.join(rest_dir, sub_name, 'func', f'{sub_name}_task-rest_space-MNI152NLin6Asym_res-2_desc-denoisedSmoothed_bold.nii.gz')
    try:
        # if some subs haven't rs-fmri; function tims:
        ind_mask_data=[]; lh_mask_data=[]; rh_mask_data=[]; both_mask_data=[]
        for i in image.iter_img(rest_file):
            ind_mask_data.append(np.nanmean(i.get_fdata()[image.get_data(ind_mask)==1]))
            lh_mask_data.append(np.nanmean(i.get_fdata()[lh_mask.get_fdata()==1]))
            rh_mask_data.append(np.nanmean(i.get_fdata()[rh_mask.get_fdata()==1]))
            both_mask_data.append(np.nanmean(i.get_fdata()[both_mask.get_fdata()==1]))
        ind_lh_fc = pearsonr(ind_mask_data, lh_mask_data, alternative='two-sided').statistic
        ind_rh_fc = pearsonr(ind_mask_data, rh_mask_data, alternative='two-sided').statistic
        ind_both_fc = pearsonr(ind_mask_data, both_mask_data, alternative='two-sided').statistic
        return (sub_datatype, sub_name, sub_site, sub_size, ind_lh_fc, ind_rh_fc, ind_both_fc)
    except:
        sub_datatype = 'No_rsfmri_Amyg'
        return (sub_datatype, sub_name, sub_site, sub_size, np.nan, np.nan, np.nan)

def get_fc_amyg_batch(args):
    return get_fc_amyg(*args)
#-------------------------------------------------------------------------------------
label_mask = 'first_amyg_reshape_tpl.nii.gz'
this_iters = list(product(all_files, [label_mask]))
future_results = run(get_fc_amyg_batch, this_iters)
df_out = pd.DataFrame(future_results, columns=['data_type', 'subject', 'mask_site', 'mask_size', 'lh_amyg_FCvalue', 'rh_amyg_FCvalue', 'amyg_FCvalue']) 
df_out.to_csv('rest_IndivMask_Amyg_First.csv', index=None)
