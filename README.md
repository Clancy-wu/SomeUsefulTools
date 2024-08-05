This is for self use.
There are some usefule code tools to make file sort for further data processing.
group_bar is much useful.

Subregion_seg.py: a script for amygdala segment provided by fsl (v6.0.5.2) and freesurfer (v7.4.1)
segment_comapre.R: plot amygdala comparison between segments of fsl and freesurfer.

stroke example (Dec 6 2023)
two examples of stroke data have been uploaded. This example introduces general check method from original DICOM to fmriprep.
Check steps cotain 4 portion: 
 1. transfer DICOM to nii.gz and json profile via dcm2niix.
 2. sort the data to bids format, including DWI, Fun, T1 and T2 (I haven't fieldmap).
 3. check TR of each modal data, make sure TR is consistance of nii.gz and json. I have found that dcm2niix would occur error TR.
 3-1 !!! Its should be reminded that always check your TR. fmriprep processes data trhough json file to acquire TR while FSL acquires from nii.gz.
 4. run 3_checkTR, if 'TR not match and need fix.csv' outputs, it should check csv immediately and unites TR referring to nii.gz or json.
 5. if you want to unit TR, run 4_fixTR.
 6. all things are prepared for 'fmriprep_run.txt' in docker.

Freesurfer longitudinal analysis (Dec 13 2023)
 1. recon-all
 2. recon-all -base
 3. recon-all -longitudinal
