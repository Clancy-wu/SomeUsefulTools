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

#############
from time import time
st = time()
tms_data = image.get_data(tms_file)
atlas_data = image.get_data('first_amyg_reshape_tpl.nii.gz')
test = np.nanmean(tms_data[atlas_data==1])
test = np.nanmean(tms_data[atlas_data==2])
ed = time()
ed - st # 0.015491008758544922
#################
from nilearn import maskers
st = time()
first_mask = maskers.NiftiLabelsMasker('first_amyg_reshape_tpl.nii.gz', background_label=0, smoothing_fwhm=None, standardize=False, standardize_confounds=False, 
                          high_variance_confounds=False, detrend=False, low_pass=None, high_pass=None, t_r=None, dtype=None, 
                          resampling_target='data', verbose=0, strategy='mean', keep_masked_labels=False)
aa=  first_mask.fit_transform(tms_file)
ed = time()
ed - st # 0.45594072341918945

#################
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def get_tms_amyg(ind_mask, label_mask):
    # file: 'rest_fmriprep/mask/IndEnvMask_affined/R_pMFG/1049_10mm.nii'
    sub_name = 'sub-' + re.findall(r'(.*)_', os.path.basename(ind_mask))[0] # sub-1049
    sub_size = re.findall(r'_(.*).nii', os.path.basename(ind_mask))[0] # 10mm
    sub_site = ind_mask.split('/')[-2] # R_pMFG
    sub_datatype = 'tmsfmri_Amyg'
    #####################  Load mask
    mask_data = image.get_data(label_mask)
    #####################  TMS-fMRI
    try:
        # some subs haven't tms_file
        tms_file = glob(os.path.join(tmsfmri_dir, sub_site, '*', f'{sub_name}_tms_*'))[0]
        tms_data = image.get_data(tms_file)    
        L = np.nanmean(tms_data[mask_data==1])
        R = np.nanmean(tms_data[mask_data==2])
        Both = np.nanmean(tms_data[ (mask_data==1) | (mask_data==2) ])    
        ## output
        return (sub_datatype, sub_name, sub_site, sub_size, L, R, Both)
    except:
        return ('NoTMSfile', sub_name+'_NoTMS', sub_site, sub_size, 0, 0, 0)

def get_tms_amyg_batch(args):
    return get_tms_amyg(*args)
label_mask = 'first_amyg_reshape_tpl.nii.gz'
this_iters = list(product(all_files, [label_mask]))
future_results = run(get_tms_amyg_batch, this_iters)
df_out = pd.DataFrame(future_results, columns=['data_type', 'subject', 'tms_site', 'mask_size', 'lh_amyg', 'rh_amyg', 'total_amyg']) 
df_out.to_csv('tmsfmri_IndivMask_Amyg_First.csv', index=None)









