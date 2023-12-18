library(ggplot2)
data.fsl <- read.table('fsl_logs/amygdala_results.txt', sep = ' ', header = T)
data.freesurfer <- read.table('freesurfer_logs/amygdala_results.txt', sep = ' ', header = T)

# left
data.compare.lh <- data.frame(
  Subject = c(seq_along(data.fsl$SubjectID), seq_along(data.freesurfer$SubjectID)),
  Group = c(rep('fsl', 29), rep('freesurfer', 29)),
  Volume = c(data.fsl$LeftVolume, data.freesurfer$LeftVolume)
)

data.compare.lh$Group <- as.factor(data.compare.lh$Group)
data.compare.lh$Volume <- as.numeric(data.compare.lh$Volume)

ggplot(data.compare.lh, aes(x=Subject, y=Volume, color=Group) )+
  geom_point(size=2)+
  geom_line(linewidth=2)+
  ggtitle('Left amygdala volume')+
  theme_bw()+
  theme(plot.title = element_text(hjust = 0.5, size=20))
  
  
# right
data.compare.rh <- data.frame(
  Subject = c(seq_along(data.fsl$SubjectID), seq_along(data.freesurfer$SubjectID)),
  Group = c(rep('fsl', 29), rep('freesurfer', 29)),
  Volume = c(data.fsl$RightVolume, data.freesurfer$RightVolume)
)

data.compare.rh$Group <- as.factor(data.compare.rh$Group)
data.compare.rh$Volume <- as.numeric(data.compare.rh$Volume)

ggplot(data.compare.rh, aes(x=Subject, y=Volume, color=Group) )+
  geom_point(size=2)+
  geom_line(linewidth=2)+
  ggtitle('Right amygdala volume')+
  theme_bw()+
  theme(plot.title = element_text(hjust = 0.5, size=20))


