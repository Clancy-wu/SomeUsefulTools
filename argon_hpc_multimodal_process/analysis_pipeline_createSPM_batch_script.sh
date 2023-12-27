#!/bin/sh

function Usage(){
    echo "\n analysis_pipeline_createSPM_batch_script.sh <output_scripts> <jobname> \n "
    exit 1 

}

if [ $# -ne 2 ] ; then 
    Usage
fi
    
#Input all jobs file
OUT_SCRIPT=$1;
if [ -f ${OUT_SCRIPT} ] ; then 
	rm ${OUT_SCRIPT}
fi


shift 
echo "addpath '${SPM8DIR}'"				>> ${OUT_SCRIPT}
echo "% List of open inputs"							>> ${OUT_SCRIPT}
echo "nrun = $# ; % enter the number of runs here"		>> ${OUT_SCRIPT}


#assign first job file
echo "jobfile = { '${1}' };"					>> ${OUT_SCRIPT}
shift 

echo "jobs = repmat(jobfile, 1, nrun);"	>> ${OUT_SCRIPT}

count=2;
for job in $@ ; do 
#	dir=`dirname $job`
#	echo "cd '${dir}'"			>> ${OUT_SCRIPT}
	echo "jobs{${count}} = '$job'"			>> ${OUT_SCRIPT}
	let count+=1
done

echo "spm('defaults', 'FMRI');"			>> ${OUT_SCRIPT}
echo "spm_jobman('initcfg'); % SPM8 only ">> ${OUT_SCRIPT}

echo "spm_jobman('serial', jobs);"			>> ${OUT_SCRIPT}
echo "quit" >> ${OUT_SCRIPT}