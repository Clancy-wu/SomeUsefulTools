#!/bin/sh 
#
#!/bin/sh
#input 1: JObdirectory
#input 2: jobname 
#input 3: Output directory, needs to be full path
#input 4...: Images to run on =

###################################################################################################################
#######################HERE ARE THE FUNCTIONS USED BY THIS SCRIPT#####################################
###################################################################################################################
Usage() {
echo ""
echo "Usage:   analysis_pipeline_SPMsmooth_SPMmodel.sh  -func_data image.nii.gz -jobname <job_basename> -outdir <output_direcotry> image_files..."
echo ""
echo "-jobname : basename for job file names"
echo "-outdir   : parent directory for output data (USE FULL PATH)"
echo "-func_data : 4D functional data to run SPM models on "
echo "-func_data_3D <text_file> : 4D functional data as a series of 3D images to run SPM models on "
echo "-design : Design Files "
echo "-motion : Motion file "
echo "-mask : Mask File"
echo ""
echo ""
exit 1
}

#######################################   Create SPM job file    ########################################
#input 1 : design file
#input 2 : contrast file

function func_createSPM_JobFile_model {
#echo "Entering function to create Job file"
MOTION_PARAMS=""


#set input as variables
DESIGN=$1
shift 
TR=$1
shift
JOBFILE=$1
shift
SPMDIR=$1 #where to put everything
shift
if [ ! $1 = 0 ] ; then
    MOTION_PARAMS=$1
fi
shift


#if another file is there assume it is a mask
MASK=""
if [ ! $1 = 0 ]; then 
    MASK=$1
    shift
fi

#echo MASK $MASK
#remove job file if it exists
if [ -f $JOBFILE ] ; then 
    rm $JOBFILE
fi

USE_DERIV=$1
echo "use deriv $USE_DERIV"
echo $@
shift


#create SPM job file using simple echo commands
#MODEL SMOOTHING 
BATCH_IND=1

echo "%%"																		>> ${JOBFILE}

    ######model specification
    #SPMDIR is output directory for spm results
  
    #**********src_exbranch******needs to eb incremented appropriately
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.dir = {'${SPMDIR}'};"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.timing.units = 'secs';"				>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.timing.RT = ${TR};"						>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.timing.fmri_t = 16;"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.timing.fmri_t0 = 1;"					>> ${JOBFILE}

#input data here 
#make sure there's at least time point
image=`imglob -extension $1`
    NSCANS=`${FSLDIR}/bin/fslnvols $image`
    if [ $# -gt 0 ] ;then 
        echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.scans = {">> ${JOBFILE}
        time=1
        while [ $time -le $NSCANS ]; do
            echo "'${image},${time}'"                           >> ${JOBFILE}
            let time+=1
        done
        echo "};"                           >> ${JOBFILE}
#    for image in $@ ; do
# echo $image

#echo "'${image},1'"                           >> ${JOBFILE}
#       done
#       echo "};"                           >> ${JOBFILE}
    fi


    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.cond = struct('name', {}, 'onset', {}, 'duration', {}, 'tmod', {}, 'pmod', {});"						>> ${JOBFILE}
    #design file
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.multi = {'${DESIGN}'};" 			>> ${JOBFILE}
    #add motion parameters if specified
if [ ! "_${MOTION_PARAMS}" = _ ] ; then 
  
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.multi_reg = {'${MOTION_PARAMS}'};"			>> ${JOBFILE}
fi
#   else 
#   echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.multi_reg = {''};"			>> ${JOBFILE}
#   fi
#echo MASK $MASK
if [ "_$MASK" = "_" ] ; then 
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.mask = {''};"               >> ${JOBFILE}
else
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.mask = {'${MASK},1'};"               >> ${JOBFILE}
fi

    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.regress = struct('name', {}, 'val', {});"		>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.sess.hpf = 128;"									>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.fact = struct('name', {}, 'levels', {});"			>> ${JOBFILE}	
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.bases.hrf.derivs = [${USE_DERIV} 0];"							>> ${JOBFILE}	
	
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.volt = 1;"											>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.global = 'None';"									>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_spec.cvi = 'AR(1)';"									>> ${JOBFILE}

    #######model estimation bit 
    #increment batch index

    let BATCH_IND+=1
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1) = cfg_dep;"                               >> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).tname = 'Select SPM.mat';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(1).name = 'filter';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(1).value = 'mat';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(2).name = 'strtype';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).tgt_spec{1}(2).value = 'e';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).sname = 'fMRI model specification: SPM.mat File';"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).src_exbranch = substruct('.','val', '{}',{1}, '.','val', '{}',{1}, '.','val', '{}',{1});"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.spmmat(1).src_output = substruct('.','spmmat');"					>> ${JOBFILE}
    echo "matlabbatch{${BATCH_IND}}.spm.stats.fmri_est.method.Classical = 1;"								>> ${JOBFILE}

}



