#!/bin/bash
for_each -nthreads 10 BIDS/sub-* : docker run -ti --rm \
    -v /home/clancy/ssd/SleepDisfunction:/work \
    -u $(id -u):$(id -g) \
    -v /home/clancy/TemplateFlow:/opt/templateflow \
    -e TEMPLATEFLOW_HOME=/opt/templateflow \
    nipreps/fmriprep:24.1.1 \
    /work/BIDS/ /work/fmriprep/ participant --participant-label PRE \
	--skip_bids_validation \
	--ignore fieldmaps \
	-w /work/fmriprep_work \
	--nthreads 1 --omp-nthreads 1 \
	--output-spaces MNI152NLin2009cAsym:res-2 \
	--bold2t1w-dof 12 --force-bbr \
	--skull-strip-t1w force \
	--fs-license-file /work/license.txt \
	--output-layout bids \
	--cifti-output 91k \
	--resource-monitor \
	--notrack \
	--stop-on-first-crash

