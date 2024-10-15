#!/bin/bash

#$ -N fmriprep
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid/logs
#$ -t 1-178:1

OMP_NUM_THREADS=10

subject=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid/sublist | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools
export TEMPLATEFLOW_HOME=${singularityDir}/TemplateFlow
export SINGULARITYENV_TEMPLATEFLOW_HOME=/templateflow
#Run fmriprep
singularity run --cleanenv \
-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/taskfmri_fmriprep/colorid:/data \
-B ${TEMPLATEFLOW_HOME:-$HOME/.cache/templateflow}:/templateflow \
${singularityDir}/fmriprep_v2314_kw.sif \
/data/BIDS/ /data/fmriprep/ participant --participant-label ${subject} \
--skip_bids_validation \
--nprocs 10 --omp-nthreads 10 --mem 32000 \
-w /data/work \
--ignore fieldmaps slicetiming \
--output-spaces MNI152NLin6Asym:res-2 T1w \
--fs-license-file ${singularityDir}/license.txt \
--fs-no-reconall \
--output-layout bids \
--resource-monitor \
--notrack \
--stop-on-first-crash
