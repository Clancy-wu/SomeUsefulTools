#!/bin/sh

##############SETUP ENVIRONMENT###################
SCRATCH=/lab-share/Neuro-Cohen-e2/Public/projects/Stanford_TMS_fMRI
export ANALYSIS_PIPE_DIR=$SCRATCH/scripts/analysis_pipeline_cd
export SPM8DIR=/lab-share/Neuro-Cohen-e2/Public/software/toolbox/spm12/
export BASHDIR=$SCRATCH/scripts/CausalConnectome
######################
TARGETDIR="L_Fp R_Fp L_aMFG R_aMFG L_pMFG R_pMFG R_IFJ R_FEF R_M1 R_preSMA R_IPL "


TMSDIR=$SCRATCH/CausalConnectome/tmsfmri/
STRUCTDIR=$SCRATCH/CausalConnectome/structural/

BRAIN_FUNC_MASK=$SCRATCH/scripts/CausalConnectome/ppi_masks_standard_nii/MNI152_T1_2mm_brain_mask.nii
#contrasts to run, identical across all subjects
CONS=$SCRATCH/scripts/CausalConnectome/Design_Con_Files/tms_pulse_con.m
DESIGN=$SCRATCH/scripts/CausalConnectome/Design_Con_Files/CC_ERtiming_stim.mat
SPM_CON_FILE=`readlink -f $CONS`
DESIGN_FILE=`readlink -f $DESIGN`
MODEL_NAME=tms_with_motion

for t in $TARGETDIR; do

for i in `ls ${TMSDIR}/${t}/CausCon_*HC*.nii.gz`  ; do

s=`basename $i | awk -F _ '{ print $2 }' | sed 's/CausCon//g'`
echo ${s}

OUTPUTDIR=${TMSDIR}/${t}/${s}
if [ ! -d ${OUTPUTDIR} ] ; then
echo no $OUTPUTDIR, please run preprocessing
fi

# head movement
MOTION_FILE="-motion ${TMSDIR}/${t}/${s}/func/rp_CausCon_${s}_*_${t}*.txt"
# spm job
jobdir=${OUTPUTDIR}/${MODEL_NAME}.spm/spm_jobs
if [ ! -d ${jobdir} ]; then
mkdir -p "${jobdir}"
fi
jobname=${jobdir}/job_model.m
# prefiltered data
# funcfile=${OUTPUTDIR}/conn_${s}/results/preprocessing/niftiDATA_Subject001_Condition000
tmpfile=`ls ${OUTPUTDIR}/func/swu*`
funcfile=`echo "${tmpfile%.*}"`
TR=2.4
# contrast file
echo ${OUTPUTDIR}  | sed 's/\//\\\//g' >  ${jobdir}/grot
foutdir=`cat ${jobdir}/grot`
/bin/rm ${jobdir}/grot

cat ${SPM_CON_FILE}  | sed "s/'<UNDEFINED>'/{'${foutdir}\/${MODEL_NAME}.spm\/SPM.mat'}/g" > ${jobdir}/job_contrast.m

${ANALYSIS_PIPE_DIR}/analysis_pipeline_createSPM_batch_script.sh ${jobdir}/run_job_contrast.m ${jobdir}/job_contrast.m
####################################
if [ ! -f ${OUTPUTDIR}/${MODEL_NAME}.spm/con_0001.nii ]; then
count=$(ls ${OUTPUTDIR}/${MODEL_NAME}.spm/ |wc -l)
if [ "$count" != 15 ]; then

echo removing GLM results and reanalyzing
  sbatch --partition=bch-compute,bch-largemem --mem=4G --wrap=" ${ANALYSIS_PIPE_DIR}/analysis_pipeline_SPMmodel.sh -tr $TR -jobname ${jobname} -outdir ${OUTPUTDIR}/${MODEL_NAME}.spm -func_data $funcfile -design $DESIGN_FILE ${MOTION_FILE} -mask ${BRAIN_FUNC_MASK}

cd ${jobdir}

echo \" cd ${jobdir} ; run_job_contrast \" | matlab -nodesktop -nodisplay -nosplash

"

    echo RUNNING TMS on ${t} ${s}
fi
fi
done
done


# ${MOTION_FILE}
# cd ${OUTPUTDIR}/${MODEL_NAME}.spm/
# $BASHDIR/img2nii_fsl.sh *.img
