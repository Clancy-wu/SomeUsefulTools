#!/bin/bash

#$ -N mriqc
#$ -pe smp 10
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/logs
OMP_NUM_THREADS=10

#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

singularity run --cleanenv \
	-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep:/work_dir \
	${singularityDir}/mriqc_2024.sif /work_dir/BIDS /work_dir/mriqc group \
	--n_procs ${OMP_NUM_THREADS} --omp-nthreads ${OMP_NUM_THREADS} --mem_gb 20 \
	--resource-monitor \
	--no-sub \
	--notrack