###################################################################################################################
##############################END OF FUNCTIONS ############################################
###################################################################################################################







#all input options need to start with "-"

#These variables store IO options
jobname=""
OUTPUTDIR=""
MASK_FILE=""
MOTION_FILE=0
TR=0
VERBOSE=0
USE_DERIV=0
#this variable tells whther data is input as a series of 3D files
#USE_FUNC_DATA_3D=0
while [ _${1:0:1} = _- ] ; do 
#echo $1
	if [ ${1} = -jobname ] ; then
		jobname=`readlink -f $2`
		shift 2

	elif [ ${1} = -outdir ] ; then 
		OUTPUTDIR=$2
		shift 2

    elif [ ${1} = -func_data ] ; then 
        FUNC_DATA=`readlink -f $2`
        
        if [ `${FSLDIR}/bin/imtest $FUNC_DATA` = 1 ] ; then 
#           echo "...Assuming $FUNC_DATA is a 4D times series"
            FUNC_DATA=`remove_ext $FUNC_DATA`

#   else
#  echo "...Assuming $FUNC_DATA is a list of 3D files"
#   USE_FUNC_DATA_3D=1
        fi
        shift 2
    elif [ ${1} = -design ] ; then 
        DESIGN_FILE=$2
        shift 2
	elif [ ${1} = -tr ] ; then 
        TR=$2
        shift 2
    
    elif [ ${1} = -motion ] ; then 
        MOTION_FILE=$2
        shift 2
elif [ ${1} = -v ] ; then
    VERBOSE=$2
    shift 2

    elif [ ${1} = -mask ] ; then
        MASK_FILE=$2
        shift 2
#        echo "...functional mask : ${MASK_FILE}"
elif [ ${1} = -temp_deriv ] ; then
    
    USE_DERIV=$2
    shift 2
#        echo "...functional mask : ${MASK_FILE}"

	else
		echo "Unrecognized option: ${1}"
		exit 1
	fi
done

#echo "process functional data ${FUNC_DATA}"

#create job file

        #append .spm for for spm process data
# OUTPUTDIR=${FUNC_DATA}.spm
if [ ! -d $OUTPUTDIR ] ; then 
    mkdir $OUTPUTDIR
fi



#BEFORE MOVING FORWARD LETS MAKE SURE EBERYTHING EXISTS
if [ "_$DESIGN_FILE" = "_" ] ; then 
    echo "Missing design file, it has not been set. "
    exit 1
fi
if [ ! -f $DESIGN_FILE ] ; then 
    echo "Missing design file, it does not exist. "
    exit 1
fi

if [  ! $MOTION_FILE = 0 ] ; then 
    if [ ! -f $MOTION_FILE ] ; then 
        echo "Missing motion file. ${MOTION_FILE}"
        exit 1
    fi
fi

if [ "_${jobname}" = _ ] ; then 
    echo "Jobname cannot be blank. "
    exit 1
