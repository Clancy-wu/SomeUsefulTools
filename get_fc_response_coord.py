import os
from nilearn import image, regions, maskers
from glob import glob
import numpy as np
import pandas as pd
import re
from scipy.stats import pearsonr
from nibabel.affines import apply_affine
#################
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import product

work_dir = '/home/kangwu/tms_fmri_project/extract_for_zhuoran'
os.chdir(work_dir)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results
  
# tmsfmri data
tmsfmri_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/group_con_data/'
all_files = glob(os.path.join(tmsfmri_dir, '*', '*HC', '*.nii.gz')) # 797

def get_hipp_activation(sub_file):
    sub_info = os.path.basename(sub_file)
    sub_name = re.findall(r'(sub-.*)_tms', sub_info)[0]
    sub_site = re.findall(r'tms_(.*)_con_0001', sub_info)[0]
    sub_type = 'harvard_hipp'
    sub_data = image.get_data(sub_file)
    ## mask, 1=L hipp, 2=R hipp
    mask_file = 'hard_hippo_reshape_tpl.nii.gz'
    mask_data = image.get_data(mask_file)
    # main
    lh_hipp = np.nanmean(sub_data[mask_data == 1])
    rh_hipp = np.nanmean(sub_data[mask_data == 2])
    both_hipp = np.nanmean(sub_data[(mask_data == 1) | (mask_data == 2)])
    return sub_type, sub_name, sub_site, lh_hipp, rh_hipp, both_hipp

#future_results = run(get_hipp_activation, all_files)
out_columns = ['data_type', 'subject', 'site', 'lh_hipp', 'rh_hipp', 'both_hipp']
df_out = pd.DataFrame(future_results, columns=out_columns)
df_out = df_out[~((df_out['subject']=='sub-1039')&(df_out['site']=='L_aMFG'))]
df_out = df_out[~((df_out['subject']=='sub-1039')&(df_out['site']=='R_aMFG'))]
df_out.to_csv('All_subs_TMS_hipp_HarvardAtlas.csv', index=None)

group_mask_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/mask/GroupEnvMask_affined/'
group_masks = glob(os.path.join(group_mask_dir, '*')) # 45
rest_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/xcp_d_36P_Head05'
rest_files = glob(os.path.join(rest_dir, '*', 'func', '*_task-rest_space-MNI152NLin6Asym_res-2_desc-denoisedSmoothed_bold.nii.gz')) # 93
tmsfmri_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/group_con_data/'

def find_peak_location(input_img):
    # data could be 3D or 4D, but is only meaningful in 3D
    img_data = input_img.get_fdata()
    # max
    max_peak_flat = np.argmax(img_data)
    max_peak_index = np.unravel_index(max_peak_flat, img_data.shape)
    max_peak_value = img_data[max_peak_index]
    max_voxel_coord = [max_peak_index[0], max_peak_index[1], max_peak_index[2]]
    max_coord = apply_affine(input_img.affine, max_voxel_coord)
    return max_peak_value, max_coord

def compute_fr(matrix_a, matrix_b):
    mean_a = np.nanmean(matrix_a, axis=0)
    mean_b = np.nanmean(matrix_b, axis=0)
    std_a = np.nanstd(matrix_a, axis=0)
    std_b = np.nanstd(matrix_b, axis=0)
    covariance_matrix = np.mean((matrix_a - mean_a) * (matrix_b - mean_b), axis=0)
    np.seterr(invalid='ignore') # ignore the warning message because 0/0 = nan.
    fr = covariance_matrix / (std_a * std_b)
    return fr

def hipp_fc_peak(sub_rs_file, group_mask):
    sub_info = os.path.basename(sub_rs_file)
    sub_type = 'Harvard_Hipp'
    sub_name = re.findall(r'(sub-.*)_task', sub_info)[0]
    group_mask_info = os.path.basename(group_mask)
    mask_site = re.findall(r'(._.*)_', group_mask_info)[0]
    mask_size = re.findall(r'._.*_(.*).nii.gz', group_mask_info)[0]
    brain_mask = maskers.NiftiMasker(smoothing_fwhm=None, standardize=False, 
                                standardize_confounds=False, detrend=False,
                                low_pass=None, high_pass=None, t_r=None)
    # mask
    hipp_mask = 'hard_hippo_reshape_tpl.nii.gz'
    roi_mask = brain_mask.fit(hipp_mask) 
    roi_mask_data = roi_mask.transform(hipp_mask) # (1,1400)
    roi_signal_2d = brain_mask.transform(sub_rs_file) # (234, 1400)
    # site
    seed_data = regions.img_to_signals_labels(sub_rs_file, labels_img=group_mask, background_label=0, order='F', strategy='mean', keep_masked_labels=False) # (234,1)
    seed_signal = seed_data[0]
    seed_signal_2d = np.tile(seed_signal, (1, roi_signal_2d.shape[1])) # (234, 1400)
    # compute
    roi_seed_fc = compute_fr(roi_signal_2d, seed_signal_2d) # (1400,)
    roi_seed_fc_lh = roi_seed_fc.copy(); roi_seed_fc_rh = roi_seed_fc.copy()
    ## lh
    roi_seed_fc_lh[roi_mask_data[0,:] == 2] = 0
    roi_seed_fc_lh_map = roi_mask.inverse_transform(roi_seed_fc_lh.reshape(1,-1))
    pos_peak_lh_info = find_peak_location(roi_seed_fc_lh_map)
    ## rh
    roi_seed_fc_rh[roi_mask_data[0,:] == 1] = 0
    roi_seed_fc_rh_map = roi_mask.inverse_transform(roi_seed_fc_rh.reshape(1,-1))
    pos_peak_rh_info = find_peak_location(roi_seed_fc_rh_map)
    return sub_type, sub_name, mask_site, mask_size, pos_peak_lh_info[0], pos_peak_lh_info[1], pos_peak_rh_info[0], pos_peak_rh_info[1]

