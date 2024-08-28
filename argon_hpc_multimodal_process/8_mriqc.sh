#!/bin/bash

#$ -N mriqc
#$ -pe smp 1
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep/logs
OMP_NUM_THREADS=20

#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

singularity run --cleanenv \
        -B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/rest_fmriprep:/work_dir \
        ${singularityDir}/mriqc_2024.sif /work_dir/BIDS /work_dir/mriqc participant \
        --n_procs ${OMP_NUM_THREADS} --omp-nthreads ${OMP_NUM_THREADS} --mem_gb 40 \
        -w /work_dir/mriqc_work \
        --resource-monitor \
        --no-sub \
        --notrack

####################################################################################
## if files are too many
ls BIDS | grep sub- > sublist_all
head -n 10 sublist_all > sublist
#!/bin/bash

#$ -N mriqc
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/logs
OMP_NUM_THREADS=30

sublist=`tr '[:space:]' ' ' < /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/sublist`

#Set up dependencies
singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

singularity run --cleanenv \
	-B /Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep:/work_dir \
	${singularityDir}/mriqc_2024.sif /work_dir/BIDS /work_dir/mriqc participant --participant_labels ${sublist} \
	--n_procs ${OMP_NUM_THREADS} --omp-nthreads ${OMP_NUM_THREADS} --mem_gb 60 \
	-w /work_dir/mriqc_work \
	--resource-monitor \
	--no-sub \
	--notrack
