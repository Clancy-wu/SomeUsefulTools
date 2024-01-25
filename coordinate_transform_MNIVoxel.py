## coordinate transform (2mm resolution)
#### 1. MNI coordinats to Voxel coordinates
def mmToVox(mmcoords):
	#function to convert mm coordinates in the standard 2mm MNI atlas into voxel coordinates
	voxcoords = ['','','']
	voxcoords[0] = str(int(round(int(mmcoords[0])/2))*-1+45)
	voxcoords[1] = str(int(round(int(mmcoords[1])/2))+63)
	voxcoords[2] = str(int(round(int(mmcoords[2])/2))+36)
	return voxcoords
	
## a better one that is corresponded to FSLeyes.
def mmToVox_fsleyes(mmcoords):
	#function to convert mm coordinates in the standard 2mm MNI atlas into voxel coordinates
	voxcoords = ['','','']
	voxcoords[0] = str(int(round(mmcoords[0]/2))*-1+45)
	voxcoords[1] = str(int(round(mmcoords[1]/2))+63)
	voxcoords[2] = str(int(round(mmcoords[2]/2))+36)
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

# the function "coord_transform" in the nilearn can transform
# voxel space to the image space you choose (either MNI or T1w)
nilearn.image.coord_transform(x, y, z, affine)


