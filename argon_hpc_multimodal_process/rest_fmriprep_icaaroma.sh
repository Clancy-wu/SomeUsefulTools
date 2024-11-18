#!/bin/bash

#$ -N ica
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/logs
#$ -t 1-199:1
OMP_NUM_THREADS=10
subject=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/sublist | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools
#Run qsiprep
singularity run --cleanenv \
-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep:/data \
${singularityDir}/fmripost-aroma_main.sif \
/data/BIDS/ /data/fmriprep_icaaroma/ participant --participant-label ${subject} \
--nthreads 10 --omp-nthreads 10 --mem-mb 32000 \
--skip_bids_validation \
-d /data/fmriprep \
--ignore fieldmaps slicetiming \
-w /data/xcpd_work \
--resource-monitor \
--notrack \
--stop-on-first-crash
