# 0_load_packages ---------------------------------------------------------
library(brainGraph) # compute network properties
# remotes::install_version("igraph", version = "1.6.0")
library(igraph) # 1.6.0
packageVersion("igraph") # 1.6.0
library(data.table) # data.table
library(parallel)
library(doMC)
registerDoMC(30)

options(bg.subject_id='participant_id', bg.group='group')
grps = c('health')
sub_info_file = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/tms_restGraphTheory/subject_info.csv'
sub_info = fread(sub_info_file)
output_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/tms_restGraphTheory/'
# 1_network_construction --------------------------------------------------
brain_274_dir = '/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/tms_restGraphTheory/brain_274'
## Network contains positive & negative & absolute
densities <- seq(0.10, 0.34, 0.01)
ba_274 <- fread('/home/kangwu/LSS/jianglab/3_Data_Working/fmriprep_processed_wk/tmsfmri_fmriprep/analysis_result/tms_restGraphTheory/ba_274_info.csv')
as_atlas(ba_274)
## --------------------------------------------------------------------------
save2dataframe <- function(data, file_path_suffix){
  vertex_df <- rbindlist(lapply(data, vertex_attr_dt))
  graph_df <- rbindlist(lapply(data, graph_attr_dt))
  fwrite(vertex_df, paste0(file_path_suffix, '_vertex.csv'), sep=',', col.names=TRUE)
  fwrite(graph_df, paste0(file_path_suffix, '_graph.csv'), sep=',', col.names=TRUE)
}
#### functional network graph weighted subject level
## raw
inds = lapply(grps, function(x) sub_info[group == x, which = TRUE])
matfiles <- paste0(brain_274_dir,'/', sub_info$participant_id, '/PearCorZ_', sub_info$participant_id, '.txt')
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = densities, inds = inds)
# check the minimun value of raw matrix
for (i in seq_along(densities)){
  Min = min(my.mats$A.norm.sub[[i]])
  print(i)
  print(Min)
}
# if values are all higher than 0, then the raw matrix could be used.
              
gw.sub <- vector('list', length(densities))
gw.group <- vector('list', length(densities))
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], 'ba_274', level='subject',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE, gnames = sub_info$participant_id,
                                     grpNames = NULL )
  gw.group[[i]] <- make_brainGraphList(my.mats$A.norm.mean[[i]], 'ba_274', level='group',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE,  grpNames = NULL )  
}
saveRDS(gw.sub, file=file.path(output_dir, 'rsfmri_subject_raw_brain274.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path(output_dir, 'rsfmri_subject_raw_brain274'))

saveRDS(gw.group, file=file.path(output_dir, 'rsfmri_group_raw_brain274.rds'), compress = 'xz')
save2dataframe(gw.group, file=file.path(output_dir, 'rsfmri_group_raw_brain274'))

## cell report
single_density = 0.25
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = single_density, inds = inds)
gw.sub <- make_brainGraphList(my.mats$A.norm.sub[[1]], 'ba_274', level='subject',
                                   modality = 'fmri',threshold = single_density,
                                   weighted = TRUE, gnames = sub_info$participant_id,
                                   grpNames = NULL )
gw.group <- make_brainGraphList(my.mats$A.norm.mean[[1]], 'ba_274', level='group',
                                     modality = 'fmri',threshold = single_density,
                                     weighted = TRUE,  grpNames = NULL ) 

saveRDS(gw.sub, file=file.path(output_dir, 'rsfmri_subject_CellReport_brain274.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path(output_dir, 'rsfmri_subject_CellReport_brain274'))

saveRDS(gw.group, file=file.path(output_dir, 'rsfmri_group_CellReport_brain274.rds'), compress = 'xz')
save2dataframe(gw.group, file=file.path(output_dir, 'rsfmri_group_CellReport_brain274'))
print('finished.')
# end. kangwu
