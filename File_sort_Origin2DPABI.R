pwd = getwd()
AllFiles = list.dirs(pwd)

# sort files
for (i in AllFiles) {
  Name = unlist(strsplit(i, '/'))
  Name.module = tail(Name,1)
  if (Name.module == 'T1') {
    Name.sub = tail(Name,2)[1]
    Name.new = paste0(pwd, '/T1Raw/', Name.sub)
    file.rename(i, Name.new)
  }else if (Name.module == 'DTI'){
    Name.sub = tail(Name,2)[1]
    Name.new = paste0(pwd, '/DtiRaw/', Name.sub)
    file.rename(i, Name.new)
  }
}