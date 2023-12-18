library(dplyr)

Old.dir = '/home/clancy/Documents/zhenlong_sort/'
New.dir = '/home/clancy/Documents/zhenlong_prepare/'
## begin
#subs.index = seq(1, 70)
#NewFile = sprintf('sub%03d', subs.index)
MetaData = read.csv('SubjectInformation.csv')
MetaData$OldIndex = as.character(MetaData$OldIndex)

# loop
for (inters in list.files(Old.dir)) {
  # inters = control + intervention
  for (before in list.files(paste0(Old.dir, inters))) {
    # before = af + be
    Dwi.path = paste0(Old.dir, inters, '/', before, '/DwiImg')
    T1.path = paste0(Old.dir, inters, '/', before, '/T1Img')
    # first sort Dwi
    for (sub in list.files(Dwi.path)) {
      SubFile.path.dwi = paste0(Dwi.path, '/', sub)
      SubFile.path.t1 = paste0(T1.path, '/', sub)
      NewSub = filter(MetaData, 
                      OldIndex == as.character(sub),
                      Group == inters,
                      Inters == before)$NewIndex
      NewSubFile.path.dwi = paste0(New.dir, NewSub, '/dwi')
      NewSubFile.path.t1 = paste0(New.dir, NewSub, '/anat')
      if (!dir.exists(NewSubFile.path.dwi)) {dir.create(NewSubFile.path.dwi, recursive=T)}
      if (!dir.exists(NewSubFile.path.t1)) {dir.create(NewSubFile.path.t1, recursive=T)}
      for (file in list.files(SubFile.path.dwi)){file.copy(file.path(SubFile.path.dwi,file), file.path(NewSubFile.path.dwi,file))}
      for (file in list.files(SubFile.path.t1)){file.copy(file.path(SubFile.path.t1,file), file.path(NewSubFile.path.t1,file))}
    }
  }
}


################################################################################
## sort anat
New.dir = '/home/clancy/Documents/zhenlong_prepare/'
for (sub in list.files(New.dir)) {
  FilePath = paste0(New.dir, sub, '/', 'anat')
  A = list.files(path=FilePath, pattern = '*Crop_1.nii', full.names = F)
  print(sub)
  print(A)
}







