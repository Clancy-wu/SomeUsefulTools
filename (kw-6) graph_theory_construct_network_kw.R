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
grps = c('health', 'patient')
# 1_network_construction --------------------------------------------------

## Network contains positive & negative & absolute
densities <- seq(0.10, 0.34, 0.01)
atlas = 'brainnetome'
## --------------------------------------------------------------------------
save2dataframe <- function(data, file_path_suffix){
  vertex_df <- rbindlist(lapply(data, vertex_attr_dt))
  graph_df <- rbindlist(lapply(data, graph_attr_dt))
  fwrite(vertex_df, paste0(file_path_suffix, '_vertex.csv'), sep=',', col.names=TRUE)
  fwrite(graph_df, paste0(file_path_suffix, '_graph.csv'), sep=',', col.names=TRUE)
}
#### CFS: functional network graph weighted subject level
covars.all <- fread('ClinicalMeasurements/CFS_subinfo.csv') # subs=79
inds = lapply(grps, function(x) covars.all[group == x, which = TRUE]) # 1=health=39, 2=patient=40
matfiles <- paste0('NetResults/CFS/', covars.all$participant_id, '/pos_func_', covars.all$participant_id, '.txt') 
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = densities, inds = inds)
gw.sub <- vector('list', length(densities)) # ws: weighted subject
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], atlas, level='subject',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE, gnames = covars.all$participant_id,
                                     grpNames = covars.all$group )
}
saveRDS(gw.sub, file=file.path('BrainGraphRDS/', 'CFS_func_weighted_subject_pos.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path('BrainGraphRDS/', 'CFS_func_weighted_subject_pos'))

#### CFS: fiber network graph weighted subject level
matfiles <- paste0('NetResults/CFS/', covars.all$participant_id, '/pos_fiber_', covars.all$participant_id, '.txt') 
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = densities, inds = inds)
gw.sub <- vector('list', length(densities)) # ws: weighted subject
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], atlas, level='subject',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE, gnames = covars.all$participant_id,
                                     grpNames = covars.all$group )
}
saveRDS(gw.sub, file=file.path('BrainGraphRDS/', 'CFS_fiber_weighted_subject_pos.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path('BrainGraphRDS/', 'CFS_fiber_weighted_subject_pos'))

## --------------------------------------------------------------------------
#### ISYB: functional network graph weighted subject level
covars.all <- fread('ClinicalMeasurements/ISYB_subinfo.csv') # subs=215
inds = lapply(grps, function(x) covars.all[group == x, which = TRUE]) # 1=health=215, 2=patient=0
matfiles <- paste0('NetResults/ISYB/', covars.all$participant_id, '/pos_func_', covars.all$participant_id, '.txt') 
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = densities, inds = inds)
gw.sub <- vector('list', length(densities)) # ws: weighted subject
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], atlas, level='subject',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE, gnames = covars.all$participant_id,
                                     grpNames = covars.all$group )
}
saveRDS(gw.sub, file=file.path('BrainGraphRDS/', 'ISYB_func_weighted_subject_pos.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path('BrainGraphRDS/', 'ISYB_func_weighted_subject_pos'))

#### ISYB: fiber network graph weighted subject level
matfiles <- paste0('NetResults/ISYB/', covars.all$participant_id, '/pos_fiber_', covars.all$participant_id, '.txt')
my.mats <- create_mats(matfiles, modality = 'fmri',threshold.by = 'density',
                       mat.thresh = densities, inds = inds)
gw.sub <- vector('list', length(densities)) # ws: weighted subject
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], atlas, level='subject',
                                     modality = 'fmri',threshold = densities[i],
                                     weighted = TRUE, gnames = covars.all$participant_id,
                                     grpNames = covars.all$group )
}
saveRDS(gw.sub, file=file.path('BrainGraphRDS/', 'ISYB_fiber_weighted_subject_pos.rds'), compress = 'xz')
save2dataframe(gw.sub, file=file.path('BrainGraphRDS/', 'ISYB_fiber_weighted_subject_pos'))

print('finished all')
########## end. author@kangwu

# use self atlas
my_atlas <- fread('ba_274_info.csv')
as_atlas(my_atlas)
for (i in seq_along(densities)){
  gw.sub[[i]] <- make_brainGraphList(my.mats$A.norm.sub[[i]], 'my_atlas', level='subject',
                                     modality = 'fmri', threshold = densities[i],
                                     weighted = TRUE, gnames = sub_info$participant_id,
                                     grpNames = sub_info$group )
}

##### check degree threshold values for func
              
matfiles <- Sys.glob('NetResults_invnodal/ISYB/*/raw_func_*_invnodal.txt')
for (i in matfiles){
  All_value = fread(i, header = F) %>%
    as.matrix(.) %>%
    get_thresholds(., densities)
  tail(All_value, 1)
  output = paste(i, tail(All_value, 1))
  print(output)
}





  
