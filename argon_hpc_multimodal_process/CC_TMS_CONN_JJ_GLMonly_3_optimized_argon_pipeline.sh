#!/bin/bash

#$ -N glm_pipeline
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/logs
#$ -t 1-1647:1
OMP_NUM_THREADS=10

subject_info=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/sublist_for_pipeline | head -n+${SGE_TASK_ID} | tail -n-1`

## Set up dependencies
export ANALYSIS_PIPE_DIR=/Shared/jianglab/0_scripts/analysis_pipeline_cd
export SPM8DIR=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/spm8_sge_merge
export BASHDIR=/Shared/jianglab/0_scripts/CausalConnectome
export FSLDIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
source ${FSLDIR}/etc/fslconf/fsl.sh
export MATLAB=/Shared/pinc/sharedopt/apps/matlab/Linux/x86_64/R2022b/bin
export PATH=${MATLAB}:$PATH

## Set scripts
TMSDIR=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/tmsfmri_pipeline_prepare
BRAIN_FUNC_MASK=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/mask/MNI152_T1_2mm_brain_mask.nii

##### run contrasts, identical to all subjects
CONS=/Shared/jianglab/0_scripts/CausalConnectome/Design_Con_Files/tms_pulse_con.m
DESIGN=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/CC_ERtiming_stim_six_volumes.mat
SPM_CON_FILE=`readlink -f $CONS`
DESIGN_FILE=`readlink -f $DESIGN`
MODEL_NAME=tms_with_motion

## main run
delimiter="/"
t=$(echo "$subject_info" | cut -d "$delimiter" -f2)  # tms site
s=$(echo "$subject_info" | cut -d "$delimiter" -f3)  # sub name

echo RUNNING TMS on ${t} ${s}

OUTPUTDIR=${TMSDIR}/${t}/${s}                        # output dir
mod_t=$(echo $t | sed 's/_//')                       # modified site
MOTION_FILE=${OUTPUTDIR}/${s}_${mod_t}_head_motion.txt  # head motion file
jobdir=${OUTPUTDIR}/${MODEL_NAME}.spm/spm_jobs
mkdir -p ${jobdir}
jobname=${jobdir}/job_model.m
funcfile=${OUTPUTDIR}/${s}_task-${mod_t}_space-MNI152NLin6Asym_res-2_desc-preproc_bold_smooth.nii
TR=2.4
echo ${OUTPUTDIR}  | sed 's/\//\\\//g' >  ${jobdir}/grot
foutdir=`cat ${jobdir}/grot`
/bin/rm ${jobdir}/grot
cat ${SPM_CON_FILE}  | sed "s/'<UNDEFINED>'/{'${foutdir}\/${MODEL_NAME}.spm\/SPM.mat'}/g" > ${jobdir}/job_contrast.m
${ANALYSIS_PIPE_DIR}/analysis_pipeline_createSPM_batch_script.sh ${jobdir}/run_job_contrast.m ${jobdir}/job_contrast.m
${ANALYSIS_PIPE_DIR}/analysis_pipeline_SPMmodel.sh -tr ${TR} -jobname ${jobname} -outdir ${OUTPUTDIR}/${MODEL_NAME}.spm -func_data ${funcfile} -design ${DESIGN_FILE} -motion ${MOTION_FILE} -mask ${BRAIN_FUNC_MASK}
cd ${jobdir}
matlab -nodesktop -nodisplay -nosplash -r run_job_contrast
       
echo ${t} ${s} successfully finished !!!
        
# end. author@kangwu
# date Dec 26 2023
