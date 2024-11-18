#!/bin/bash

#$ -N xcpd_No_parcel
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/logs
#$ -t 1-19:1
OMP_NUM_THREADS=10
subject=`cat /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/re_sublist | head -n+${SGE_TASK_ID} | tail -n-1`
#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools
#Run qsiprep
singularity run --cleanenv \
-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep:/data \
${singularityDir}/xcp_d-v0_7_1rc5_kw.simg \
/data/fmriprep/ /data/rerun_xcpd/ participant --participant-label ${subject} \
--nthreads 10 --omp-nthreads 10 --mem-gb 20 \
--input-type fmriprep \
-p 36P \
--fd-thresh 0.5 \
--min-time 0 \
--smoothing 6 \
--skip-parcellation \
-w /data/xcpd_work \
--skip-dcan-qc \
--fs-license-file ${singularityDir}/license.txt \
--resource-monitor \
--stop-on-first-crash
