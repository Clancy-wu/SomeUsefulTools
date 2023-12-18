Dir = '/home/clancy/Documents/zhenlong_prepare/'
for (inters in list.files(Dir)) {
  # inters: control and intervention
  for (before in list.files(paste0(Dir, inters))) {
    # before: af and be
    for (DT in list.files(paste0(Dir, inters, '/', before))) {
     # DT: DWI and T1
      for (sub in list.files(paste0(Dir, inters, '/', before, '/', DT))) {
        SubFile = paste0(Dir, inters, '/', before, '/', DT, '/', sub)
        FileLen = length(list.files(SubFile))
        fileConn = file("prepare_log.txt")
        A = print(SubFile)
        B = print(as.character(FileLen))
        writeLines(A, fileConn)
        writeLines(B, fileConn)
        close(fileConn)
      }
    }
  }
}



