#! /bin/bash

# This script is created for VMB analysis in Freesurfer & FSL.
# longitudinal analysis in Freesurfer is better than normal analysis.

# Steps of longitudinal analysis include
#    1) recon-all for each person per time point
#    2) recon-all -base -all for generating robust template
#    3) recon-all -long -all for generating comparable VBM to analysis between a person in two/more time points

##########################################################################################################
###    Step 1
#!/bin/bash

#$ -N seg-failed
#$ -pe smp 35
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/logs
#$ -t 1-102:1
subject=`cat /Shared/jianglab/3_Data_Working/tms_project_wk/project/sublist | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
export FREESURFER_HOME=/Shared/pinc/sharedopt/apps/freesurfer/Linux/x86_64/7.4.0
export SUBJECTS_DIR=/Shared/jianglab/3_Data_Working/tms_project_wk/project/data_input
export FS_LICENSE=/Shared/jianglab/3_Data_Working/tms_project_wk/project/license.txt
source ${FREESURFER_HOME}/FreeSurferEnv.sh
export FSL_DIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
export FSLDIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
source ${FSLDIR}/etc/fslconf/fsl.sh
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

##########################################################################################################
###    Step 2. generate SUB1_S1+2_robust_template
recon-all -base SUB1_S1+2_robust_template -tp SUB1 -tp SUB1_S2 -all

#!/bin/bash

#$ -N seg-template
#$ -pe smp 35
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/logs
#$ -t 1-51:1
subject=`cat /Shared/jianglab/3_Data_Working/tms_project_wk/project/sublist_S2 | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
export FREESURFER_HOME=/Shared/pinc/sharedopt/apps/freesurfer/Linux/x86_64/7.4.0
export SUBJECTS_DIR=/Shared/jianglab/3_Data_Working/tms_project_wk/project/freesurfer
export FS_LICENSE=/Shared/jianglab/3_Data_Working/tms_project_wk/project/license.txt
source ${FREESURFER_HOME}/FreeSurferEnv.sh
##########
# freesurfer
sub_name="${subject%_S2}"
# freesurfer
recon-all -base ${sub_name}_robust_template -tp ${sub_name} -tp ${sub_name}_S2 -all
echo "freesurfer successfully finished."

##########################################################################################################
###    Step 3. generate SUB1.long.SUB1_S1+2_robust_template
recon-all -long SUB1 SUB1_S1+2_robust_template -all

#!/bin/bash

#$ -N seg-long
#$ -pe smp 35
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/logs
#$ -t 1-102:1
subject=`cat /Shared/jianglab/3_Data_Working/tms_project_wk/project/sublist_S3 | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
export FREESURFER_HOME=/Shared/pinc/sharedopt/apps/freesurfer/Linux/x86_64/7.4.0
export SUBJECTS_DIR=/Shared/jianglab/3_Data_Working/tms_project_wk/project/freesurfer
export FS_LICENSE=/Shared/jianglab/3_Data_Working/tms_project_wk/project/license.txt
source ${FREESURFER_HOME}/FreeSurferEnv.sh
##########
# freesurfer
word="S2"
if [[ ${subject} == *"${word}"* ]]; then
    sub_name="${subject%.nii.gz}"
    sub_basename="${subject%_S2.nii.gz}"
else
    sub_name="${subject%.nii.gz}"
    sub_basename="${subject%.nii.gz}"
fi

# freesurfer
recon-all -long ${sub_name} ${sub_basename}_robust_template -all
echo "freesurfer successfully finished."

##########################################################################################################
###    Step 4. generate hipoo-amygdala through -long-base segmentation
ls freesurfer | grep robust_template | grep -v 'long' > sublist_S4
segment_subregions hippo-amygdala --long-base xx_robust_template
# hippo-amygdala, thalamus, brainstem
# 17.22 mins per sub. Generate subregion files in each time sub.long.xxtemplate dir,
# eg. SUB1.long.SUB1_robust_template/mri/lh.hippoAmygLabels.long.FS60.FSvoxelSpace.mgz

#!/bin/bash

#$ -N hippo-long
#$ -pe smp 35
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/tms_project_wk/project/logs
#$ -t 1-51:1
subject=`cat /Shared/jianglab/3_Data_Working/tms_project_wk/project/sublist_S4 | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
export FREESURFER_HOME=/Shared/pinc/sharedopt/apps/freesurfer/Linux/x86_64/7.4.0
export SUBJECTS_DIR=/Shared/jianglab/3_Data_Working/tms_project_wk/project/freesurfer
export FS_LICENSE=/Shared/jianglab/3_Data_Working/tms_project_wk/project/license.txt
source ${FREESURFER_HOME}/FreeSurferEnv.sh
##########
# freesurfer
segment_subregions hippo-amygdala --long-base ${subject}
echo "freesurfer successfully finished."
