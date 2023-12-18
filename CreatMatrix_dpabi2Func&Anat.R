################################
library(gifti)
library(freesurferformats)
###############################
data <- 'AnatSurfWThickness/'
FileName <- list.files(data)
FileAll <- lapply(FileName, function(x)
                         strsplit(x, '_')[[1]][1])
Files <- unique(unlist(FileAll))
for (i in Files) dir.create(i)

GiiFiles <- list.files(data, pattern = '.gii', full.names = T)
for (i in GiiFiles){
  Files = unlist(strsplit(i, '//'))
  Mid = strsplit(Files[2], '_')[[1]][1]
  New = vector(); New[1] = Files[1]; New[2] = Mid; New[3] = Files[2]
  NewFile = paste(New, collapse = '//')
  file.rename(i, NewFile)
}

#############################################################################
Input.path <- 'FunSurfWIglobalCF/'; Output.path <- 'NetFun/'
Template.l5.annot <- 'fsaverage5/label/lh.aparc.a2009s.annot'
Template.r5.annot <- 'fsaverage5/label/rh.aparc.a2009s.annot'
Template.l5 <- read.fs.annot(Template.l5.annot)
Template.r5 <- read.fs.annot(Template.r5.annot)
Subs <- list.dirs(Input.path, full.names = F, recursive = F)

RoiList.l.all <- Template.l5$colortable_df$struct_name
# x[! x %in% c('A', 'D', 'E')]
RoiList.l <- RoiList.l.all[! RoiList.l.all %in% c('Unknown', 'Medial_wall')]
RoiList.r.all <- Template.r5$colortable_df$struct_name
RoiList.r <- RoiList.r.all[! RoiList.r.all %in% c('Unknown', 'Medial_wall')]
RoiOderKey <- data.frame(
  Index = seq(1,148),
  Hemi = c(rep('LH', 74), rep('RH', 74)),
  RoiName = c(RoiList.l, RoiList.r)
)
write.csv(RoiOderKey, 'ROI_CenterOfMass.csv')

#############################################################################
## function prepare
for (i in Subs){
  # files
  Func.l.file = list.files(file.path(Input.path, i), pattern = 'L', full.names = T)
  Func.r.file = list.files(file.path(Input.path, i), pattern = 'R', full.names = T)
  Func.l = readgii(Func.l.file); Func.l = as.data.frame(Func.l$data)
  Func.r = readgii(Func.r.file); Func.r = as.data.frame(Func.r$data)
  TimeSeries <- dim(Func.l)[2]
  df.r <- df.l <- matrix(NA, nrow = TimeSeries, ncol = length(RoiList.l))
  # LH roi list
  for (k in seq_along(RoiList.l)){
    RoiMask <- Template.l5$label_names == RoiList.l[k]
    df.l[,k] <- colMeans(Func.l[RoiMask, ])
  }
  # RH roi list
  for (w in seq_along(RoiList.r)){
    RoiMask <- Template.r5$label_names == RoiList.r[w]
    df.r[,w] <- colMeans(Func.r[RoiMask, ])
  }
  # matrix
  df <- cbind(df.l, df.r)
  df.cor <- cor(df, method = 'pearson')
  # raw matrix
  write.table(df.cor, paste0(Output.path, 'ROICorrelation_', i, '.txt'),
              col.names = F, row.names = F)
  # abs matrix
  df.cor.abs <- abs(df.cor)
  write.table(df.cor.abs, paste0(Output.path, 'abs/abs_ROICorrelation_', i, '.txt'),
              col.names = F, row.names = F)
  # positive matrix
  df.cor.pos <- df.cor
  df.cor.pos[df.cor.pos < 0] = 0
  write.table(df.cor.pos, paste0(Output.path, 'pos/pos_ROICorrelation_', i, '.txt'),
              col.names = F, row.names = F)
  # negative matrix
  df.cor.neg <- df.cor
  df.cor.neg[df.cor.neg > 0 ] = 0
  write.table(abs(df.cor.neg), paste0(Output.path, 'neg/neg_ROICorrelation_', i, '.txt'),
              col.names = F, row.names = F)
}

#############################################################################
Input.path <- 'AnatSurfWThickness/'; Output.path <- 'NetAnat/'
Template.l5.annot <- 'fsaverage5/label/lh.aparc.a2009s.annot'
Template.r5.annot <- 'fsaverage5/label/rh.aparc.a2009s.annot'
Template.l5 <- read.fs.annot(Template.l5.annot)
Template.r5 <- read.fs.annot(Template.r5.annot)
Subs <- list.dirs(Input.path, full.names = F, recursive = F)

RoiList.l.all <- Template.l5$colortable_df$struct_name
# x[! x %in% c('A', 'D', 'E')]
RoiList.l <- RoiList.l.all[! RoiList.l.all %in% c('Unknown', 'Medial_wall')]
RoiList.r.all <- Template.r5$colortable_df$struct_name
RoiList.r <- RoiList.r.all[! RoiList.r.all %in% c('Unknown', 'Medial_wall')]

#############################################################################
## anat prepare
df <- matrix(nrow = length(Subs), ncol = 149)
for (i in seq_along(Subs)){
  # files
  Anat.l.file = list.files(file.path(Input.path, Subs[i]), pattern = 'L', full.names = T)
  Anat.r.file = list.files(file.path(Input.path, Subs[i]), pattern = 'R', full.names = T)
  Anat.l = readgii(Anat.l.file); Anat.l = as.vector(Anat.l$data$unknown)
  Anat.r = readgii(Anat.r.file); Anat.r = as.vector(Anat.r$data$unknown)
  df[i,1] = Subs[i]
  # LH roi list
  for (k in seq_along(RoiList.l)){
    RoiMask <- Template.l5$label_names == RoiList.l[k]
    df[i,k+1] <- round(mean(Anat.l[RoiMask]), 5)
  }
  # RH roi list
  for (w in seq_along(RoiList.r)){
    RoiMask <- Template.r5$label_names == RoiList.r[w]
    df[i, w+75] <- round(mean(Anat.r[RoiMask]), 5)
  }
}
colnames(df) <- c('SubId', paste0('lh_', RoiList.l), paste0('rh_', RoiList.r))
df <- as.data.frame(df)
write.csv(df, paste0(Output.path, 'aparc.a2009s_both_thickness.csv'), row.names = F)

## end
