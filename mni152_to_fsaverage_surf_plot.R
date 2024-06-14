library(fsbrain)
library(RColorBrewer)
library(freesurferformats)
##############################################
# mri_vol2surf --src gsp_lAmyg_LH_T.nii.gz --out surf.gii --hemi rh --reg $FREESURFER_HOME/average/mni152.register.dat
# get vertex

# projectMNI2fsaverage -s gsp_lAmyg_LH_T.nii.gz -o surf/

##############################################
lh_num <- read.fs.morph.ni1('/home/clancy/Downloads/cit_amyg_FromJoel_result/surf/lh.gsp_lAmyg_LH_T.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz')
rh_num <- read.fs.morph.ni1('/home/clancy/Downloads/cit_amyg_FromJoel_result/surf/rh.gsp_lAmyg_LH_T.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz')

colFn_blue_red = colorRampPalette(c("#013e7d", "#FFFFFF", "#760715"));
fsbrain.set.default.figsize(1200, 1200);

coloredmeshes <- vis.data.on.fsaverage(
  vis_subject_id = "fsaverage",
  morph_data_lh = lh_num,
  morph_data_rh = rh_num,
  surface = "pial",
  views = c("t4"),
  rgloptions=rglo(),
  rglactions = list('trans_fun'=limit_fun(-20,20)), # limit values
  draw_colorbar = 'horizontal',
  makecmap_options = list('colFn'=colFn_blue_red, symm=TRUE, 'col.na'='white'),
  bg = 'curv_light',
  morph_data_both = NULL,
  style = "default"
)

#export(coloredmeshes, colorbar_legend = "sulcal depth [mm]", transparency_color = "#FFFFFF");
export(coloredmeshes, colorbar_legend = "");





############################################################################################
# T map
roi_file_name = 'gsp_mAmyg_RH_T'

fsbrain.set.default.figsize(1200, 1200);
print(paste0('projectMNI2fsaverage -s ', roi_file_name, '.nii.gz', ' -o surf/'))


lh_file = paste0('surf/lh.', roi_file_name, '.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz')
rh_file = paste0('surf/rh.', roi_file_name, '.allSub_RF_ANTs_MNI152_orig_to_fsaverage.nii.gz')
lh_num <- read.fs.morph.ni1(lh_file)
rh_num <- read.fs.morph.ni1(rh_file)
colFn_blue_red = colorRampPalette(c("#053061", "#FFFFFF", "#67001f"))

colFn_diverging = grDevices::colorRampPalette(rev(RColorBrewer::brewer.pal(1000, name="RdBu")))

coloredmeshes <- vis.data.on.fsaverage(
  vis_subject_id = "fsaverage",
  morph_data_lh = lh_num,
  morph_data_rh = rh_num,
  surface = "pial",
  views = c("t4"),
  rgloptions=rglo(),
  rglactions = list('trans_fun'=limit_fun(-20,20)), # limit values
  draw_colorbar = 'horizontal',
  makecmap_options = list('colFn'=colFn_diverging, symm=TRUE, 'col.na'='white'),
  bg = 'curv_light',
  morph_data_both = NULL,
  style = "default"
)
export(coloredmeshes, colorbar_legend = "", output_img = paste0(roi_file_name, '.png'));
