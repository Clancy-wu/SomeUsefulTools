#!/bin/bash

#$ -N glm_pipeline
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid/logs
#$ -t 1-178:1

OMP_NUM_THREADS=10

## Set up dependencies
export ANALYSIS_PIPE_DIR=/Shared/jianglab/0_scripts/analysis_pipeline_cd
export SPM8DIR=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/spm8_sge_merge
export FSLDIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
source ${FSLDIR}/etc/fslconf/fsl.sh
export MATLAB=/Shared/pinc/sharedopt/apps/matlab/Linux/x86_64/R2022b/bin
export PATH=${MATLAB}:$PATH


sub_name=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid/sublist | head -n+${SGE_TASK_ID} | tail -n-1`
######################

#contrasts to run, identical across all subjects
CONS=/Shared/jianglab/0_scripts/CausalConnectome/Design_Con_Files/colorid_contrasts.m

sub_dir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid/pipeline_prepare/${sub_name}_colorid

st=`date`
echo "begin precess"

# 1. preprocess

# 2. 
SESSDIRS=`find ${sub_dir} -type d -name '*.sess*' | sort `
MATS=`find ${sub_dir} -name '*regressor*' | sort `
MASK=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/mask/MNI152_T1_2mm_brain_mask_tpl

spm_result=${sub_dir}/multi_session.spm/spm_jobs
mkdir -p ${spm_result}

# 3. do model
echo "begin do model"
${ANALYSIS_PIPE_DIR}/multi_session_createSPMjob_kw.sh ${sub_dir}/multi_session.spm spm_model 2 2 ${SESSDIRS} ${MATS} 1 ${MASK}

cd ${spm_result}
matlab -nodesktop -nodisplay -nosplash -r run_spm_model_job

# 4. run contrast
echo "begin do contrast"
readlink -f ${sub_dir} | sed 's/\//\\\//g' >  ${sub_dir}/multi_session.spm/spm_jobs/grot
full_out=`cat ${sub_dir}/multi_session.spm/spm_jobs/grot`
/bin/rm ${sub_dir}/multi_session.spm/spm_jobs/grot

echo FULL OUT $full_out
cat ${CONS}  | sed "s/'<UNDEFINED>'/{'${full_out}\/multi_session.spm\/SPM.mat'}/g" > ${spm_result}/job_contrast.m

# create run
${ANALYSIS_PIPE_DIR}/analysis_pipeline_createSPM_batch_script.sh ${spm_result}/run_job_contrast.m ${spm_result}/job_contrast.m

cd ${spm_result}
matlab -nodesktop -nodisplay -nosplash -r run_job_contrast

echo 'Done Contrast'


cd ${sub_dir}/multi_session.spm
all_img=`ls | grep con_.*\.img`
for img in ${all_img}; do fslchfiletype NIFTI_GZ ${img}; done

et=`date`
echo "start from $st, end to $et"
