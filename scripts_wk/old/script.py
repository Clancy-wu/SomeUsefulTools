#!/bin/python3.10
from nilearn.interfaces.fmriprep import load_confounds_strategy
from nilearn import image
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from pathlib import Path
import os
import re

def FmriPreprocess_ica(sub):
    # Defined
    #fmriprep_dir = 'fmriprep'
    output = os.path.join('Results', 'VolumesFilter_ica', sub)
    os.mkdir(output)
    # mask
    brain_mask = os.path.join('fmriprep', sub, 'anat', sub+'_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz')  
    # Function for extracting time series through steps of ica-aroma and filter
    fmri_file_name = sub + '_*space-MNI152NLin6Asym_desc-smoothAROMAnonaggr_bold.nii.gz'
    fmri_file_path = os.path.join(fmriprep_dir, sub, 'func', fmri_file_name)
    fmri_file_bolds = glob(fmri_file_path)
    #### for multiple bold image.
    for fmri_file in fmri_file_bolds:
        #brain_mask = fmri_file.replace('desc-smoothAROMAnonaggr_bold', 'res-2_desc-brain_mask') # error
        # ica-aroma
        confounds, sample_mask = load_confounds_strategy(fmri_file, denoise_strategy="ica_aroma")
        ## ica-aroma remove
        Image_ica = image.clean_img(fmri_file, runs=None, detrend=False, standardize=False, 
                        confounds=confounds, sample_mask=sample_mask, low_pass=None, high_pass=None, t_r=None, 
                        ensure_finite=False, mask_img=brain_mask)
        ## filter - low_pass: Low cutoff frequencies, in Hertz; high_pass: High cutoff frequencies, in Hertz.
        Image_filter = image.clean_img(Image_ica, runs=None, detrend=False, standardize=False, 
                        confounds=None, sample_mask=None, low_pass=None, high_pass=0.08, t_r=2.4, 
                        ensure_finite=False, mask_img=brain_mask)
        # output
        Image_filter_name_base = sub + '_' + re.findall(r"task-(.*)_space", os.path.basename(fmri_file))[0] + '.nii.gz'
        Image_filter_name = os.path.join(output, Image_filter_name_base)
        Image_filter.to_filename(Image_filter_name)

def FmriPreprocess_simple(sub):
    # Defined
    #fmriprep_dir = 'fmriprep'
    output = os.path.join('Results', 'VolumesFilter_simple', sub)
    os.mkdir(output)  
    # mask
    brain_mask = os.path.join('fmriprep', sub, 'anat', sub+'_space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz')      
    # Function for extracting time series through steps of ica-aroma and filter
    fmri_file_name = sub + '_*space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz'
    fmri_file_path = os.path.join(fmriprep_dir, sub, 'func', fmri_file_name)
    fmri_file_bolds = glob(fmri_file_path)
    #### for multiple bold image.
    for fmri_file in fmri_file_bolds:
        #brain_mask = fmri_file.replace('preproc_bold', 'brain_mask') # error
        # simple
        confounds, sample_mask = load_confounds_strategy(fmri_file, denoise_strategy="simple")
        ## simple remove
        Image_ica = image.clean_img(fmri_file, runs=None, detrend=False, standardize=False, 
                        confounds=confounds, sample_mask=sample_mask, low_pass=None, high_pass=None, t_r=None, 
                        ensure_finite=False, mask_img=brain_mask)
        ## filter - low_pass: Low cutoff frequencies, in Hertz; high_pass: High cutoff frequencies, in Hertz.
        Image_filter = image.clean_img(Image_ica, runs=None, detrend=False, standardize=False, 
                        confounds=None, sample_mask=None, low_pass=None, high_pass=0.08, t_r=2.4, 
                        ensure_finite=False, mask_img=brain_mask)
        # output
        Image_filter_name_base = sub + '_' + re.findall(r"task-(.*)_space", os.path.basename(fmri_file))[0] + '.nii.gz'
        Image_filter_name = os.path.join(output, Image_filter_name_base)
        Image_filter.to_filename(Image_filter_name)

def call_func_job_simple(args):
    return FmriPreprocess_simple(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=14) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

######################
## loop

if __name__ == '__main__':
    fmriprep_dir = 'fmriprep'
    subs = list(set([Path(f).stem for f in Path(fmriprep_dir).glob(f"sub-*") if Path(f).is_dir()]))
    subs.sort(key=lambda x: int("".join(re.findall("\d+",x))))

    import itertools
    zip_args = itertools.product(subs)
    this_iter = list(zip_args)
    future_results = run(call_func_job_simple, this_iter)

## end. @author: clancy wu.