def hipp_fc_peak_batch(args):
    return hipp_fc_peak(*args)

group_6mm = [x for x in group_masks if '_6mm' in x]
this_iters = list(product(rest_files, group_6mm))
future_results = run(hipp_fc_peak_batch, this_iters)
out_columns = ['data_type', 'subject', 'mask_site', 'mask_size', 'lh_fc_value', 'lh_fc_coord', 'rh_fc_value', 'rh_fc_coord']
df_out = pd.DataFrame(future_results, columns=out_columns)
df_out.to_csv('AllSubs_TMS_Site_Hipp_FC_Peak_Coord.csv', index=None)

def hipp_response_peak(sub_tms_file):
    sub_info = os.path.basename(sub_tms_file)
    sub_name = re.findall(r'(sub-.*)_tms', sub_info)[0]
    sub_site = re.findall(r'tms_(.*)_con_0001', sub_info)[0] 
    sub_type = 'harvard_hipp'
    brain_mask = maskers.NiftiMasker(smoothing_fwhm=None, standardize=False, 
                                standardize_confounds=False, detrend=False,
                                low_pass=None, high_pass=None, t_r=None)    
    # mask
    hipp_mask = 'hard_hippo_reshape_tpl.nii.gz'
    roi_mask = brain_mask.fit(hipp_mask) 
    roi_mask_data = roi_mask.transform(hipp_mask) # (1,1400)
    roi_signal_2d = brain_mask.transform(sub_tms_file) # (1, 1400)
    roi_signal_2d_lh = roi_signal_2d.copy(); roi_signal_2d_rh = roi_signal_2d.copy()
    roi_signal_lh = roi_signal_2d_lh[0,:]; roi_signal_rh = roi_signal_2d_rh[0,:]    
    ## lh
    roi_signal_lh[roi_mask_data[0,:] == 2] = 0
    roi_signal_lh_map = roi_mask.inverse_transform(roi_signal_lh.reshape(1, -1))
    pos_peak_lh_info = find_peak_location(roi_signal_lh_map)
    ## rh
    roi_signal_rh[roi_mask_data[0,:] == 1] = 0
    roi_signal_rh_map = roi_mask.inverse_transform(roi_signal_rh.reshape(1, -1))
    pos_peak_rh_info = find_peak_location(roi_signal_rh_map)
    return sub_type, sub_name, sub_site, pos_peak_lh_info[0], pos_peak_lh_info[1], pos_peak_rh_info[0], pos_peak_rh_info[1]
    
future_results = run(hipp_response_peak, all_files)
out_columns = ['data_type', 'subject', 'tms_site', 'lh_response_value', 'lh_response_coord', 'rh_response_value', 'rh_response_coord']
df_out = pd.DataFrame(future_results, columns=out_columns)
df_out.to_csv('AllSubs_TMS_Site_Hipp_Response_Peak_Coord.csv', index=None)  

#######################################################################################################################################33
rest_info = pd.read_csv('rest_IndivMask_Hipp_Coord.csv')
all_subs = np.unique(rest_dir_info['subject']) 
all_subs = [x for x in all_subs if 'mm' not in x] # 73 subjects referred to IndVidualMask

def coord2voxel(my_coord, img_affine):
    mni_x, mni_y, mni_z = my_coord[0], my_coord[1], my_coord[2]
    coords = np.c_[
        np.atleast_1d(mni_x).flat,
        np.atleast_1d(mni_y).flat,
        np.atleast_1d(mni_z).flat,
        np.ones_like(np.atleast_1d(mni_z).flat),
    ].T
    project_affine = np.linalg.inv(img_affine)
    voxel_x, voxel_y, voxel_z, _ = np.around(np.dot(project_affine, coords))
    return voxel_x.item(), voxel_y.item(), voxel_z.item()

def compute_fr(matrix_a, matrix_b):
    mean_a = np.nanmean(matrix_a, axis=0)
    mean_b = np.nanmean(matrix_b, axis=0)
    std_a = np.nanstd(matrix_a, axis=0)
    std_b = np.nanstd(matrix_b, axis=0)
    covariance_matrix = np.mean((matrix_a - mean_a) * (matrix_b - mean_b), axis=0)
    np.seterr(invalid='ignore') # ignore the warning message because 0/0 = nan.
    fr = covariance_matrix / (std_a * std_b)
    return fr

