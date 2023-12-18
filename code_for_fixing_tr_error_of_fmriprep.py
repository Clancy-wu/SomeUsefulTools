# When nii.gz file was preprcessed by fmriprep, the true TR number will be recorded in the json and the TR number of prepared
# nii.gz file will be set to 1.0 number.
# for some times, eg. in fsl and spm, TR number is read from nii.gz file instead of json. To fix this inappropriate issues, 
# this script is created.
# require pybids package.
from bids import BIDSLayout
import nibabel

def set_tr(img, tr):
    header = img.header.copy()
    zooms = header.get_zooms()[:3] + (tr,)
    header.set_zooms(zooms)
    return img.__class__(img.get_fdata().copy(), img.affine, header)

def sync_tr(bids_root):
    layout = BIDSLayout(bids_root)
    for nii in layout.get(extensions=['.nii', '.nii.gz']):
        metadata = layout.get_metadata(nii.path)
        if 'RepetitionTime' in metadata:
            img = nb.load(nii.path)
            if img.header.get_zooms()[3:] != (metadata['RepetitionTime'],):
                fixed_img = set_tr(img, metadata['RepetitionTime'])
                fixed_img.to_filename(nii.path)

if __name == "__main__":
  sync_tr()

## end. author @clancy_wu
