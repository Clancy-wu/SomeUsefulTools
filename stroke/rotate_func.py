#!/bin/python39
import numpy as np
import nibabel as nib
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

def rotate_file(file_name, new_filename):
    img = nib.load(file_name)
    matrix = img.get_fdata()
    new_matrix = matrix.copy()
    affine = img.affine.copy()
    hdr = img.header.copy()
    rotate_matrix = Rotate(new_matrix)
    new_nifti = nib.Nifti1Image(rotate_matrix, affine, hdr)
    return nib.save(new_nifti, new_filename)     

file = '/home/clancy/data/WuJing/org_bids/sub-LISHULAN/anat/sub-LISHULAN_T1w.nii'
new_filename = file.replace('T1w.nii', 'T1w_rotate.nii')

