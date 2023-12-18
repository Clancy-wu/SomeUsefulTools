import os
from glob import glob
from nibabel import load
from shutil import copy
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import json
import pandas as pd

def get_file_type(file):
    file_name = os.path.basename(file)
    file_suffix = file_name.split('.nii.gz')[0]
    # file is nii.gz
    if 'T1' in file_name:
        return {'name': file_suffix, 'type': 't1w', 'num': 1}
    if 'T2' in file_name:
        return {'name': file_suffix, 'type': 't2w', 'num': 1}
    if 'DTI' in file_name:
        return {'name': file_suffix, 'type': 'dwi', 'num': 1}
    if 'BOLD' in file_name:
        Img = load(file)
        Num = Img.shape[3]
        return {'name': file_suffix, 'type': 'func', 'num': Num}
    else:
        return {'name': file_suffix, 'type': 'pass', 'num': 1}

def sort_bids(sub):
    nii_files = glob(os.path.join(org_data, sub, '*.nii.gz'))
    anat_dir = os.path.join(bids, sub, 'anat')
    func_dir = os.path.join(bids, sub, 'func')
    dwi_dir = os.path.join(bids, sub, 'dwi')
    os.makedirs(anat_dir); os.makedirs(func_dir); os.makedirs(dwi_dir)
    for nii_file in nii_files:
        file_info = get_file_type(nii_file)
        #################  t1
        if file_info['type'] == 't1w':
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(anat_dir, sub+'_T1w.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(anat_dir, sub+'_T1w.json')
            copy(file_old_json, file_new_json)
        #################  t2            
        if file_info['type'] == 't2w':
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(anat_dir, sub+'_T2w.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(anat_dir, sub+'_T2w.json')
            copy(file_old_json, file_new_json)  
        #################  dwi            
        if file_info['type'] == 'dwi':
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(dwi_dir, sub+'_dwi.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(dwi_dir, sub+'_dwi.json')
            copy(file_old_json, file_new_json)   
            file_old_bval = os.path.join(os.path.dirname(nii_file), file_info['name']+'.bval')
            file_new_bval = os.path.join(dwi_dir, sub+'_dwi.bval')
            copy(file_old_bval, file_new_bval)   
            file_old_bvec = os.path.join(os.path.dirname(nii_file), file_info['name']+'.bvec')
            file_new_bvec = os.path.join(dwi_dir, sub+'_dwi.bvec')
            copy(file_old_bvec, file_new_bvec)                                     
        #################  bold                  
        if file_info['type'] == 'func' and file_info['num'] == 11:
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(func_dir, sub+'_task-hand_bold.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(func_dir, sub+'_task-hand_bold.json')
            copy(file_old_json, file_new_json)
        if file_info['type'] == 'func' and file_info['num'] == 180:
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(func_dir, sub+'_task-rest_bold.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(func_dir, sub+'_task-rest_bold.json')
            copy(file_old_json, file_new_json)
        if file_info['type'] == 'func' and file_info['num'] == 271:
            file_old_nii = os.path.join(os.path.dirname(nii_file), file_info['name']+'.nii.gz')
            file_new_nii = os.path.join(func_dir, sub+'_task-acupun_bold.nii.gz')
            copy(file_old_nii, file_new_nii)
            file_old_json = os.path.join(os.path.dirname(nii_file), file_info['name']+'.json')
            file_new_json = os.path.join(func_dir, sub+'_task-acupun_bold.json')
            copy(file_old_json, file_new_json)
        else:
            pass
    # get demographic
    try:
        sub_json_file = os.path.join(anat_dir, sub+'_T1w.json')
        with open(sub_json_file) as jf:
            sub_json = json.load(jf)
            return sub, sub_json['PatientName'], sub_json['PatientSex'], sub_json['PatientWeight']
    except:
        return sub, 'no T1', 'no T1', 'no T1'

def run(f, this_iter):
    with ProcessPoolExecutor(max_workers=8) as executor:
        results = list(tqdm(executor.map(f, this_iter), total=len(this_iter)))
    return results

if __name__ == '__main__':
    # run
    current_dir = os.getcwd()
    org_data = os.path.join(current_dir, 'org_data')
    bids = os.path.join(current_dir, 'BIDS')
    if not os.path.exists(bids):
        os.mkdir(bids)
    sub_list = os.listdir(org_data)
    final_results = run(sort_bids, sub_list)
    
    # participants.tsv
    SubID = []; SubName = []; SubSex = []; SubAge = []
    for result in final_results:
        sub_id, sub_name, sub_sex, sub_age = result
        SubID.append(sub_id)
        SubName.append(sub_name)
        SubSex.append(sub_sex)
        SubAge.append(str(sub_age)+'Y')
    df = pd.DataFrame({
        'participant_id': SubID,
        'Name': SubName,
        'Sex': SubSex,
        'Age': SubAge
    })
    df.to_csv(os.path.join(bids, 'participants.tsv'), header=True, index=None, sep='\t')
    # dataset_description
    dataset_description = {
        "Name": "Example dataset",
        "BIDSVersion": "1.4.1",
        "Author": "Kang Wu",
        "Acknowledgements": "No",
        }
    with open(os.path.join(bids, 'dataset_description.json'), 'w') as json_file:
        json.dump(dataset_description, json_file)
        
    print('finished.')
#### end. author@kangwu.
