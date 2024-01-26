#!/bin/python10
#!/bin/python3.10
## GLM

def get_name(file):
    middle_file = os.path.basename(file)
    sub_name = re.findall(r'sub-\d+', middle_file)[0]
    sub_pos = re.findall(r'_(\w+).nii', middle_file)[0]
    return sub_name,sub_pos

def get_headmotion(sub_name, sub_pos, motion_para):
    motion_file = glob(os.path.join('fmriprep', sub_name, 'func','*' + sub_pos + '*confounds_timeseries.tsv'))[0]
    motion_data = pd.read_csv(motion_file, sep='\t', header=0)
    motion_para_data = motion_data.loc[:, motion_para]
    return (motion_para_data)

def map_compute_stand(file):
    six_motion_para = ['trans_x', 'trans_y', 'trans_z', 'rot_x', 'rot_y', 'rot_z'] # add_reg_names
    motion_file_sub, motion_file_pos = get_name(file)
    motion_data = get_headmotion(motion_file_sub, motion_file_pos, six_motion_para)
    X1 = make_first_level_design_matrix(frame_times, events, drift_model=None, drift_order=None, 
                                        add_regs=motion_data, add_reg_names=six_motion_para, hrf_model='spm')
    # mask
    mask_img = 'GrayMask/gray_thr0.3.nii' # standard gray mask threshold=0.3
    fmri_glm = FirstLevelModel(
                    t_r = 2.4,
                    slice_time_ref=0,
                    high_pass=None,
                    standardize=False,
                    hrf_model='spm',
                    drift_model=None,
                    drift_order=None,
                    mask_img=mask_img,
                    subject_label= motion_file_sub
                )
    fmri_glm = fmri_glm.fit(run_imgs=file, design_matrices=X1)
    # zmap
    z_map_dir = os.path.join('Results/glm_gm/simple/zmap_files', motion_file_sub)
    if not os.path.exists(z_map_dir):
        os.mkdir(z_map_dir)
    z_map = fmri_glm.compute_contrast(['TMSpulse'], stat_type = None, output_type = 'z_score')
    z_map_name = os.path.join(z_map_dir, 'zmap_' + motion_file_pos + '.nii.gz')
    z_map.to_filename(z_map_name)
    # report
    report = make_glm_report(
    fmri_glm, contrasts=['TMSpulse'], title = 'TMS pulse on ' + motion_file_pos + ' for ' + motion_file_sub, 
                                    cluster_threshold=15, plot_type='glass', bg_img=None)
    report_name = os.path.join(z_map_dir, motion_file_pos + '.html')
    report.save_as_html(report_name)
    # beta
    beta_map_dir = os.path.join('Results/glm_gm/simple/beta_files', motion_file_sub)
    if not os.path.exists(beta_map_dir):
        os.mkdir(beta_map_dir)
    beta_map = fmri_glm.compute_contrast(['TMSpulse'], stat_type = None, output_type = 'effect_size')
    beta_map_name = os.path.join(beta_map_dir, 'beta_' + motion_file_pos + '.nii.gz')
    beta_map.to_filename(beta_map_name)
    # report
    report = make_glm_report(
    fmri_glm, contrasts=['TMSpulse'], title = 'TMS pulse on ' + motion_file_pos + ' for ' + motion_file_sub, 
                                    cluster_threshold=15, plot_type='glass', bg_img=None)
    report_name = os.path.join(beta_map_dir, motion_file_pos + '.html')
    report.save_as_html(report_name)

def run(f, file):
    with ProcessPoolExecutor(max_workers=14) as executor:
        results = list(tqdm(executor.map(f, file), total=len(file)))
    return results

if __name__ == "__main__":
    # 1. paramaters defined
    import numpy as np
    import os
    import re
    tr = 2.4
    n_scans = 161
    frame_times = np.arange(n_scans) * tr
    import pandas as pd
    events_df = pd.read_csv('Results/glm_gm/CC_ERtiming_stim.csv')
    conditions = events_df['trial_type'].values
    durations = events_df['duration'].values
    onsets = events_df['onset'].values - 3*tr
    events = pd.DataFrame(
        {'trial_type': conditions, 'onset': onsets, 'duration': durations})
    # motion paramaters

    from glob import glob
    from nilearn.glm.first_level import make_first_level_design_matrix, FirstLevelModel
    from nilearn.reporting import make_glm_report
    from concurrent.futures import ProcessPoolExecutor
    from tqdm import tqdm

    # start
    glm_dir = 'Results/VolumesFilter_simple'
    glm_niis = glob(os.path.join(glm_dir, '*/*.nii.gz'))
    files = glm_niis

    run(map_compute_stand, files)

