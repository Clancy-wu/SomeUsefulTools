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

# flatten a np.array and reshape it
test = np.random.randint(1, 10, size=(3, 2, 4))
test_1d = test.flatten()
test_1d.reshape(test.shape) # same as test

# in first_atlas:
#        left amyg: 18, right amyg: 54
# in bn_atlas:
#        left amyg: 211, 213
#        right amyg: 212, 214
first_data = image.get_data(first_atlas)
empty_data = np.zeros_like(first_data)
empty_data[first_data==18] = 1
empty_data[first_data==54] = 2
image.new_img_like(ref_niimg=first_atlas, data=empty_data).to_filename('first_amyg.nii.gz')

bn_data = image.get_data(bn_atlas)
empty_data = np.zeros_like(bn_data)
empty_data[bn_data==211] = 1; empty_data[bn_data==213] = 1
empty_data[bn_data==212] = 2; empty_data[bn_data==214] = 2
image.new_img_like(ref_niimg=bn_atlas, data=empty_data).to_filename('bn_amyg.nii.gz')

first_amyg = image.get_data('first_amyg.nii.gz')
bn_amyg = image.get_data('bn_amyg.nii.gz')
empty_data = np.zeros_like(bn_amyg)
empty_data[(first_amyg==1) | (bn_amyg==1)] =1 
empty_data[(first_amyg==2) | (bn_amyg==2)] =2 
image.new_img_like(ref_niimg=bn_atlas, data=empty_data).to_filename('first_bn_amyg.nii.gz')
