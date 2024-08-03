#!/bin/bash

#$ -N hcp1065_dwi_process
#$ -pe smp 30
#$ -q PINC,CCOM,UI
#$ -j y
#$ -o /Shared/jianglab/3_Data_Working/structure_project_wk/logs
#$ -t 1-1065:1
OMP_NUM_THREADS=5

singularityDir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/fmriprep_tools
export FSL_DIR=/Shared/pinc/sharedopt/apps/fsl/Linux/x86_64/6.0.6.5
source ${FSL_DIR}/etc/fslconf/fsl.sh

sub_name=`cat /Shared/jianglab/3_Data_Working/structure_project_wk/sublist | head -n+${SGE_TASK_ID} | tail -n-1`

hcp1065_dir=/Shared/jianglab/3_Data_Working/structure_project_wk/Diffusion_preproc
output_dir=/Shared/jianglab/3_Data_Working/structure_project_wk/HCP1065

#### main run

# make dir
sub_out_dir=${output_dir}/sub-${sub_name}
sub_out_temp=${sub_out_dir}/temp
mkdir -p ${sub_out_temp}

## prepare files
sub_dir=${hcp1065_dir}/${sub_name}/T1w
sub_anat=${sub_dir}/T1w_acpc_dc_restore_1.25.nii.gz
sub_bvec=${sub_dir}/Diffusion/bvecs
sub_bvals=${sub_dir}/Diffusion/bvals
sub_dwi=${sub_dir}/Diffusion/data.nii.gz
sub_mask=${sub_dir}/Diffusion/nodif_brain_mask.nii.gz

## run output
#### 1. anat process
sub_anat_prepare=${sub_out_dir}/sub-${sub_name}_desc-preproc_T1w.nii.gz

${FSL_DIR}/bin/fslmaths ${sub_anat} -mul ${sub_mask} ${sub_anat_prepare}

#### 1.1 register
fsl_template=${FSL_DIR}/data/standard/MNI152_T1_1mm_brain.nii.gz    # LAS
cd ${sub_out_temp}
ln -s ${fsl_template} mni_T1w.nii.gz    # LAS
ln -s ${sub_anat_prepare} native_T1w.nii.gz    # LAS
singularity exec ${singularityDir}/ants.sif antsRegistrationSyNQuick.sh -d 3 -m mni_T1w.nii.gz -f native_T1w.nii.gz -o mni2native
# Total elapsed time: 70.01, finished
mv ${sub_out_temp}/mni2native0GenericAffine.mat ${sub_out_dir}/sub-${sub_name}_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.mat

#### 2. dwi process
# &&: only run after previous success.
# ; : run no matter previous success.

singularity exec ${singularityDir}/mrtrix3.sif /bin/bash -c " \

mrconvert ${sub_dwi} dwi.mif -fslgrad ${sub_bvec} ${sub_bvals} -datatype float32 -strides 0,0,0,1 && \
dwi2mask dwi.mif dwi_mask.mif && \
dwi2response dhollander dwi.mif dwi_wm.txt dwi_gm.txt dwi_csf.txt -mask dwi_mask.mif -nthreads ${OMP_NUM_THREADS} && \
dwi2fod msmt_csd dwi.mif dwi_wm.txt dwi_wm.mif dwi_gm.txt dwi_gm.mif dwi_csf.txt dwi_csf.mif -mask dwi_mask.mif -nthreads ${OMP_NUM_THREADS} && \
mtnormalise dwi_wm.mif dwi_wm_mtnorm.mif dwi_gm.mif dwi_gm_mtnorm.mif dwi_csf.mif dwi_cfs_mtnorm.mif -mask dwi_mask.mif -nthreads ${OMP_NUM_THREADS} && \
mrconvert dwi_wm_mtnorm.mif dwi_wm_mtnorm.mif.gz && \
mv ${sub_out_temp}/dwi_wm_mtnorm.mif.gz ${sub_out_dir}/sub-${sub_name}_space-T1w_desc-preproc_desc-wmFODmtnormed_msmtcsd.mif.gz && \
rm -r ${sub_out_temp}

"

echo finished successfully. Author@kangwu

# end. author@kangwu