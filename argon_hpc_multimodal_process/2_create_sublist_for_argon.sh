#!/bin/bash
# scrpit to create sublist for 3_optimized_argon_pipeline

cd /home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep
find tmsfmri_pipeline_prepare/ -maxdepth 2 -mindepth 2 -type d > sublist_for_pipeline

# end. author@kangwu