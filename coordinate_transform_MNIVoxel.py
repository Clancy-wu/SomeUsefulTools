## coordinate transform (2mm resolution)
#### 1. MNI coordinats to Voxel coordinates
def mmToVox(mmcoords):
	#function to convert mm coordinates in the standard 2mm MNI atlas into voxel coordinates
	voxcoords = ['','','']
	voxcoords[0] = str(int(round(int(mmcoords[0])/2))*-1+45)
	voxcoords[1] = str(int(round(int(mmcoords[1])/2))+63)
	voxcoords[2] = str(int(round(int(mmcoords[2])/2))+36)
	return voxcoords
  
#### 2. Voxel coordinates to MNI coordinates
def coords(inputimage, i, j, k):
    """Returns X, Y, Z coordinates for i, j, k
    i,j,k is the voxel coordinats
    X,Y,Z is the MNI coordinats
    refer to https://nipy.org/nibabel/coordinate_systems.html
    """
    M = inputimage.affine[:3, :3]
    abc = inputimage.affine[:3, 3]
    return M.dot([i, j, k]) + abc


nilearn.image.coord_transform(x, y, z, affine)
# the function "coord_transform" in the nilearn can transform
# voxel space to the image space you choose (either MNI or T1w)

import numpy as np
import nibabel as nib

# Load your transformation matrix
transform_matrix = np.array([[a, b, c, d],
                              [e, f, g, h],
                              [i, j, k, l],
                              [0, 0, 0, 1]])  # Example transformation matrix
# Load voxel size
voxel_size = np.array([voxel_size_x, voxel_size_y, voxel_size_z])  # Example voxel size
# Load MNI coordinates
mni_coordinates = np.array([x_mni, y_mni, z_mni])  # Example MNI coordinates
# Inverse transformation
inverse_transform = np.linalg.inv(transform_matrix)
voxel_coordinates = np.dot(np.hstack((mni_coordinates, 1)), inverse_transform)[:3]
# Convert to voxel coordinates
voxel_coordinates /= voxel_size
print("Voxel coordinates:", voxel_coordinates)
  
