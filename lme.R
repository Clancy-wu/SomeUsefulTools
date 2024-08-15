data = read.csv('all_sub_info_SiteSpecific.csv')
library(afex)
site_orders = c('R_M1', 'R_IPL', 'R_preSMA', 'R_FEF', 'R_IFJ', 'R_Fp', 'R_aMFG', 'R_pMFG', 'L_aMFG', 'L_pMFG', 'L_Fp')
data$site = factor(data$site, levels = site_orders) # set orders to make R_M1 to be the comparison
all_col_names = colnames(data)
roi_names = all_col_names[6:length(all_col_names)] # ROI.1 , ROI.2 ...
###############################################################################
# prepare for run
stat_out = data.frame( matrix(nrow=length(site_orders), ncol=length(roi_names)) ) # empty output
colnames(stat_out) = roi_names
rownames(stat_out) = c('intercept', site_orders[-1]) # remove R_M1, add intercept
# empty tables for beta value, p value, and F test value
stat_beta = stat_t = stat_p = stat_out
stat_Ftest = data.frame( matrix(nrow = 2, ncol = length(roi_names)) )
colnames(stat_Ftest) = roi_names
rownames(stat_Ftest) = c('Fvalue', 'Pvalue')

# run
for (roi in roi_names){
  # extract ROI data
  roi_table = data.frame(site = data$site, subject = data$subject, value = data[[roi]])
  # method S: the Satterthwaite approximation for degrees of freedom
  # methods PB and LRT will make a pvalue same as the matlab lme function.
  mod <- afex::lmer_alt(value ~ site + (1|subject), data=roi_table, method="PB")
  mod_result = summary(mod)
  # main effect: F test
  F_test = anova(mod)
  stat_Ftest[1, roi] = F_test$`F value`
  stat_Ftest[2, roi] = F_test$`Pr(>F)`
  # estimate value: beta
  stat_beta[, roi] = mod_result$coefficients[, 'Estimate']
  # statistic value: t value
  stat_t[, roi] = mod_result$coefficients[, 't value']
  # p value
  stat_p[, roi] = mod_result$coefficients[, 'Pr(>|t|)']
}
###############################################################################
# add multi-correlation
stat_Ftest['Pvalue_FDR', ] = p.adjust(stat_Ftest['Pvalue', ], method = 'fdr')
stat_Ftest['Pvalue_BH', ] = p.adjust(stat_Ftest['Pvalue', ], method = 'BH')
stat_Ftest['Pvalue_BY', ] = p.adjust(stat_Ftest['Pvalue', ], method = 'BY')
stat_Ftest['Pvalue_none', ] = p.adjust(stat_Ftest['Pvalue', ], method = 'none')
# save data
write.csv(stat_Ftest, 'spec_lme_Ftest.csv')
write.csv(stat_beta, 'spec_lme_beta.csv')
write.csv(stat_t, 'spec_lme_t.csv')
write.csv(stat_p, 'spec_lme_pvalue.csv')
print('end.')
###############################################################################
# write csv to nii img
library(freesurferformats)

csv2nii_img <- function(csv_table, out_img_suffix, use_log=FALSE){
  # csv table: columnes are roi names
  template = 'BN_Atlas_274_combined_resample.nii.gz' # reshaped
  template_head = read.nifti1.header(template) # head
  template_data = read.nifti1.data(template) # data
  # make img by row
  for (i in seq(dim(csv_table)[1])){
    # i is the row
    # make empty data
    empty_data = array(0, dim = dim(template_data))
    # use roi_names
    for (roi in roi_names){
      roi_index = as.numeric(gsub('[^0-9]', '', roi))
      roi_index_mask = (template_data == roi_index)
      if (use_log == TRUE){ empty_data[roi_index_mask] = -log10(csv_table[i, roi]) }
      if (use_log == FALSE){ empty_data[roi_index_mask] = csv_table[i, roi] }
    }
    # make image
    new_img_name = paste0('spec_lme_', out_img_suffix, '_', rownames(csv_table)[i], '.nii.gz')
    write.nifti1(new_img_name, niidata = empty_data, niiheader = template_head)
  }
  print('finished.')
}

csv2nii_img(stat_beta, 'Beta', use_log=FALSE)
csv2nii_img(stat_t, 'Tvalue', use_log=FALSE)
csv2nii_img(stat_p, 'LogP', use_log=TRUE)
csv2nii_img(stat_Ftest[1, ], 'F', use_log=FALSE)
csv2nii_img(stat_Ftest[-1, ], 'LogF', use_log=TRUE)

