import os
from glob import glob
from nibabel import load
import json
import numpy as np
import pandas as pd
import re

def get_sub_tr(sub, bids):
    # anat
    anat_json = []; anat_nii = []; anat_match = []
    anat_dir = os.path.join(bids, sub, 'anat')
    anat_files = glob(os.path.join(anat_dir, '*.nii.gz'))  
    if len(anat_files) == 0:
        anat_json.append([]); anat_nii.append([]); anat_match.append([])
    else:
        for anat_file in anat_files:
            Img = load(anat_file)
            Img_tr = round(Img.header['pixdim'][4], 4)
            anat_file_json = anat_file.replace('.nii.gz', '.json')
            with open(anat_file_json, 'r') as afj:
                anat_file_json_data = json.load(afj)
                Json_tr = np.float32(anat_file_json_data['RepetitionTime'])
                afj.close()
            Mat_tr = str(round(Img_tr, 4)== round(Json_tr, 4))
            anat_json.append(Json_tr); anat_nii.append(Img_tr); anat_match.append(Mat_tr)
    # func
    func_json = []; func_nii = []; func_match = []
    func_dir = os.path.join(bids, sub, 'func')
    func_files = glob(os.path.join(func_dir, '*.nii.gz'))
    if len(func_files) == 0:
        func_json.append([]); func_nii.append([]); func_match.append([])        
    else:
        for func_file in func_files:
            Img = load(func_file)
            Img_tr = round(Img.header['pixdim'][4], 4)
            func_file_json = func_file.replace('.nii.gz', '.json')
            with open(func_file_json, 'r') as afjjj:
                func_file_json_data = json.load(afjjj)
                Json_tr = np.float32(func_file_json_data['RepetitionTime'])
                afjjj.close()
            Mat_tr = str(round(Img_tr, 4)== round(Json_tr, 4))
            func_json.append(Json_tr); func_nii.append(Img_tr); func_match.append(Mat_tr)
    return sub, anat_json, anat_nii, anat_match, func_json, func_nii, func_match
            
def list_onedim(old_list):
    new_list = []
    for i in old_list:
        for k in i :
            new_list.append(k)
    return(new_list)

def check_tr():
    SubID = []; AnatJson = []; AnatNii = []; AnatMatch = []; FuncJson = []; FuncNii = []; FuncMatch = []
    current_dir = os.getcwd()
    bids = os.path.join(current_dir, 'BIDS')
    sub_list = [os.path.basename(x) for x in glob(os.path.join(bids, 'sub*'))]
    for sub in sub_list:
        subid, aj, an, am, fj, fn, fm = get_sub_tr(sub, bids)
        SubID.append(subid)
        AnatJson.append(aj)
        AnatNii.append(an)
        AnatMatch.append(am)
        FuncJson.append(fj)
        FuncNii.append(fn)
        FuncMatch.append(fm)
    check_df = pd.DataFrame({
        'participant_id': SubID,
        'AnatJson': AnatJson,
        'AnatNifti': AnatNii,
        'AnatMatch': AnatMatch,
        'FuncJson': FuncJson,
        'FuncNifti': FuncNii,
        'FuncMatch': FuncMatch
    })
    # output
    if 'False' in list_onedim(AnatMatch) or 'False' in list_onedim(FuncMatch):
        file_name = os.path.join(current_dir, "TR_not_match_and_need_fix.csv")
        check_df.to_csv(file_name, header=True, index=None, sep='\t')
        print("TR are not matched between json and nifti, please fix it.")
    else:
        file_name = os.path.join(current_dir, "start_for_fmriprep.csv")
        check_df.to_csv(file_name, header=True, index=None, sep='\t')
        print("TR are matched well, you can execute fmriprep now.")

if __name__ == '__main__':
    check_tr()
### end. author@kangwu.