import os
from nilearn import image
import numpy as np
import nibabel as nib

bold_nii = '/home/clancy/Downloads/tms_test_iowa/fmriprep/sub-20240830/func/sub-20240830_task-rest_run-02_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz'

amyg_lh = '/home/clancy/Downloads/tms_test_iowa/fmriprep_old/Amyg_First_LH_2mm_tpl.nii.gz'
amyg_rh = '/home/clancy/Downloads/tms_test_iowa/fmriprep_old/Amyg_First_RH_2mm_tpl.nii.gz'

################################################
#### new version: SNR
################################################
def compute_SNR_tSNR(bold_file, roi_file, air_perc_thresh = 2):
    bold_img = image.load_img(bold_file)
    tmean_img = image.mean_img(bold_file) # Temporal mean
    # Estimate air signal threshold from temporal mean of raw BOLD data
    median_img = image.math_img("np.nanmedian(img, axis=-1)", img=bold_file)
    air_thresh = np.percentile(median_img.dataobj[np.where(median_img.dataobj[...] > 0)], air_perc_thresh)
    air_mask = np.sum(bold_img.dataobj < air_thresh, axis=-1) > 0
    # Robust estimate of noise sigma in 4D air space using MAD of air space
    noise_sd = np.nanmedian(median_img.dataobj[air_mask]) / 0.6745
    # Calculate temporal SFNR for MC BOLD series
    #airmask_image = nib.Nifti1Image(air_mask, affine=median_img.affine, header=median_img.header)
    tmean_img.dataobj[np.where(np.isfinite(tmean_img.dataobj) == False)] = 0
    region = nib.load(roi_file)
    region_mask = np.where(region.dataobj[...] > 0)
    # region SNR
    region_snr = np.mean(tmean_img.dataobj[region_mask]) / noise_sd
    # Calculate temporal SFNR for MC BOLD series
    tfluc_img = image.math_img("np.std(img, axis=-1)", img=bold_file)
    tfsnr = nib.Nifti1Image( tmean_img.dataobj / tfluc_img.dataobj, 
                            affine=tmean_img.affine, header=tmean_img.header )
    tfsnr.dataobj[np.where(tfluc_img.dataobj[...] == 0)] = np.nan
    tfsnr.dataobj[np.where(np.isfinite(tfsnr.dataobj) == False)] = 0
    region_tsfnr = np.nanmean(tfsnr.dataobj[region_mask])
    return region_snr, region_tsfnr
################################################
compute_SNR_tSNR(bold_nii, amyg_lh)



################################################
#### If error, change median image of raw image to first iamge
################################################
from nilearn import image
import numpy as np
import nibabel as nib
import os

def compute_SNR_tSNR(bold_file, roi_file):
    bold_img = image.load_img(bold_file)
    tmean_img = image.mean_img(bold_file) # Temporal mean
    tmean_img.dataobj[np.where(np.isfinite(tmean_img.dataobj) == False)] = 0 # ADD

    ref_img = image.index_img(bold_file, 0)

    air_thresh = np.percentile(ref_img.dataobj[np.where(ref_img.dataobj[...] > 0)], 2)

    air_mask = np.sum(ref_img.dataobj < air_thresh, axis=-1) > 0
    # Robust estimate of noise sigma in 4D air space using air space
    noise_sd = np.nanmedian(ref_img.dataobj[air_mask]) / 0.6745
    # Calculate temporal SFNR for MC BOLD series
    #airmask_image = nib.Nifti1Image(air_mask, affine=median_img.affine, header=median_img.header)
    region = nib.load(roi_file)
    region_mask = np.where(region.dataobj[...] > 0)
    # region SNR
    region_snr = np.mean(ref_img.dataobj[region_mask]) / noise_sd
    # Calculate temporal SFNR for MC BOLD series
    tfluc_img = image.math_img("np.std(img, axis=-1)", img=bold_file)
    np.seterr(divide='ignore', invalid='ignore') # for tmean_img.dataobj / tfluc_img.dataobj
    tfsnr = nib.Nifti1Image( tmean_img.dataobj / tfluc_img.dataobj, 
                            affine=tmean_img.affine, header=tmean_img.header )
    tfsnr.dataobj[np.where(tfluc_img.dataobj[...] == 0)] = np.nan
    tfsnr.dataobj[np.where(np.isfinite(tfsnr.dataobj) == False)] = 0
    region_tsfnr = np.nanmean(tfsnr.dataobj[region_mask])
    #####
    sub_name = os.path.basename(bold_file)
    return sub_name, region_snr, region_tsfnr
################################################
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import itertools   
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=13) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results
def compute_SNR_tSNR_batch(args):
    return compute_SNR_tSNR(*args)
#compute_SNR_tSNR(bold_file, amyg_lh)
from glob import glob
all_niis = glob('MNI_img/sub-*_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz')
amyg_lh = 'Amyg_First_LH_2mm_tpl.nii.gz'
this_iter = list(itertools.product(all_niis, [amyg_lh]))
future_resutls = run(compute_SNR_tSNR_batch, this_iter)
import pandas as pd
df = pd.DataFrame(future_resutls, columns=['subject', 'region_SNR', 'region_tSNR'])
df.to_csv('amyg_lh_org_snr_tsnr.csv', index=None)
