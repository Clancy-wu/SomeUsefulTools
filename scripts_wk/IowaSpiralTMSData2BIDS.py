import os
from glob import glob
import re
from shutil import copy
import pandas as pd
import json

org_data = 'spiral_test'
bids_dir = 'BIDS_spiral'

#########################################
## main
#########################################
def create_json_for_spiral(run_file):
    run_df = pd.read_table(run_file, header=None)
    Date = re.findall(r'= (.*)', run_df.iloc[5,0])[0]
    Time = re.findall(r'= (.*)', run_df.iloc[6,0])[0]
    SeriesDescription = re.findall(r'= (.*)', run_df.iloc[14,0])[0]
    Fov = float(re.findall(r'\d+\.\d+', run_df.iloc[23,0])[0])
    SliceThickness = float(re.findall(r'\d+\.\d+', run_df.iloc[24,0])[0])
    SpacingBetweenSlices = float(re.findall(r'\d+\.\d+', run_df.iloc[33,0])[0])
    EchoTime = float(re.findall(r'\d+', run_df.iloc[27,0])[0]) / 1000
    RepetitionTime = float(re.findall(r'\d+', run_df.iloc[26,0])[0]) / 1000
    FlipAngle = int(re.findall(r'\d+', run_df.iloc[28,0])[0])
    ReconMatrixPE = int(re.findall(r'\d+', run_df.iloc[31,0])[0])
    bold_json = {
        "Modality": "MR",
        "InstitutionName": "Iowa cavar hospital",
        "Scanner id": "Iowa3T",
        "PulseSequenceName": "Spiral",
        "AcquisitionDate": Date,
        "AcquisitionTime": Time,
        "SeriesDescription": SeriesDescription,
        "Fov": Fov,
        "SliceThickness": SliceThickness,
        "SpacingBetweenSlices": SpacingBetweenSlices,
        "EchoTime": EchoTime,
        "RepetitionTime": RepetitionTime,
        "FlipAngle": FlipAngle,
        "ReconMatrixPE": ReconMatrixPE,
        "ConversionSoftware": "manual",
        "ConversionSoftwareAuthor": "Kang Wu"
    }
    return bold_json

def IowaData2BIDS_main(single_dir):
    sub_name = 'sub-'+os.path.basename(single_dir)
    sub_runs = glob(os.path.join(single_dir, 'E*'))
    sub_runs.sort(key=lambda x: int("".join(re.findall("\d+",x)))) # sort
    run_index = 1
    func_dir = os.path.join(bids_dir, sub_name, 'func')
    os.makedirs(func_dir, exist_ok=True)
    for run in sub_runs:
        # bold file
        run_parent_dir = os.path.dirname(run)
        run_basename = os.path.basename(run)
        run_bold = os.path.join(run_parent_dir, re.findall(r'(P.*)', run_basename)[0]+'.nii')
        run_bold_den = run_bold.replace('.nii', '.den.nii')
        run_bold_new = f'{func_dir}/{sub_name}_task-Spiral_run-{run_index:02}_bold.nii'
        run_bold_den_new = f'{func_dir}/{sub_name}_task-SpiralDen_run-{run_index:02}_bold.nii'
        copy(run_bold, run_bold_new)
        copy(run_bold_den, run_bold_den_new)
        # json file
        run_bold_json_content = create_json_for_spiral(run)
        run_bold_json_new = run_bold_new.replace('.nii', '.json')
        with open(run_bold_json_new, 'w') as wf:
            json.dump(run_bold_json_content, wf, indent='\t')
        run_bold_json_den_new = run_bold_den_new.replace('.nii', '.json')
        with open(run_bold_json_den_new, 'w') as wf:
            json.dump(run_bold_json_content, wf, indent='\t')       
        # next run
        run_index += 1
    return 0

dir_paths = glob(org_data+'/*')
for i in dir_paths:
    IowaData2BIDS_main(i)

# dataset_description
dataset_description = {
    "Name": "Task dataset",
    "BIDSVersion": "1.4.1",
    "Author": "Kang Wu",
    "Acknowledgements": "No",
    "Time": "Aug 31 2024",
    "Others": "Remember work life balance"
    }
with open(os.path.join(bids_dir, 'dataset_description.json'), 'w') as json_file:
    json.dump(dataset_description, json_file, indent='\t')

print('end.')