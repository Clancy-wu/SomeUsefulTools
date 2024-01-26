#!/bin/bash python310
import os
from glob import glob
from nilearn import image

work_dir = 'fmriprep'
anat_mask_files = glob(os.path.join(work_dir, '*', 'anat', '*space-MNI152NLin6Asym_res-2_desc-brain_mask.nii.gz'))
group_mean = image.mean_img(anat_mask_files)
group_mean_mask = image.binarize_img(group_mean, threshold=0.5)
group_mean.to_filename('GroupMask/group_mean.nii.gz')
group_mean_mask.to_filename('GroupMask/group_mean_mask.nii.gz')

