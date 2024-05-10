# atlas trasform
from nilearn import image, regions
import numpy as np
import os
import re
from glob import glob
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import product
import pandas as pd

template = 'tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz'
sub_example = '/home/clancy/data/BigData/chronic_fatigue/xcp_d_155/sub-sub001/func/sub-sub001_task-rest_space-MNI152NLin2009cAsym_res-2_desc-denoisedSmoothed_bold.nii.gz'

check_result = image.load_img(template).affine == image.load_img(sub_example).affine
if check_result.all():
    print('same')
else:
    print('different')
# answer is: same

input_file = 'BN_Atlas_246_2mm.nii.gz' # 91x109x91
interpolation_para = 'MultiLabel'
output_file = 'tpl-MNI152NLin2009cAsym_res-02_atlas-BN_desc-246_dseg.nii.gz'
reference_file = 'tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz'
transform_file = 'tpl-MNI152NLin2009cAsym_from-MNI152NLin6Asym_mode-image_xfm.h5'
os.system(f'antsApplyTransforms --default-value 0 \
                                --float 0 \
                                --input {input_file} \
                                --interpolation {interpolation_para} \
                                --output {output_file} \
                                --reference-image {reference_file} \
                                --transform {transform_file}')

check_result = image.load_img(output_file).affine == image.load_img(sub_example).affine
if check_result.all():
    print('same')
else:
    print('different')
# answer is: same

#######################################################
# functions to compute correlation matrix
def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def create_func_network(func_file, out_func_dir, func_atlas):
    sub_name = re.findall(r'(sub-.*)_task-rest', os.path.basename(func_file))[0]
    # keep_masked_labels=False has been deprecated
    # df[0] = (TimePoints, Regions)
    df = regions.img_to_signals_labels(func_file, labels_img=func_atlas, background_label=0, strategy='mean')
    df_cor = pd.DataFrame(df[0]).corr(method='pearson') # (Regions, Regions)
    df_cor.replace(1, 0, inplace=True) # make diagonal to be zero
    df_out_name = os.path.join(out_func_dir, f'PearCor_{sub_name}.txt')
    df_cor.to_csv(df_out_name, header=None, index=None, sep=' ')

def create_func_network_batch(args):
    return create_func_network(*args)

#######################################################
# functional network construction
#### CFS
func_atlas = '/home/clancy/Desktop/BrainFunction/Atlas/tpl-MNI152NLin2009cAsym_res-02_atlas-BN_desc-246_dseg.nii.gz'
out_func_dir = '/home/clancy/Desktop/BrainFunction/NetFunc/CFS'
func_dir = '/home/clancy/data/BigData/chronic_fatigue/xcp_d_155'
func_files = glob(os.path.join(func_dir, '*', 'func', '*_task-rest_space-MNI152NLin2009cAsym_res-2_desc-denoisedSmoothed_bold.nii.gz'))
func_iters = list(product(func_files, [out_func_dir], [func_atlas]))
run(create_func_network_batch, func_iters)

#### large population
func_atlas = '/home/clancy/Desktop/BrainFunction/Atlas/tpl-MNI152NLin2009cAsym_res-02_atlas-BN_desc-246_dseg.nii.gz'
out_func_dir = '/home/clancy/Desktop/BrainFunction/NetFunc/ISYB'
func_dir = '/home/clancy/data/BigData/isyb_bigdata/xcp_d_215'
func_files = glob(os.path.join(func_dir, '*', 'func', '*_task-rest_space-MNI152NLin2009cAsym_res-2_desc-denoisedSmoothed_bold.nii.gz'))
func_iters = list(product(func_files, [out_func_dir], [func_atlas]))
run(create_func_network_batch, func_iters)

