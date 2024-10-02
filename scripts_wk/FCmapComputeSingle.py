from nilearn.maskers import NiftiMasker
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm
from itertools import product
import re
from os.path import basename

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=3) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

def compute_fr_fz(matrix_a, matrix_b):
    mean_a = np.mean(matrix_a, axis=0)
    mean_b = np.mean(matrix_b, axis=0)
    std_a = np.std(matrix_a, axis=0)
    std_b = np.std(matrix_b, axis=0)
    covariance_matrix = np.mean((matrix_a - mean_a) * (matrix_b - mean_b), axis=0)
    np.seterr(invalid='ignore') # ignore the warning message because 0/0 = nan.
    fr = covariance_matrix / (std_a * std_b)
    fr[np.isnan(fr)] = 0
    #fz = np.arctanh(fr)
    #return fz
    return fr

def FCmapCompute(bold_file, lesion_file, mni_mask):
    # bold_file: 4D image
    # lesion_file: 3D image
    # return: 3D FCmap
    # elapse time: 12.4337s
    masker = NiftiMasker(mask_img=mni_mask, smoothing_fwhm=None, standardize=False, 
                                standardize_confounds=False)
    masker.fit(mni_mask)
    lesion_mask = masker.transform(lesion_file)
    bold_data = masker.transform(bold_file)
    lesion_data = np.mean(lesion_mask * bold_data, axis=1)
    lesion_mask_inverse = 1 - lesion_mask
    lesion_inverse_data = np.multiply(lesion_mask_inverse, bold_data)
    lesion_data_shape = lesion_data[:, np.newaxis]
    lesion_local_data = np.tile(lesion_data_shape, lesion_inverse_data.shape[1])
    r_map = compute_fr_fz(lesion_local_data, lesion_inverse_data)
    ## define out_name
    bold_file_name = re.findall(r'(.*)_space-MNI152NLin6Asym', basename(bold_file))[0]
    lesion_file_name = re.findall(r'(.*)_2mm_tpl', basename(lesion_file))[0]
    out_name = f'{bold_file_name}_{lesion_file_name}.nii.gz'
    return masker.inverse_transform(r_map).to_filename(out_name)

def FCmapCompute_batch(args):
    return FCmapCompute(*args)

if __name__ == '__main__':

    from glob import glob
    bold_files = glob('xcp_d/sub-20240930/func/sub-*_space-MNI152NLin6Asym_res-2_desc-denoisedSmoothed_bold.nii.gz')
    lesion_files = glob('fcmap/lesion/*.nii.gz')
    mni_mask = '/home/clancy/TemplateFlow/tpl-MNI152NLin6Asym/tpl-MNI152NLin6Asym_res-02_desc-brain_mask.nii.gz'
    this_item = list(product(bold_files, lesion_files, [mni_mask]))
    run(FCmapCompute_batch, this_item)
    print('finished.')

    

