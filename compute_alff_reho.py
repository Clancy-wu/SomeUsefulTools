# test alff and reho
# fmriprep process: orig file -> MNI file
# xcp-d process:   MNI file -> denoise (nuisance regression) + filter -> alff + reho + time series -> smooth all results

################## alff
orig_file = 'sub-sub001_task-rest_space-MNI152NLin2009cAsym_res-2_desc-denoised_bold.nii.gz'
targ_file = 'sub-sub001_task-rest_space-MNI152NLin2009cAsym_res-2_stat-alff_boldmap.nii.gz'

import nibabel as nb
import numpy as np
from scipy import signal
from scipy.stats import rankdata

# compute_alff(data_matrix, low_pass, high_pass, TR, sample_mask=None
TR = 2.0
file_data = nb.load(orig_file).get_fdata()
data_matrix = file_data.reshape(( file_data.shape[0]*file_data.shape[1]*file_data.shape[2], file_data.shape[3]))

high_pass = 0.01
low_pass = 0.10

#######################
fs = 1 / TR  # sampling frequency
n_voxels, n_volumes = data_matrix.shape
alff = np.zeros(n_voxels) # initial the voxel
for i_voxel in range(n_voxels):
    voxel_data = data_matrix[i_voxel, :] # (240, )
    # some voxels will be zero crossing all times, set these voxel to alff=0
    if np.std(voxel_data) == 0:
        alff[i_voxel] = 0
        continue
    sd_scale = np.std(voxel_data)
    voxel_data -= np.mean(voxel_data)
    voxel_data /= np.std(voxel_data)
    frequencies_hz, power_spectrum = signal.periodogram(
                voxel_data,
                fs,
                scaling="spectrum",
            )
    power_spectrum_sqrt = np.sqrt(power_spectrum)
    if high_pass == 0:
        high_pass = frequencies_hz[0]
    if low_pass == 0:
        low_pass = frequencies_hz[-1]
    ff_alff = [
        np.argmin(np.abs(frequencies_hz - high_pass)),
        np.argmin(np.abs(frequencies_hz - low_pass)),
        ]
    alff[i_voxel] = len(ff_alff) * np.mean(power_spectrum_sqrt[ff_alff[0] : ff_alff[1]])
    alff[i_voxel] *= sd_scale

alff = alff[:, None]
print(alff)
     
targ_data = nb.load(targ_file).get_fdata()
targ_data_1d = targ_data.reshape(-1, targ_data.shape[-1])

alff[alff!=0]
#array([1.57014704, 1.55542568, 0.97892727, ..., 0.86730102, 0.77369999,
#       0.83799011])
targ_data_1d[targ_data_1d!=0]
#array([1.57014704, 1.55542564, 0.97892725, ..., 0.86730099, 0.7737    ,
#       0.83799011])