#######################################################
# functions to compute fiber correlation matrix
## prepare MNI IPL atlas
input_file = '/home/clancy/qsirecon_atlas/qsirecon_atlases/brainnetome246MNI_lps.nii.gz' # 182x218x182
interpolation_para = 'MultiLabel'
output_file = 'tpl-MNI152NLin2009cAsym_res-01_atlas-BN246_desc-LPS_dseg.nii.gz' 
reference_file = '/home/clancy/qsirecon_atlas/mni_1mm_t1w_lps.nii.gz' # 193x229x193
transform_file = 'tpl-MNI152NLin2009cAsym_from-MNI152NLin6Asym_mode-image_xfm.h5'
os.system(f'antsApplyTransforms --default-value 0 \
                                --float 0 \
                                --input {input_file} \
                                --interpolation {interpolation_para} \
                                --output {output_file} \
                                --reference-image {reference_file} \
                                --transform {transform_file}')
## functions
def create_fiber_network(fiber_file, fiber_prep_dir, out_fiber_dir, fiber_atlas):
    sub_name = re.findall(r'(sub-.*)_space-T1w', os.path.basename(fiber_file))[0]
    # MNI to dwi T1 space
    input_file = fiber_atlas
    interpolation_para = 'MultiLabel'
    output_atlas_file = f'{sub_name}_atlas-BN246_desc-LPS_dseg_to_dwi.nii.gz'
    reference_file = os.path.join(fiber_prep_dir, sub_name, 'dwi', f'{sub_name}_space-T1w_desc-preproc_dwi.nii.gz')
    transform_file = os.path.join(fiber_prep_dir, sub_name, 'anat', f'{sub_name}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5')
    os.system(f'antsApplyTransforms --default-value 0 \
                                --float 0 \
                                --input {input_file} \
                                --interpolation {interpolation_para} \
                                --output {output_atlas_file} \
                                --reference-image {reference_file} \
                                --transform {transform_file}')
    # SIFT2
    sift2_weight = os.path.join(os.path.dirname(fiber_file), f'{sub_name}_space-T1w_desc-preproc_desc-siftweights_ifod2.csv')
    # matrix_connectome: sift_invmodevol_radius2_count
    out_matrix = os.path.join(out_fiber_dir, f'Connectome_{sub_name}.txt')
    os.system(f'tck2connectome -tck_weights_in {sift2_weight} \
                                -nthreads 1 \
                                -quiet \
                                -scale_invnodevol \
                                -assignment_radial_search 2.000000 \
                                -stat_edge sum \
                                -symmetric \
                                -zero_diagonal \
                                {fiber_file} \
                                {output_atlas_file} \
                                {out_matrix} ')
    # delete derivatives
    os.remove(output_atlas_file)

def create_fiber_network_batch(args):
    return create_fiber_network(*args)

#######################################################
# fiber network construction
fiber_atlas = 'tpl-MNI152NLin2009cAsym_res-01_atlas-BN246_desc-LPS_dseg.nii.gz'
#### CFS
fiber_prep_dir = '/home/clancy/data/BigData/chronic_fatigue/qsiprep_155'
out_fiber_dir = '/home/clancy/Desktop/BrainFunction/NetFiber/CFS'
fiber_dir = '/home/clancy/data/BigData/chronic_fatigue/qsirecon_155'
fiber_files = glob(os.path.join(fiber_dir, '*', 'dwi', '*_space-T1w_desc-preproc_desc-tracks_ifod2.tck'))
fiber_iters = list(product(fiber_files, [fiber_prep_dir], [out_fiber_dir], [fiber_atlas]))
run(create_fiber_network_batch, fiber_iters)
#### large population
fiber_prep_dir = '/home/clancy/data/BigData/isyb_bigdata/qsiprep_215'
out_fiber_dir = '/home/clancy/Desktop/BrainFunction/NetFiber/ISYB'
fiber_dir = '/home/clancy/data/BigData/isyb_bigdata/qsirecon_215'
fiber_files = glob(os.path.join(fiber_dir, '*', 'dwi', '*_space-T1w_desc-preproc_desc-tracks_ifod2.tck'))
fiber_iters = list(product(fiber_files, [fiber_prep_dir], [out_fiber_dir], [fiber_atlas]))
run(create_fiber_network_batch, fiber_iters)

######## end. author@kangwu.
