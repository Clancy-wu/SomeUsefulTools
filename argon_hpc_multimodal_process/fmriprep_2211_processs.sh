#!/bin/bash

#$ -N sub_erp
#$ -pe smp 1
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/sgacc/logs

OMP_NUM_THREADS=10

subject='sub-518'

#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

export TEMPLATEFLOW_HOME=${singularityDir}/TemplateFlow
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow

##########

#Run fmriprep
singularity run --cleanenv \
-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/sgacc:/work_dir \
-B ${TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/templateflow \
${singularityDir}/fmriprep_v22_1_1.simg \
/work_dir/BIDS/ /work_dir/fmriprep/ participant --participant-label ${subject} \
--fs-license-file ${singularityDir}/license.txt \
--fs-no-reconall \
--skip_bids_validation \
--ignore fieldmaps \
--output-space MNI152NLin6Asym:res-2 \
--output-layout bids \
--nprocs ${OMP_NUM_THREADS} --omp-nthreads ${OMP_NUM_THREADS} --mem 32000 \
-w /work_dir/work \
--resource-monitor \
--notrack \
--stop-on-first-crash
