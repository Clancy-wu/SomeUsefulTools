#/bin/python3.8.10
from tqdm import tqdm
from nilearn import image, regions
from glob import glob
import os
from scipy import stats
import pandas as pd
import numpy as np
from concurrent.futures import ProcessPoolExecutor

def group_fc(sub, from_mask, to_mask):
    # compute
    Image_data = os.path.join('Results', 'VolumesFilter_simple', sub + '.nii.gz')
    Image = image.load_img(Image_data)    
    from_mask_name_full = os.path.basename(from_mask).split('.n')[0]
    from_mask_name_f = from_mask_name_full.split('_')
    from_mask_side = from_mask_name_f[0]
    from_mask_name = from_mask_name_f[1]
    from_mask_size = from_mask_name_f[2]
    to_mask_name = os.path.basename(to_mask).split('.')[0]
    # prepare
    from_mask_affined = image.resample_to_img(source_img=from_mask, target_img=Image, interpolation='nearest')
    time_series_from = regions.img_to_signals_labels(Image, labels_img=from_mask_affined, background_label=0, order='F', strategy='mean')
    time_series_to = regions.img_to_signals_labels(Image, labels_img=to_mask, background_label=0, order='F', strategy='mean')
    fcvalue = stats.pearsonr(np.squeeze(time_series_from[0]), np.squeeze(time_series_to[0]), alternative='two-sided').statistic
    # to df
    return(sub, from_mask_name, from_mask_side, from_mask_size, to_mask_name, fcvalue)

def call_func_job(args):
    return group_fc(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=6) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results


group_mask_path = 'mask/GroupEnvMask'
group_mask_10mm = glob(os.path.join(group_mask_path, '*_10mm.nii.gz'))
group_mask_10mm = group_mask_10mm[0:3]
amygdala_mask_path = 'mask/AmygdalaMask'
amygdala_mask = glob(os.path.join(amygdala_mask_path, '*')) 
amygdala_mask = amygdala_mask[0:3]    
subs = glob('fmriprep/sub*')
subs = [os.path.basename(x) for x in subs if os.path.isdir(x)]
subs = subs[0:3]

import itertools
zip_args = itertools.product(subs, group_mask_10mm, amygdala_mask)
this_iter = list(zip_args)
future_results = run(call_func_job, this_iter)

# to df
Subject = []
From_mask = []
From_side = []
From_size = []
To_mask = []
FC_value = []

for Result in future_results:
    sub, from_mask_name, from_mask_side, from_mask_size, to_mask_name, fcvalue = Result
    Subject.append(sub)
    From_mask.append(from_mask_name)
    From_side.append(from_mask_side)
    From_size.append(from_mask_size)
    To_mask.append(to_mask_name)
    FC_value.append(fcvalue)    

df_simple = pd.DataFrame(
        {'Subject': Subject,
        'From': From_mask,
        'Side': From_side,
        'Size': From_size,
        'To': To_mask,
        'FC_value': FC_value
        })

df_simple.to_csv(os.path.join('Results', 'FC', 'simple', 'Group_Amygdala_10mm_Results.csv'), header=True, index=None)  

# end. @clancy_wu