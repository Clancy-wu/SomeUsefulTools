#!/bin/sh

#########
tmssites="R_pMFG L_pMFG R_aMFG L_aMFG R_Fp L_Fp  R_IFJ R_M1 R_preSMA R_IPL R_FEF"
groups="TEHC NTHC NTS TIS"
model="tms_with_tr21_motion"
contrasts="1"
analysisdir=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/TR21_group_con_data/
TASKDIR=/Shared/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/tmsfmri_pipeline_prepare/

# create analysis and group dir
if [ ! -d ${analysisdir} ]; then
	mkdir ${analysisdir}
fi

for t in ${tmssites}; do
	for g in ${groups}; do
		mkdir -p ${analysisdir}/${t}/${g}
	done
done

# copy con_0001.nii to anylysisdir
for t in ${tmssites}; do
	for j in ${contrasts}; do
		subs=`ls ${TASKDIR}/${t}`
		for s in ${subs}; do
			# t: tms site, j: 1, s: sub
			cp ${TASKDIR}/${t}/${s}/${model}.spm/con_000${j}.nii.gz ${analysisdir}/${t}/${s}_tms_${t}_con_000${j}.nii.gz
		done
	done
done

# organized con_0001.nii in analysisdir
## 1: NTHC
## 2: TEHC
## 3: NTS
## 4: TIS
for t in ${tmssites}; do
	mv ${analysisdir}/${t}/sub-1*.nii.gz ${analysisdir}/${t}/NTHC/
	mv ${analysisdir}/${t}/sub-2*.nii.gz ${analysisdir}/${t}/TEHC/
	mv ${analysisdir}/${t}/sub-3*.nii.gz ${analysisdir}/${t}/NTS/
	mv ${analysisdir}/${t}/sub-4*.nii.gz ${analysisdir}/${t}/TIS/
done

#### end. Jan 13 2024
