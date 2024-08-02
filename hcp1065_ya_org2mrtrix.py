########################################################
## made by kangwu
import os
import subprocess
from shutil import rmtree, move
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

def run(f, this_iter, max_workers):
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def quiet_run(command):
    return subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
def org_to_mrtrix_prepare(sub_name):
    ## make dir
    sub_out_dir = os.path.join(output_dir, f'sub-{sub_name}')
    sub_out_temp = os.path.join(sub_out_dir, 'temp') # temp files
    os.makedirs(sub_out_temp)
    ## prepare files
    sub_dir = os.path.join(hcp1065_dir, sub_name, 'T1w')
    sub_anat = os.path.join(sub_dir, 'T1w_acpc_dc_restore_1.25.nii.gz')
    sub_bvec = os.path.join(sub_dir, 'Diffusion', 'bvecs')
    sub_bvals = os.path.join(sub_dir, 'Diffusion', 'bvals')
    sub_dwi = os.path.join(sub_dir, 'Diffusion', 'data.nii.gz')
    sub_mask = os.path.join(sub_dir, 'Diffusion', 'nodif_brain_mask.nii.gz')
    ## output
    #### 1. anat process
    sub_anat_prepare = os.path.join(sub_out_dir, f'sub-{sub_name}_desc-preproc_T1w.nii.gz')
    anat_bet = f'fslmaths {sub_anat} -mul {sub_mask} {sub_anat_prepare}' 
    quiet_run(anat_bet)
    #### 1.1 register: -f fix -m move
    fsl_template = '/home/clancy/TemplateFlow/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-01_desc-brain_T1w.nii.gz'
    os.chdir(sub_out_temp)
    os.system(f'ln -s {fsl_template} mni_T1w.nii.gz')
    os.system(f'ln -s {sub_anat_prepare} native_T1w.nii.gz')
    anat_register = 'antsRegistrationSyNQuick.sh -d 3 -m mni_T1w.nii.gz -f native_T1w.nii.gz -o mni2native'
    quiet_run(anat_register) # Total elapsed time: 70.01, finished
    anat_transform = os.path.join(sub_out_temp, 'mni2native0GenericAffine.mat')
    anat_transform_prepare = os.path.join(sub_out_dir, f'sub-{sub_name}_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.mat')
    move(anat_transform, anat_transform_prepare)
    #### 2. dwi process
    #### 2.1 create mif
    dwi_convert = f'mrconvert {sub_dwi} dwi.mif -fslgrad {sub_bvec} {sub_bvals} -datatype float32 -strides 0,0,0,1'
    quiet_run(dwi_convert)
    #### 2.2 make mask for RF estimate, do not use the origial mask
    quiet_run('dwi2mask dwi.mif dwi_mask.mif')
    #### 2.3 estimate response, dhollander+msmt_csd is recommended by QSIPrep.
    quiet_run(f'dwi2response dhollander dwi.mif dwi_wm.txt dwi_gm.txt dwi_csf.txt -mask dwi_mask.mif -nthreads {n_thread_per}')
    #### 2.4 estimate FOD
    quiet_run(f'dwi2fod msmt_csd dwi.mif dwi_wm.txt dwi_wm.mif dwi_gm.txt dwi_gm.mif dwi_csf.txt dwi_csf.mif -mask dwi_mask.mif -nthreads {n_thread_per}')
    #### 2.5 norm intensity
    quiet_run(f'mtnormalise dwi_wm.mif dwi_wm_mtnorm.mif dwi_gm.mif dwi_gm_mtnorm.mif dwi_csf.mif dwi_cfs_mtnorm.mif -mask dwi_mask.mif -nthreads {n_thread_per}')
    #### 2.6 prepare dwi_wm_mtnrom
    quiet_run('mrconvert dwi_wm_mtnorm.mif dwi_wm_mtnorm.mif.gz') # 658.5 MB --> 151.9 MB
    dwi_wm_mtnrom = os.path.join(sub_out_temp, 'dwi_wm_mtnorm.mif.gz')
    dwi_wm_mtnrom_prepare = os.path.join(sub_out_dir, f'sub-{sub_name}_space-T1w_desc-preproc_desc-wmFODmtnormed_msmtcsd.mif.gz')
    move(dwi_wm_mtnrom, dwi_wm_mtnrom_prepare)
    # end
    rmtree(sub_out_temp)

########################################################
if __name__ == "__main__":
    hcp1065_dir = '/home/clancy/data/HCP1065/Diffusion_preproc'
    sub_list = os.listdir(hcp1065_dir)
    output_dir = '/home/clancy/Music/test'
    n_thread_per = 1
    parallel_work = 10

    run(org_to_mrtrix_prepare, sub_list[0:10], parallel_work)
    print('finished.')
# @author: kangwu. July 31 2024



