import os
import json
from shutil import move, copy
# This script will replace the func brain mask with MNI brain mask

from glob import glob
old_mask = glob(f'fmriprep/sub-*/func/sub-*_space-MNI152NLin2009cAsym_res-2_desc-brain_mask.nii.gz')
len(old_mask)

temp_mask = '/home/clancy/TemplateFlow/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-02_desc-brain_mask.nii.gz'
for mask in old_mask:
    # mask = mni_mask, mask_replaced = org_mask
    mask_replaced = mask.replace('brain_mask.nii.gz', 'brain_mask_fmrip.nii.gz')
    mask_new = mask
    move(mask, mask_replaced)
    copy(temp_mask, mask_new)
    # mask description
    mask_description = {
        "Step": "replace mask created by fmriprep wtih standard MNI mask",
        "Function": "enhance comparison of ALFF",
        "Author": "Kang Wu",
        }
    mask_description_name = mask_replaced.replace('.nii.gz', '.json')
    with open(mask_description_name, 'w') as json_file:
        json.dump(mask_description, json_file, indent=4)

print('finished.')