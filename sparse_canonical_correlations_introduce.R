library(ggplot2)
library(GGally)
library(CCA)
library(CCP)

mm <- read.csv("https://stats.idre.ucla.edu/stat/data/mmreg.csv")
colnames(mm) <- c("Control", "Concept", "Motivation", "Read", "Write", "Math", 
                  "Science", "Sex")
summary(mm)
psych <- mm[, 1:3]
acad <- mm[, 4:8]

# standard pearson correlations
CCA::matcor(psych, acad)

# canonial correlations
cc1 <- CCA::cc(psych, acad)
# display the canonical correlations
cc1$cor


cc2 <- comput(psych, acad, cc1)
# display canonical loadings
cc2[3:6]