def find_peak_location(input_img):
    # data could be 3D or 4D, but is only meaningful in 3D
    img_data = input_img.get_fdata()
    # max
    max_peak_flat = np.argmax(img_data)
    max_peak_index = np.unravel_index(max_peak_flat, img_data.shape)
    max_voxel_coord = [max_peak_index[0], max_peak_index[1], max_peak_index[2]]
    max_coord = apply_affine(input_img.affine, max_voxel_coord)
    # min
    min_peak_flat = np.argmin(img_data)
    min_peak_index = np.unravel_index(min_peak_flat, img_data.shape)
    min_voxel_coord = [min_peak_index[0], min_peak_index[1], min_peak_index[2]]
    min_coord = apply_affine(input_img.affine, min_voxel_coord)
    # output
    return max_voxel_coord, max_coord, min_voxel_coord, min_coord
    
def compute_parietal_activation(sub_name):
    #### defined
    rest_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/xcp_d_36P_Head05'
    rh_parietal_file = 'rh_parietal_tpl.nii.gz'
    Hipp_L_mask = f'lh_hipp_coord_6mm_tpl.nii.gz'
    Hipp_R_mask = f'rh_hipp_coord_6mm_tpl.nii.gz'
    sub_size = 'hipp_coord_6mm'
    #### prepare func file
    rest_file = os.path.join(rest_dir, sub_name, 'func', f'{sub_name}_task-rest_space-MNI152NLin6Asym_res-2_desc-denoisedSmoothed_bold.nii.gz')
    #### activation map
    output_dir = 'RH_Parietal_Hipp_Activation'
    # time = 15s for each Hipp
    # Hipp_L[0][:,0].shape = (234,)
    Hipp_L = regions.img_to_signals_labels(rest_file, labels_img=Hipp_L_mask, background_label=0, order='F', strategy='mean', keep_masked_labels=False)
    Hipp_R = regions.img_to_signals_labels(rest_file, labels_img=Hipp_R_mask, background_label=0, order='F', strategy='mean', keep_masked_labels=False)
    Hipp_L_1d = Hipp_L[0][:,0] # (234,)
    Hipp_R_1d = Hipp_R[0][:,0]
    parietal_mask = maskers.NiftiMasker(mask_img=rh_parietal_file, smoothing_fwhm=None, standardize=False, 
                                    standardize_confounds=False, detrend=False,
                                    low_pass=None, high_pass=None, t_r=None)
    parietal_mask.fit(rh_parietal_file)
    roi_img_2d = parietal_mask.transform(rest_file) # (234, 25610)
    ############################### LH
    Hipp_L_2d = np.tile(Hipp_L_1d, (roi_img_2d.shape[1], 1)).T # (234, 25610)
    Hipp_L_roi_img_fc = compute_fr(roi_img_2d, Hipp_L_2d) # (25610,)
    Hipp_L_roi_img_fc_map = parietal_mask.inverse_transform(Hipp_L_roi_img_fc.reshape(1,-1)) # (1, 25610)
    Hipp_L_roi_img_fc_map.to_filename(os.path.join(output_dir, f'{sub_name}_L-Hipp_R-Parietal_FcMap.nii.gz'))
    peak_info_L = find_peak_location(Hipp_L_roi_img_fc_map)
    ############################### RH    
    Hipp_R_2d = np.tile(Hipp_R_1d, (roi_img_2d.shape[1], 1)).T # (234, 25610)
    Hipp_R_roi_img_fc = compute_fr(roi_img_2d, Hipp_R_2d) # (25610,)
    Hipp_R_roi_img_fc_map = parietal_mask.inverse_transform(Hipp_R_roi_img_fc.reshape(1,-1)) # (1, 25610)
    Hipp_R_roi_img_fc_map.to_filename(os.path.join(output_dir, f'{sub_name}_R-Hipp_R-Parietal_FcMap.nii.gz'))
    peak_info_R = find_peak_location(Hipp_R_roi_img_fc_map)
    # output, 50s
    return sub_name, sub_size, peak_info_L[0], peak_info_L[1], peak_info_L[2], peak_info_L[3], peak_info_R[0], peak_info_R[1], peak_info_R[2], peak_info_R[3]

future_results = run(compute_parietal_activation, all_subs)
out_columns = ['subject', 'data_type', 'LH_PosPeak_voxel', 'LH_PosPeak_coord', 'LH_NegPeak_voxel', 'LH_NegPeak_coord', 'RH_PosPeak_voxel', 'RH_PosPeak_coord', 'RH_NegPeak_voxel', 'RH_NegPeak_coord']
df_out = pd.DataFrame(future_results, columns=out_columns)
df_out.to_csv('rest_LR-Hipp_R-Parietal_PeakCoord.csv', index=None)





