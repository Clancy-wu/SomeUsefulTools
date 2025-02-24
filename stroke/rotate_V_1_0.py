#!/bin/python39
print('    Convert is running, please wait ......')

import numpy as np
import nibabel as nb
import os

def Rotate(matrix):
    shape = np.shape(np.shape(matrix))[0]
    row = np.shape(matrix)[0]
    if shape == 3:
        convert = np.zeros((np.shape(matrix)[0],np.shape(matrix)[1],np.shape(matrix)[2]))
        for i in range(row):
            convert[i] = matrix[row-1-i]
    elif shape == 4:
        convert = np.zeros((np.shape(matrix)[0],np.shape(matrix)[1],np.shape(matrix)[2],np.shape(matrix)[3]))
        for i in range(row):
            convert[i] = matrix[row-1-i]
    return convert

if __name__ == '__main__':

    PWD = os.getcwd()
    path = os.path.join(PWD, 'convert')
    output = os.path.join(PWD, 'output')
    if os.path.exists(output) == False:
        os.mkdir(output)

    for file in os.listdir(path):
        # nii
        if file[-3:] == 'nii':
            img = nb.load(os.path.join(path, file))
            matrix = img.get_fdata()
            new_matrix = matrix.copy()
            affine = img.affine.copy()
            hdr = img.header.copy()
            rotate_matrix = Rotate(new_matrix)
            new_name = file[:-4] + '_rotate.nii'
            new_nifti = nb.Nifti1Image(rotate_matrix, affine, hdr)
            nb.save(new_nifti, os.path.join(output, new_name))

        # nii.gz
        if file[-6:] == 'nii.gz':
            img = nb.load(os.path.join(path, file))
            matrix = img.get_fdata()
            new_matrix = matrix.copy()
            affine = img.affine.copy()
            hdr = img.header.copy()
            # rotate
            rotate_matrix = Rotate(new_matrix)
            # save
            new_name = file[:-7] + '_rotate.nii.gz'
            new_nifti = nb.Nifti1Image(rotate_matrix, affine, hdr)
            nb.save(new_nifti, os.path.join(output, new_name))

    # show number of files in the output
    total_file = os.listdir(path)
    total_file_number = np.shape(total_file)[0]
    success_file = os.listdir(output)
    success_file_number = np.shape(success_file)[0]
    print('    %s in %s files convert successfully' %(success_file_number, total_file_number))

os.system('pause')