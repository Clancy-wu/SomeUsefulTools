from nilearn import image
import re
import numpy as np
import pandas as pd
from glob import glob
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

org_data_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/fmriprep'
out_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/model_free_results'
brain_func_mask = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/mask/MNI152_T1_2mm_brain_mask.nii'
# the brain_func_mask has been reshaped with fMRIPrep and is used on tmsfmri_pipeline_prepare

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=30) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def get_headmotion(func_para, motion_para):
    confound_data = pd.read_csv(func_para, sep='\t', header=0)
    motion_data = confound_data.loc[:, motion_para]
    return motion_data

def model_free_process(sub_name):
    # sub_name: sub-1001
    ## file: xx/xx/sub-1021_task-LaMFG_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz
    func_files = glob(os.path.join(org_data_dir, sub_name, 'func', '*space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz'))
    sub_out = os.path.join(out_dir, sub_name)
    if not os.path.exists(sub_out):
        os.mkdir(sub_out)
    # start to process
    for func_file in func_files:
        func_data = image.get_data(func_file)
        func_para = func_file.replace('space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz', 'desc-confounds_timeseries.tsv')
        motion_para = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] # remove 6 head motion
        # headmotion regression
        motion_data = get_headmotion(func_para, motion_para)
        # filter to ~ 0.008
        # SPM12 High-pass filter: The default high-pass filter cutoff is 128 seconds. Slow signal
        # drifts with a period longer than this will be removed.
        # standardize = False, see https://nilearn.github.io/stable/auto_examples/04_glm_first_level/
        # plot_predictions_residuals.html#sphx-glr-auto-examples-04-glm-first-level-plot-predictions-residuals-py
        deIMG = image.clean_img(func_file, mask_img=brain_func_mask, detrend=False, standardize=False, confounds=motion_data, low_pass=None, high_pass=0.008, t_r=2.4)
        image.smooth_img(deIMG, fwhm=6).to_filename(os.path.join(sub_out, 'DeSmooth_'+os.path.basename(func_file))) # smooth 6

all_dirs = [x for x in os.listdir(org_data_dir) if 'sub-' in x and 'html' not in x]
health_subs = [x for x in all_dirs if 'sub-1' in x or 'sub-2' in x] # 82
run(model_free_process, health_subs)
print('finished.')
