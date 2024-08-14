import os
from nilearn import image
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

#### functions
def run(f, this_iter, cpu_num):
    with ProcessPoolExecutor(max_workers=cpu_num) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def track2tdi(file_tck):
    file_tck_name = os.path.join(file_tck)
    file_tck_filter = os.path.join(temp_dir, file_tck_name)
    os.system(f'tckedit {file_tck} -mask {filter_img} {file_tck_filter} -quiet')
    file_tdi = file_tck_filter.replace('tck', 'nii.gz')
    ref_fsl = '/usr/local/fsl/data/standard/MNI152_T1_1mm_brain.nii.gz'
    os.system(f'tckmap {file_tck_filter} -template {ref_fsl} {file_tdi} -quiet')
    os.system(f'fslmaths {file_tdi} -thr 0 -bin {file_tdi}')
    return 0

if __name__ == '__main__':
    ###################################################################
    ## self define
    tck_dir = '/home/clancy/Desktop/dti_dlpfc_amyg/tck_data/dlpfc_amyg_lh'
    out_dir = '/home/clancy/Desktop/dti_dlpfc_amyg/Results'
    filter_img = '/home/clancy/Desktop/dti_dlpfc_amyg/atlas/MNI152_T1_1mm_brain_mask_LH.nii.gz'
    cpu_num = 5
    ###################################################################
    ## main run
    temp_dir = os.path.join(out_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    all_tracks = glob(f'{tck_dir}/space_mni/*.tck')
    future_results = run(track2tdi, all_tracks, cpu_num)
    out_tdi_name = os.path.basename(tck_dir) + '_1065Prob.nii.gz'
    image.mean_img(imgs=glob(f'{temp_dir}/*.nii.gz'), n_jobs=cpu_num).to_filename(f'{out_dir}/{out_tdi_name}')
    os.remove(temp_dir)
    print('finished.')
    ###################################################################
    ## Author@kangwu.
