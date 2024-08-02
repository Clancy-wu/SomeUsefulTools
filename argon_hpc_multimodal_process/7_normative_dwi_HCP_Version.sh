#!/bin/bash

#$ -N hcp1065_track
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/structure_project_wk/logs
#$ -t 1-1065:1
OMP_NUM_THREADS=10

singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools

sub_name=`cat /Shared/jianglab/3_Data_Working/HCP1065/sublist | head -n+${SGE_TASK_ID} | tail -n-1`

hcp1065_prepare_dir=/Shared/jianglab/3_Data_Working/HCP1065
output_dir=/Shared/jianglab/3_Data_Working/structure_project_wk/ndp_wk

FSL_DIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5 # for mni normalize
########################################################################
## main run

if [ ! -d ${output_dir} ]; then mkdir ${output_dir}; fi

output_mni=${output_dir}/space_mni    # save mni space tck
output_t1=${output_dir}/space_t1    # save native space tck
if [ ! -d ${output_mni} ]; then mkdir ${output_mni}; fi
if [ ! -d ${output_t1} ]; then mkdir ${output_t1}; fi

# mask should be MNI152NLin6Asym space, but LAS and 1mm resolution
ROI1_mni=/Shared/jianglab/3_Data_Working/structure_project_wk/Big_DLPFC_LH_FSL.nii.gz
ROI2_mni=/Shared/jianglab/3_Data_Working/structure_project_wk/Amyg_First_LH_FSL.nii.gz

#### main run

# make dir 
sub_data_dir=${hcp1065_prepare_dir}/${sub_name}
sub_temp_dir=${output_dir}/${sub_name}
mkdir ${sub_temp_dir}

cd ${sub_temp_dir}

# roi prepare
ln -s ${sub_data_dir}/${sub_name}_desc-preproc_T1w.nii.gz t1.nii.gz
ln -s ${sub_data_dir}/${sub_name}_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.mat mni2t1.mat
ln -s ${ROI1_mni} ROI1_mni.nii.gz
ln -s ${ROI2_mni} ROI2_mni.nii.gz

singularity exec ${singularityDir}/ants.sif /bin/bash -c " \
	
	antsApplyTransforms -d 3 -i ROI1_mni.nii.gz -r t1.nii.gz -o ROI1_native.nii.gz -t mni2t1.mat  -n NearestNeighbor &&
	antsApplyTransforms -d 3 -i ROI2_mni.nii.gz -r t1.nii.gz -o ROI2_native.nii.gz -t mni2t1.mat  -n NearestNeighbor
"


# tracking
echo begin run `date`

st=`date`
singularity exec ${singularityDir}/mrtrix3.sif /bin/bash -c " \

	mrconvert ${sub_data_dir}/${sub_name}_space-T1w_desc-preproc_desc-wmFODmtnormed_msmtcsd.mif.gz dwi.mif &&
	mrconvert ROI1_native.nii.gz ROI1_native.mif &&
	mrconvert ROI2_native.nii.gz ROI2_native.mif &&
	
    tckgen dwi.mif ROI1_2.tck \
        -algorithm iFOD2 \
        -maxlength 200 \
        -minlength 30 \
        -cutoff 0.06 \
        -samples 4 \
        -power 0.33 \
        -seed_image ROI1_native.mif \
        -seeds 1000000 \
        -seed_unidirectional \
        -include ROI2_native.mif \
        -stop \
        -nthreads ${OMP_NUM_THREADS} &&

    tckgen dwi.mif ROI2_1.tck \
        -algorithm iFOD2 \
        -maxlength 200 \
        -minlength 30 \
        -cutoff 0.06 \
        -samples 4 \
        -power 0.33 \
        -seed_image ROI2_native.mif \
        -seeds 1000000 \
        -seed_unidirectional \
        -include ROI1_native.mif \
        -stop \
        -nthreads ${OMP_NUM_THREADS} &&

    tckedit ROI1_2.tck ROI2_1.tck ROIs_space-T1w.tck &&

    warpinit ${FSL_DIR}/data/standard/MNI152_T1_1mm_brain.nii.gz inv_identity_warp[].nii
"

echo begin native2mni `date`

# native to mni
singularity exec ${singularityDir}/ants.sif /bin/bash -c " \
	antsApplyTransforms -d 3 -e 0 -i inv_identity_warp0.nii -o inv_mrtrix_warp0.nii -r t1.nii.gz -t mni2t1.mat --default-value 2147483647 &&
	antsApplyTransforms -d 3 -e 0 -i inv_identity_warp1.nii -o inv_mrtrix_warp1.nii -r t1.nii.gz -t mni2t1.mat --default-value 2147483647 &&
	antsApplyTransforms -d 3 -e 0 -i inv_identity_warp2.nii -o inv_mrtrix_warp2.nii -r t1.nii.gz -t mni2t1.mat --default-value 2147483647
"

singularity exec ${singularityDir}/mrtrix3.sif /bin/bash -c " \
	warpcorrect inv_mrtrix_warp[].nii inv_mrtrix_warp_corrected.mif -marker 2147483647 &&
	tcktransform ROIs_space-T1w.tck inv_mrtrix_warp_corrected.mif ROIs_space-MNI152NLin6Asym.tck &&
	mv ROIs_space-T1w.tck ${output_t1}/${sub_name}_ROIs_space-T1w.tck &&	
	mv ROIs_space-MNI152NLin6Asym.tck ${output_mni}/${sub_name}_ROIs_space-MNI152NLin6Asym.tck
"
rm -r ${sub_temp_dir}

et=`date`

echo start from ${st} and end at ${et}
echo author Kang Wu
