#!/bin/bash

#$ -N segmentation
#$ -pe smp 20
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/logs
#$ -t 1-2:1

subject=`cat /Shared/jianglab/3_Data_Working/tms_project_wk/project/sublist_test | head -n+${SGE_TASK_ID} | tail -n-1`

#Set up dependencies

export FREESURFER_HOME=/Shared/pinc/sharedopt/apps/freesurfer/Linux/x86_64/7.4.0
export SUBJECTS_DIR=/Shared/jianglab/3_Data_Working/tms_project_wk/project/data_input
export FS_LICENSE=/Shared/jianglab/3_Data_Working/tms_project_wk/project/license.txt

export FSL_DIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
export FSLDIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
source ${FSLDIR}/etc/fslconf/fsl.sh



source ${FREESURFER_HOME}/FreeSurferEnv.sh


##########
# freesurfer

sub_name="${subject%.nii.gz}"

# freesurfer
recon-all -i /Shared/jianglab/3_Data_Working/tms_project_wk/project/data_input/${subject} -s ${sub_name} -sd /Shared/jianglab/3_Data_Working/tms_project_wk/project/freesurfer/ -all
echo "freesurfer successfully finished."

# fsl
mkdir /Shared/jianglab/3_Data_Working/tms_project_wk/project/fsl/${sub_name}
run_first_all -m auto -i /Shared/jianglab/3_Data_Working/tms_project_wk/project/data_input/${subject} -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/fsl/${sub_name}/output
echo "fsl successfully finished."

# author@kangwu
