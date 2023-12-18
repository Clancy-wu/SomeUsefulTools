import os
from glob import glob
from nibabel import load
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import json
import numpy as np

def fix_sub_TR(bids, sub, run_name, refer_to):
    # refer to should be "json" or "nifti"
    # run name is the task name
    if refer_to == 'json':
        right_file = glob(os.path.join(bids, sub, '*', '*'+run_name+'*.json'))[0]
        with open(right_file, 'r') as rf:
            right_data = json.load(rf)
            right_tr = np.float32(right_data['RepetitionTime'])
            rf.close()
        wrong_file = glob(os.path.join(bids, sub, '*', '*'+run_name+'*.nii.gz'))[0]
        wrong_img = load(wrong_file)
        wrong_img.header['pixdim'][4] = right_tr
        wrong_img.to_filename(wrong_file)
    if refer_to == 'nifti':
        right_file = glob(os.path.join(bids, sub, '*', '*'+run_name+'*.nii.gz'))[0]
        right_img = load(right_file)
        right_tr = right_img.header['pixdim'][4]
        wrong_file = glob(os.path.join(bids, sub, '*', '*'+run_name+'*.json'))[0]
        with open(wrong_file, 'r+') as wf:
            wrong_data = json.load(wf)
            wrong_data['RepetitionTime'] = int(right_tr)
            wf.seek(0)
            json.dump(wrong_data, wf, indent=4)
            wf.truncate()

def fix_sub_TR_run(args):
    return fix_sub_TR(*args)

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    current_dir = os.getcwd()
    bids = os.path.join(current_dir, 'BIDS')
    bids_dict = [bids]
    sub_list = [os.path.basename(x) for x in glob(os.path.join(bids, 'sub*'))]
    run_name = ['hand']
    refer_to = ['nifti']
    import itertools
    zip_iter = itertools.product(bids_dict, sub_list, run_name, refer_to)
    this_iter = list(zip_iter)
    run(fix_sub_TR_run, this_iter)
### end. author@kangwu.