# end
#####################################################
# F test summary
# -log10(0.05) = 1.30103
sum(stat_Ftest['Pvalue_FDR', ]<0.05) # 6
sum(stat_Ftest['Pvalue_BH', ]<0.05) # 6
sum(stat_Ftest['Pvalue_BY', ]<0.05) # 2
sum(stat_Ftest['Pvalue_none', ]<0.05) # 76

aa = stat_Ftest['Pvalue_FDR', ]
aa[, aa<0.05]
# ROI.157    ROI.169    ROI.180    ROI.191    ROI.217    ROI.219
#####################################################
# ROI_157: A1/2/3tonIa_L
# ROI_169: vId/vIq_L
# ROI_180: A32p_R
# ROI_191: rCunG_L
# ROI_217: cHipp_L
# ROI_219: vCa_L

library(data.table)
library(corrplot)
library(magrittr)

data = fread('all_sub_info_SiteSpecific.csv')
compare_sites = c('R_M1', 'R_IPL', 'R_preSMA', 'R_FEF', 'R_IFJ', 'R_Fp', 'R_aMFG', 'R_pMFG', 'L_aMFG', 'L_pMFG', 'L_Fp') # 11 sites

compare_data = data[, .(subject, site, `ROI-219`)]
colnames(compare_data) = c('subject', 'site', 'Value')
site_from=vector(); site_to=vector(); value_T=vector(); value_P=vector(); value_FDR_P=vector()
for (site_1 in compare_sites){
  for (site_2 in compare_sites){
    if (site_1 == site_2){
      {} # pass
    }else{
      result = t.test(compare_data[site==site_1, .(Value)], compare_data[site==site_2, .(Value)], alternative = 'two.sided', var.equal = T) # student ttest
      site_from = c(site_from, site_1)
      site_to = c(site_to, site_2)
      value_T = c(value_T, as.numeric(result$statistic))
      value_P = c(value_P, result$p.value)      
    }
  }
}

value_FDR_P = p.adjust(value_P, method = 'fdr')
df_out=data.table(
    site_from = site_from,
    site_to = site_to,
    value_T = value_T,
    value_P = value_P,
    value_FDR_P = value_FDR_P
  )

site_num = length(compare_sites)
M <- matrix(data = 0, nrow = site_num, ncol = site_num); colnames(M) <- compare_sites; rownames(M) <- compare_sites
M_p <- matrix(data = 1, nrow = site_num, ncol = site_num); colnames(M_p) <- compare_sites; rownames(M_p) <- compare_sites
for (i in seq(dim(df_out)[1])){
  i_df = df_out[i,]
  M[i_df[,1][[1]], i_df[,2][[1]]] = i_df[,3][[1]] #  value_T
  M_p[i_df[,1][[1]], i_df[,2][[1]]] = i_df[,5][[1]] #  value_FDR_P
}

corrplot(M, p.mat = M_p,sig.level = 0.05, method = 'circle', type='lower', insig='blank', addCoef.col = 'white', number.cex = 1, diag = FALSE, is.corr = F, 
         col = rev(COL2('RdBu')), tl.col = 'black', tl.srt = 45 )
# 8 x 8


############################################




compare_sites = c('R_M1', 'R_IPL', 'R_preSMA', 'R_FEF', 'R_IFJ', 'R_Fp', 'R_aMFG', 'R_pMFG', 'L_aMFG', 'L_pMFG', 'L_Fp')
compare_data = data[, .(subject, site, `ROI-180`)]
colnames(compare_data) = c('subject', 'site', 'Value')
site_from=vector(); site_to=vector(); value_T=vector(); value_P=vector(); value_FDR_P=vector()

for (site_1 in compare_sites){
  for (site_2 in compare_sites){
    if (site_1 == site_2){
      {} # pass
    }else{
      #site_1_control = as.vector(compare_data[site==site_1, .(Value)])$Value - as.vector(compare_data[site=='R_M1', .(Value)])$Value  #not in same length
      #site_2_control = as.vector(compare_data[site==site_2, .(Value)])$Value - as.vector(compare_data[site=='R_M1', .(Value)])$Value
      result = t.test(compare_data[site==site_1, .(Value)], compare_data[site==site_2, .(Value)], alternative = 'two.sided', var.equal = T) # student ttest
      site_from = c(site_from, site_1)
      site_to = c(site_to, site_2)
      value_T = c(value_T, as.numeric(result$statistic))
      value_P = c(value_P, result$p.value)      
    }
  }
}
value_FDR_P = p.adjust(value_P, method = 'fdr')
value_FDR_P[value_FDR_P<0.05]
