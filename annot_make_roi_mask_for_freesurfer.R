library(freesurferformats)

## bn atlas
bn_lh_file <- '/home/clancy/Pictures/BN_Atlas_freesurfer/fsaverage/label/lh.BN_Atlas.annot'
bn_lh <- read.fs.annot(bn_lh_file)
# 1
lh_lmfg_vertex <- length(bn_lh$vertices) # prepare
# 2
index_0 <- c('Unknown', 25, 5, 25, 0, 1639705, '#190519', '#19051900', 0)
index_1 <- c('mfg_big_L', 0, 255, 0, 0,  65280, '#00FF00', '#00FF0000', 1)
index_2 <- c('mfg_big_R', 0, 255, 0, 0,  65280, '#00FF00', '#00FF0000', 2)
index_3 <- c('ifg_big_L', 0, 246, 255, 0, 16774656, '#00F6FF', '#00F6FF00', 3)
index_4 <- c('ifg_big_R', 0, 246, 255, 0, 16774656, '#00F6FF', '#00F6FF00', 4)
lh_lmfg_colortable_df <- rbind(index_0, index_1, index_2, index_3, index_4)
lh_lmfg_colortable_df <- as.data.frame(lh_lmfg_colortable_df)
colnames(lh_lmfg_colortable_df) <- colnames(bn_lh$colortable_df) # prepare
# 3
medial_index <- c(0)
mfg_lh_index <- c(15, 17, 19, 21, 23)
mfg_rh_index <- c(16, 18, 20, 22, 24)
ifg_lh_index <- c(29, 31, 33, 35, 37, 39, 51)
ifg_rh_index <- c(30, 32, 34, 36, 38, 40, 52)

assign_value_from_index <- function(input_index, input_annot, assign_code){
  code_100 <- input_annot$colortable_df$code
  vector_100 <- input_annot$colortable_df$struct_index
  vector_10 <- input_index
  code_10 <- sapply(vector_10, function(x) code_100[vector_100==x])
  assign_label_code <- rep(0, length(input_annot$label_codes))
  for (i in code_10){
    assign_label_code[input_annot$label_codes==i] <- assign_code
  }
  return (assign_label_code)
}
# 3
save_medial <- assign_value_from_index(medial_index, bn_lh, 1639705)
save_mfg <- assign_value_from_index(mfg_lh_index, bn_lh, 65280)
save_ifg <- assign_value_from_index(ifg_lh_index, bn_lh, 16774656)
# 3
lh_lmfg_label_codes <- save_medial + save_mfg + save_ifg # prepare
# output
write.fs.annot('big_mfg_ifg_LH.annot', lh_lmfg_vertex, lh_lmfg_colortable_df, lh_lmfg_label_codes)
# end. author@Kang Wu, kangwu@uiowa.edu