fi

######DONE CHECKS

    IMS_TO_CLEANUP=""
    #Finally, let's do some processing
        
#if [ $USE_FUNC_DATA_3D = 0 ] ; then

        export FSLOUTPUTTYPE=NIFTI
        #remove any prevous existing images
        FUNC_DIR=`dirname $FUNC_DATA`


#       existing_ims=`imglob ${FUNC_DIR}/fmri_grot*`
#       Nims=`echo $existing_ims | wc | awk '{ print $2 }'`
#        if [ $Nims -gt 0 ] ; then
#if [ $VERBOSE = 1 ] ; then
#          echo "Removing existing files 3D files"
#fi
#           ${FSLDIR}/bin/imrm $existing_ims
#       fi

#if [ 0 = 1 ] ; then
#break up 4D file for spm processing
#if [ $VERBOSE = 1 ] ; then
#       echo "Splitting 4D NIFTI for SPM processing"
#fi
#    fslsplit $FUNC_DATA ${FUNC_DIR}/sfmri_grot
        #need to include extension to process with spm
#       FUNC_DATA_3D=`imglob -extensions ${FUNC_DIR}/sfmri_grot*`
#       FUNC_DATA_3D=`imglob -extensions ${OUTPUTDIR}/sfmri_grot*`

        #Keeping track of stuff to clean as I go 
#        IMS_TO_CLEANUP="${IMS_TO_CLEANUP} ${FUNC_DATA_3D}"
#        echo "images that i will need to clean "
    # echo $IMS_TO_CLEANUP

#    else
#if [ $VERBOSE = 1 ] ; then
#        echo "Checking 3D images..."
#fi
#       FUNC_DATA_3D=`cat $FUNC_DATA`
#       for i in $FUNC_DATA_3D ; do
#       if [ `${FSLDIR}/bin/imtest $i` = 0 ] ; then
#           echo ""
#           echo "$i is not a valid image"
#           echo ""
#           exit 1
#       fi
#       done
#   fi
#fi

#   echo "Create model job file "
    #remove existing spm.mat if it exists 
    if [ -f ${OUTPUTDIR}/SPM.mat ] ; then 
        /bin/rm ${OUTPUTDIR}/SPM.mat
    fi



if [ $VERBOSE = 1 ] ; then
    echo "...Using design file : $DESIGN_FILE"
    echo "...Using motion parameters : $MOTION_FILE"
    echo "...Using functional mask : $MASK_FILE"
echo "...Using Temporal Derivative : $USE_DERIV"

fi

func_createSPM_JobFile_model $DESIGN_FILE $TR ${jobname} $OUTPUTDIR $MOTION_FILE $MASK_FILE $USE_DERIV $FUNC_DATA 
#   func_createSPM_JobFile_model $DESIGN_FILE $TR ${jobname} $OUTPUTDIR $MOTION_FILE $MASK_FILE $FUNC_DATA_3D
if [ $VERBOSE = 1 ] ; then
    echo "...Job file created : $jobname"
fi

if [ $VERBOSE = 1 ] ; then
echo "Using functional mask: $MASK"
fi 
    #create run script and call with matlab
    dirj=`dirname $jobname` 
    fj=`basename $jobname`
    fj_run=${dirj}/run_${fj}
    ${ANALYSIS_PIPE_DIR}/analysis_pipeline_createSPM_batch_script.sh ${fj_run} $jobname

    #--run the matlab script
    CURDIR=`pwd`
    cd $dirj
    fj=`basename ${fj} .m`
    echo "cd ${dirj}; run_${fj}" | matlab -nodesktop -nojvm -nosplash -nodisplay
    cd $CURDIR


#remove 3D files, does not matter if from 3D split, 4D file
#4D files remains
# ${FSLDIR}/bin/imrm ${FUNC_DATA_3D}
#don tin case doing PPI, do at higher level












