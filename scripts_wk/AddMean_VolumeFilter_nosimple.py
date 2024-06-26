#/bin/python310
from nilearn import image
from nilearn.maskers import NiftiMasker
import re
import numpy
from glob import glob
import os
from nilearn.interfaces.fmriprep import load_confounds_strategy
import numpy as np
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
    
def filter_AddMeanBack(Image_covariance, low_pass=None, high_pass=None, t_r=None):
    Image = image.load_img(Image_covariance)
    masker = NiftiMasker(mask_img=None, smoothing_fwhm=None, standardize=False, standardize_confounds=False, detrend=False,
                         high_variance_confounds=False, target_affine=None, target_shape=None, mask_strategy='background', 
                         dtype=None, reports=False)
    Image_onedim = masker.fit_transform(Image) # 161, 902629
    Image_onedim_sum = np.sum(Image_onedim, axis=0) # 94927
    Image_onedim_nonzero = np.count_nonzero(Image_onedim, axis=0) # 94927
    Image_onedim_mean = np.divide(Image_onedim_sum, Image_onedim_nonzero, out=np.zeros_like(Image_onedim_sum, dtype=np.float64), where=Image_onedim_nonzero!=0) # 94927
    Image_mean = masker.inverse_transform(Image_onedim_mean) # 91,109,91
    ## remove the mean 
    Image_remove = [Image.get_fdata()[:,:,:,x] - Image_mean.get_fdata() for x in range(Image.shape[-1])] # remove the mean
    Image_remove_data = np.stack(Image_remove, axis=3)
    Image_remove_file = image.new_img_like(Image, data=Image_remove_data, copy_header=True)
    # filter
    fmri_file_filter = image.clean_img(Image_remove_file, runs=None, detrend=False, standardize=False, confounds=None, sample_mask=None, 
                            standardize_confounds=False, low_pass=low_pass, high_pass=high_pass, t_r=t_r, ensure_finite=False)
    ## add mean back
    Image_filter = [fmri_file_filter.get_fdata()[:,:,:,x] + Image_mean.get_fdata() for x in range(Image.shape[-1])] # add mean back
    Image_filter_data = np.stack(Image_filter, axis=3)
    Image_final = image.new_img_like(Image, data=Image_filter_data, copy_header=True)
    return(Image_final)

def FmriPreprocess_nosimple(sub):
    # Defined
    fmriprep_dir = 'fmriprep'
    output = os.path.join('Results/VolumeFilter_nosimple', sub)
    os.mkdir(output)
    fmri_file_name = sub + '_*space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz'
    fmri_file_path = os.path.join(fmriprep_dir, sub, 'func', fmri_file_name)
    fmri_file_bolds = glob(fmri_file_path)
    #### for multiple bold image.
    for fmri_file in fmri_file_bolds:
        ## no simple
        # filter
        Image_filter = filter_AddMeanBack(fmri_file, low_pass=None, high_pass=0.008, t_r=2.4)
        # output
        Image_filter_name_base = sub + '_' + re.findall(r"task-(.*)_space", os.path.basename(fmri_file))[0] + '.nii.gz'
        Image_filter_name = os.path.join(output, Image_filter_name_base)
        Image_filter.to_filename(Image_filter_name)

def AddMeanBack_simple(args):
    return FmriPreprocess_nosimple(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    fmriprep_dir = 'fmriprep'
    subs = list(set([Path(f).stem for f in Path(fmriprep_dir).glob(f"sub-*") if Path(f).is_dir()]))
    subs.sort(key=lambda x: int("".join(re.findall("\d+",x))))
    subs = subs[122:]
    import itertools
    zip_args = itertools.product(subs)
    this_iter = list(zip_args)
    future_results = run(AddMeanBack_simple, this_iter)

## end. @author: clancy wu.