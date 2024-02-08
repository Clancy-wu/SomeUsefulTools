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
def mmToVox_fsleyes_2mm(mmcoords):
	#function to convert mm coordinates in the standard 2mm MNI atlas into voxel coordinates
	voxcoords = ['','','']
	voxcoords[0] = str(int(round(mmcoords[0]/2))*-1+45)
	voxcoords[1] = str(int(round(mmcoords[1]/2))+63)
	voxcoords[2] = str(int(round(mmcoords[2]/2))+36)
	return voxcoords

def mmToVox_fsleyes_0_5mm(mmcoords):
	#function to convert mm coordinates in the standard 0.5mm MNI atlas into voxel coordinates
      # FSL space
	voxcoords = ['','','']
	voxcoords[0] = str(int(round((mmcoords[0])/0.5))*-1+180)
	voxcoords[1] = str(int(round((mmcoords[1])/0.5))+252)
	voxcoords[2] = str(int(round((mmcoords[2])/0.5))+144)
	return voxcoords  

def mmToVox_fsleyes_1mm(mmcoords):
	#function to convert mm coordinates in the standard 1mm MNI atlas into voxel coordinates
      # FSL space
	voxcoords = ['','','']
	voxcoords[0] = str(int(round((mmcoords[0])/1))*-1+90)
	voxcoords[1] = str(int(round((mmcoords[1])/1))+126)
	voxcoords[2] = str(int(round((mmcoords[2])/1))+72)
	return voxcoords  

def mmToVox_fsleyes_xmm(mmcoords, x):
	#function to convert mm coordinates in the standard 1mm MNI atlas into voxel coordinates
      # FSL space
	voxcoords = ['','','']
	voxcoords[0] = str(int(round((mmcoords[0])/x))*-1+(90/x))
	voxcoords[1] = str(int(round((mmcoords[1])/x))+(126/x))
	voxcoords[2] = str(int(round((mmcoords[2])/x))+(72/x))
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

#### 3. final transformation methods
# coord2voxel
def coord2voxel(my_coord, img_affine):
    mni_x, mni_y, mni_z = my_coord[0], my_coord[1], my_coord[2]
    coords = np.c_[
        np.atleast_1d(mni_x).flat,
        np.atleast_1d(mni_y).flat,
        np.atleast_1d(mni_z).flat,
        np.ones_like(np.atleast_1d(mni_z).flat),
    ].T
    project_affine = np.linalg.inv(img_affine)
    voxel_x, voxel_y, voxel_z, _ = np.around(np.dot(project_affine, coords))
    return voxel_x.item(), voxel_y.item(), voxel_z.item()
	
# voxel2coord
def voxel2cood(my_coord, img_affine):
    mni_x, mni_y, mni_z = my_coord[0], my_coord[1], my_coord[2]
    coords = np.c_[
        np.atleast_1d(mni_x).flat,
        np.atleast_1d(mni_y).flat,
        np.atleast_1d(mni_z).flat,
        np.ones_like(np.atleast_1d(mni_z).flat),
    ].T
    voxel_x, voxel_y, voxel_z, _ = np.around(np.dot(img_affine, coords))
    return voxel_x.item(), voxel_y.item(), voxel_z.item()

