#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spatial SNR and temporal SFNR function
Authors: Brandon Egger (beggr@uiowa.edu), Dorit Kliemann (dkliemann@uiowa.edu), Satra!!!
Adapted: Mike Tyszka (jmt@caltech.edu) 
This script has been written for use in the Social Cognitive Lab at the
University of Iowa
python3 "${sortScriptPath}/SNRSorter.py" "${DERIVATIVES}" "${BIDS_PATH}" -s "${SPACE}" -o "${OUTPUT_DIR}
python3 /Shared/klie/data/code/amygdalaFC/createSNR/SNRSorter.py '/Shared/klie/data/projects/fca/data/mri/derivatives' '/Shared/klie/data/projects/fca/data/mri/bids' -c 'fca' -s 'T1w_res-2' -o '/Shared/klie/data/projects/fca/data/mri/derivatives/snr' -d 'T1w'
"""
from nilearn import image, regions
from nilearn.input_data import NiftiMapsMasker
import numpy as np
import nibabel as nb
import glob
import os
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from scipy import stats
from nibabel.processing import resample_from_to, resample_to_output
import nitransforms as nt
from nilearn.image import resample_img, index_img, binarize_img, resample_to_img
from pathlib import Path # DK
import pdb as ipdb

import sys
sys.path.append('../')
import subjectListHandler
from utils.io.logger import LOGGER
from utils.io.files import get_param_default_from_environ


#Config:
OUTPUT_PATH = "outputs/" #Default path output csv is produced
SPACE = "T1w_res-2" #Default space
SPACEORIG = "T1w"
STD_BELOW_MEAN = 3.0 #Flag subjects with value this many STDs below the site mean
DERIVATIVES_ROOT = get_param_default_from_environ('DERIVATIVES_ROOT')

#####ISSUE TO READ IN CSV IN
#####ISSUES TO RUN PER RUN

def calc_snr(mc_bold_file, mc_bold_orig_file, nuc_files, raw_bold_file, air_perc_thresh=2):
    """
    Calculate sSNR and tSFNR from 4D motion corrected BOLD series
    Parameters:
        mc_bold_file: str, pathlike
            Motion corrected BOLD Nifti filename
        nuc_files: list
            Nuclear mask filenames
        raw_bold_file: str, pathlike
            Original BOLD image file
        air_perc_thresh: float
            Nominal percentile threshold for air space
    """
    # CREATE resampled bold for TFSNR
    #load in orig bold in output space (T1) but original resolution from fmriprep
    mc_bold_orig_img = image.load_img(mc_bold_orig_file)
    mc_tmean_orig_img = image.mean_img(mc_bold_orig_img)


    detrended_orig_img = image.clean_img(mc_bold_orig_img, detrend=True, standardize=False)
    tfluc_orig_img = image.math_img("np.std(img, axis=-1)", img=detrended_orig_img)

    # Calculate temporal SFNR for MC BOLD series
    tfsnr_orig = nb.Nifti1Image(
        mc_tmean_orig_img.dataobj / tfluc_orig_img.dataobj,
        affine=mc_tmean_orig_img.affine,
        header=mc_tmean_orig_img.header
    )
    tfsnr_orig.dataobj[np.where(tfluc_orig_img.dataobj[...] == 0)] = np.nan
    tfsnr_orig.dataobj[np.where(np.isfinite(tfsnr_orig.dataobj) == False)] = 0
    tfsnr_orig_2mm_nii = resample_to_output(tfsnr_orig, (2,2,2))
    

    



    ####OLD VERSION
    # Load 4D BOLD series as nilearn image objects
    mc_bold_img = image.load_img(mc_bold_file)
    raw_bold_img = image.load_img(raw_bold_file)

    # Temporal mean of MC BOLD series (3D)
    mc_tmean_img = image.mean_img(mc_bold_img)

    # Linear detrend MC BOLD series for temporal fluctuation SD estimate
    detrended_img = image.clean_img(mc_bold_img, detrend=True, standardize=False)
    tfluc_img = image.math_img("np.std(img, axis=-1)", img=detrended_img)

    # Estimate air signal threshold from temporal mean of raw BOLD data
    # TODO: Why not use MC BOLD data?
    # TODO: Low level background artifacts probably still included in air noise SD estimate
    # TODO: Estimate air noise distribution some other way (Wavelet decomposition?)
    raw_median_img = image.math_img("np.nanmedian(img, axis=-1)", img=raw_bold_img)
    air_thresh = np.percentile(raw_median_img.dataobj[np.where(raw_median_img.dataobj[...] > 0)], air_perc_thresh)

    # Create 3D air mask from thresholded 4D raw BOLD data
    air_mask = np.sum(raw_bold_img.dataobj < air_thresh, axis=-1) > 0

    # Robust estimate of noise sigma in 4D air space using MAD of air space
    # Assumes Rayleigh noise distribution
    noise_sd = np.nanmedian(raw_median_img.dataobj[air_mask]) / 0.6745
    #noise_sd = stats.median_abs_deviation(raw_median_img.dataobj[air_mask], scale="normal") # air_noise


    # Calculate temporal SFNR for MC BOLD series
   # tsfnr = nb.Nifti1Image(
   #     mc_tmean_img.dataobj / tfluc_img.dataobj,
   #     affine=mc_tmean_img.affine,
   #     header=mc_tmean_img.header
   # )

    airmask_image = nb.Nifti1Image(
        air_mask,
        affine=raw_median_img.affine,
        header=raw_median_img.header
    )
    # Replace zero SD voxels with NaNs

#    tsfnr.dataobj[np.where(tfluc_img.dataobj[...] == 0)] = np.nan

    # Calculate regional sSNR and tSFNR

    # Init result lists
    region_snr = []
    region_tsfnr = []
    
    mc_tmean_img.dataobj[np.where(np.isfinite(mc_tmean_img.dataobj) == False)] = 0

    # Loop over all regional masks
    for filename in nuc_files:

        region = nb.load(filename)
        region_mask = np.where(region.dataobj[...] > 0)

        # Regional spatial SNR of MC tmean BOLD
        # Temporal mean regional signal / air space noise SD estimate


        region_snr.append(np.mean(mc_tmean_img.dataobj[region_mask]) / noise_sd)

        # Regional tSFNR
        region_tsfnr.append(np.nanmean(tfsnr_orig_2mm_nii.dataobj[region_mask]))

    return tfsnr_orig_2mm_nii, airmask_image, region_snr, region_tsfnr, noise_sd

def addSiteToCSV(siteName, df, filePath):
    """
    Takes a site SNR 
    """
    fileName = filePath.strip("/").split("/")[-1] #include entire path except for csv file
    outputPath = filePath[0:len(filePath)-len(fileName)]
    
    try:
        if (not os.path.isdir(outputPath)):
            os.makedirs(outputPath)

        if (os.path.exists(filePath)):
            #csv file already exists, we need to merge them
            oldDF = pd.read_csv(filePath)

            if (siteName in oldDF['site'].values):
                oldDF = oldDF.drop(df.index[df['site'] == siteName], inplace = True)

            df = pd.concat([oldDF, df], ignore_index=True)

        df.to_csv(filePath, index=False)
    except:
        LOGGER.warning(f"Unable to save csv {filePath} at this time")


def computeSiteSNR(pathToSite, pathToAbideSite, maxDeviationBelowMean=STD_BELOW_MEAN, outputDir=OUTPUT_PATH, space=SPACE, outputGraph=False, spaceorig=SPACEORIG, subjListPath=None):
    df = pd.DataFrame(columns=["subject", "site", "abide", "seed", "region_snr", "region_tfsnr", "include", "run"])
    errorDF = pd.DataFrame(columns=["subject", "site", "abide", "error", "run"])

    #abideName = pathToSite.strip("/").split("/")[-2]
    #siteFolderName = pathToSite.strip("/").split("/")[-1] #With derivatives
    #siteNameList = siteFolderName.split("_")
    #siteNameList.remove("derivatives")
    #siteName = '_'.join(siteNameList) #No _derivatives
    siteName = site # DK
    abideName = 'fca'
    RUN_ID_LIST = [f"run-{i}" for i in range(1,6)]

    ### <handle subject list>
    #subjListPath = os.path.join(pathToSite,"subj_list.txt") DK
    # subjListPath = os.path.join(pathToSite,"subj_list-dorit.csv") #DK
    if subjListPath is None:
        raise ValueError(f"subjListPath needed, found --> {subjListPath}")

    subjSeedFolderPaths = None
    if (os.path.exists(subjListPath)):
        subjSeedFolderPaths = subjectListHandler.parse_subject_list_from_file(subjListPath)
        subjSeedFolderPaths = [os.path.join(pathToSite, "seeds/", subjectName) for subjectName in subjSeedFolderPaths]
        # with open(subjListPath) as f:
            # subjSeedFolderPaths = [os.path.join(pathToSite, "seeds/", subjectName) for subjectName in f.read().split(" ")]
    
    if subjSeedFolderPaths == None:
        LOGGER.warning(f"Unable to access subj_list.txt for {pathToSite}, using all subjects (this may cause errors if some subjects are not processed)")
        subjSeedFolderPaths = glob.glob(os.path.join(pathToSite,f"seeds/*"))
    ### </handle subject list>

    ### <main processing loop, needs to support multiple-runs>
    LOGGER.info(f"To process --> ({len(subjSeedFolderPaths)})")
    for subjSeedPath in subjSeedFolderPaths:
        subjName = subjSeedPath.strip("/").split("/")[-1]
        LOGGER.info(f"Now processing: {subjName}\t{subjSeedPath}")
        LOGGER.info(f"Grabbing the following seeds from path "+str(os.path.join(subjSeedPath, f"{space}/*")))
        nucFiles = [seedBin for seedBin in glob.glob(os.path.join(subjSeedPath, f"{space}/*")) if seedBin.split('.')[0].split("_")[-1] == "bin"] #Acquire only bin files
        LOGGER.info(f"Grabbed seeds: {nucFiles}")
        
        rowDict = {"subject":subjName, "site":siteName, "abide":abideName, "seed":None, "region_snr":None, "region_tfsnr":None, "include":None, "noise_sd":None, "run":-1}
        if (len(nucFiles) == 0):
            LOGGER.error(f"Unable to compute subject: {subjName} from site: {siteName}. They have no seeds!")
            errorDF = errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"no seed files", "run": -1}, ignore_index=True)
        else:
            for RUN_ID in RUN_ID_LIST:
                LOGGER.info(f"--> {subjName} : {RUN_ID}")
                pathToFunc = os.path.join(pathToSite, f"fmriprep/{subjName}/func")
                pathToAnat = os.path.join(pathToSite, f"fmriprep/{subjName}/anat")
                pathToAbideFunc = os.path.join(pathToAbideSite, f"{subjName}/func")

                if (not os.path.isdir(pathToFunc)) or (not os.path.isdir(pathToAnat)):
                    pathToFunc = os.path.join(pathToSite, f"fmriprep/{subjName}/*/func")
                    pathToAnat = os.path.join(pathToSite, f"fmriprep/{subjName}/*/anat")
                    pathToAbideFunc = os.path.join(pathToAbideSite, f"{subjName}/*/func")

                mcBoldFile = None
                try:
                    # mcBoldFile = glob.glob(os.path.join(pathToFunc, f"{subjName}*_space-{space}_desc-preproc_bold.nii.gz"))[0] #DK RUN DEPENDENT
                    mcBoldFile = glob.glob(os.path.join(pathToFunc, f"{subjName}*{RUN_ID}_space-{space}_desc-preproc_bold.nii.gz"))[0] #DK RUN DEPENDENT
                except:
                    LOGGER.error("Error finding mc bold file")

                mcBoldFileOrig = None
                try:
                    mcBoldFileOrig = glob.glob(os.path.join(pathToFunc, f"{subjName}*{RUN_ID}_space-{spaceorig}_desc-preproc_bold.nii.gz"))[0] #DK RUN DEPENDENT
                except:
                    LOGGER.error("Error finding mc bold file")


                rawBoldFile = None
                try:
                    # These runs are zero-padded
                    rawBoldFile = glob.glob(os.path.join(pathToAbideFunc, f"{subjName}*-rest_{RUN_ID.replace('-','-0')}_bold.nii.gz"))[0] #DK RUN DEPENDENT
                except:
                    LOGGER.error("Error finding raw bold file")

                gmMaskBinFile = None
                try:
                    gmMaskBinFile = glob.glob(os.path.join(pathToAnat, f"{subjName}*_space-{space}_label-GM_033thr_bin.nii.gz"))[0]
                    nucFiles.append(gmMaskBinFile)
                except:
                    LOGGER.error("Error finding gm mask bin file")

                try:
                    dsegIn = glob.glob(os.path.join(pathToFunc, f"{subjName}*_task-rest_{RUN_ID}_space-{space}_desc-aparcaseg_dseg.nii.gz"))[0] #DK RUN DEPENDENT
                    dsegImg = nb.load(dsegIn)
                    dsegInSplit = dsegIn.strip("/").split("/")
                    dsegOut = os.path.join(pathToFunc, dsegInSplit[-1].replace("_desc-aparcaseg_dseg.nii.gz","_desc-aparcaseg_21021only.nii.gz")) #DK RUN DEPENDENT
                    if ("*" in dsegOut.strip("/").split("/")):
                         dsegSes = dsegInSplit[dsegInSplit.index("func")-1]
                         dsegOut = os.path.join(pathToSite, f"fmriprep/{subjName}/{dsegSes}/func", dsegIn.strip("/").split("/")[-1].replace("_desc-aparcaseg_dseg.nii.gz","_desc-aparcaseg_21021only.nii.gz"))     #DK RUN DEPENDENT
                    nb.Nifti1Image(np.logical_or(dsegImg.dataobj[...] == 1021, dsegImg.dataobj[...] == 2021), affine=dsegImg.affine, header=dsegImg.header).to_filename(dsegOut)
                    nucFiles.append(dsegOut)
                except:
                    LOGGER.error("dsegOut step failed")

                """OLD
                mcBoldFile = glob.glob(os.path.join(pathToSite, f"fmriprep/{subjName}/func/{subjName}_task-*_space-{space}_desc-preproc_bold.nii.gz"))
                if len(mcBoldFile) == 0:
                    mcBoldFile = glob.glob(os.path.join(pathToSite, f"fmriprep/{subjName}/*/func/{subjName}*_task-*_space-{space}_desc-preproc_bold.nii.gz"))

                gmMaskBinFile = glob.glob(os.path.join(pathToSite, f"fmriprep/{subjName}/anat/{subjName}*_space-T1w_res-2_label-GM_033thr_bin.nii.gz"))
                if len(gmMaskBinFile) == 0:
                    gmMaskBinFile = glob.glob(os.path.join(pathToSite, f"fmriprep/{subjName}/*/anat/{subjName}*_space-T1w_res-2_label-GM_033thr_bin.nii.gz"))

                rawBoldFile = glob.glob(os.path.join(pathToAbideSite, f"{subjName}/func/{subjName}_task-*_bold.nii.gz"))
                if len(rawBoldFile) == 0:
                    rawBoldFile = glob.glob(os.path.join(pathToAbideSite, f"{subjName}/*/func/{subjName}*_task-*_bold.nii.gz"))

                if len(mcBoldFile) == 0 or len(rawBoldFile) == 0:
                    mcBoldFile = None
                    rawBoldFile = None
                else:
                    mcBoldFile = mcBoldFile[0]
                    rawBoldFile = rawBoldFile[0]

                if len(gmMaskBinFile) == 0:
                    errorMsg=f"Unable to find gm_mask_bin file for {subjName}"
                    LOGGER.error(errorMsg)
                    errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":errorMsg}, ignore_index=True)
                else:
                    nucFiles.append(gmMaskBinFile[0])
                """

                if mcBoldFile == None or rawBoldFile == None:
                    LOGGER.error(f"Unable to retrieve path for raw and mc bold file for {subjName}")
                    errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"Unable to retrieve path for raw and mc bold file", "run": RUN_ID}, ignore_index=True)
                    rowDict["include"] = 0
                elif (not os.path.exists(mcBoldFile)):
                    LOGGER.error(f"The mc bold file was not found! ({mcBoldFile})")
                    errorDF = errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"no mc bold", "run": RUN_ID}, ignore_index=True)
                    rowDict["include"] = 0
                elif (not os.path.exists(rawBoldFile)):
                    LOGGER.error(f"The raw bold file was not found! ({rawBoldFile})")
                    errorDF = errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"no raw bold", "run": RUN_ID}, ignore_index=True)
                    rowDict["include"] = 0
                else:
                    LOGGER.info(f"Using raw bold file: {rawBoldFile} and mc bold file: {mcBoldFile}")

                    try:
                        tfsnr, airmask_image, regionSnrs, regionTfsnrs, noise_sd = calc_snr(mcBoldFile, mcBoldFileOrig, nucFiles, rawBoldFile) #run calculations

                        # snrPath = os.path.join(pathToSite, f"snr/{subjName}")  # raygon Nov 26, 2023
                        snrPath = os.path.join(outputDir, f"snr/{subjName}")  # raygon Nov 26, 2023
                        if (not os.path.isdir(snrPath)): #Make sure the SNR path is created
                            os.makedirs(snrPath)

                        nb.nifti1.save(tfsnr, os.path.join(snrPath,f"tfsnr_{RUN_ID}.nii.gz"))
                        nb.nifti1.save(airmask_image, os.path.join(snrPath,f"airmask_{RUN_ID}.nii.gz"))

                        regionIndex = 0
                        for seedFile in nucFiles:
                            seedFileName = seedFile.strip("/").split("/")[-1]
                            regionSnr = regionSnrs[regionIndex]
                            regionTfsnr = regionTfsnrs[regionIndex]

                            convertedSeedFileName = seedFileName.split(".")[0].replace(subjName+"_", "").replace("space-T1w_res-2_", "").replace("_bin", "")
                            if convertedSeedFileName.find("run") != -1:
                                convertedSeedFileName = convertedSeedFileName[convertedSeedFileName.find("run")+6:]

                            rowDict["seed"] = convertedSeedFileName
                            rowDict["region_snr"] = regionSnr
                            rowDict["region_tfsnr"] = regionTfsnr
                            rowDict["noise_sd"] = noise_sd
                            rowDict["run"] = RUN_ID

                            df = df.append(rowDict, ignore_index=True)
                            regionIndex += 1
                    except Exception as e:
                        errorDF = errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"Failed processing snr calculations", "run": RUN_ID}, ignore_index=True)
                        LOGGER.error(e)
    ipdb.set_trace()
    ### </main processing loop, needs to support multiple-runs>

    #Get the DF of the site, update values
    siteDF = df
    snrSiteMean = siteDF["region_snr"].mean()
    snrSiteSTD = siteDF["region_snr"].std()
    tfsnrSiteMean = siteDF["region_tfsnr"].mean()
    tfsnrSiteSTD = siteDF["region_tfsnr"].std()

    minSnr = float(snrSiteMean) - float(maxDeviationBelowMean)*float(snrSiteSTD)
    minTfSnr = float(tfsnrSiteMean) - float(maxDeviationBelowMean)*float(tfsnrSiteSTD)

    LOGGER.info(f"Site {siteName} values:")
    LOGGER.info(f"snr: mean = {snrSiteMean}, std = {snrSiteSTD}")
    LOGGER.info(f"tfsnr: mean = {tfsnrSiteMean}, std = {tfsnrSiteSTD}")

    for subj in siteDF["subject"].unique():
        subjSNRValues = siteDF.loc[siteDF["subject"] == subj, 'region_snr'].values
        subjTFSNRValues = siteDF.loc[siteDF["subject"] == subj, 'region_tfsnr'].values
        
        include = 1

        LOGGER.info(f"Checking criteria for {subj}, criteria: {subjSNRValues} < {minSnr} or {subjTFSNRValues} < {minTfSnr}")
        try:
            for i in range(0,len(subjSNRValues)):
                subjSNR = subjSNRValues[i]
                subjTFSNR = subjTFSNRValues[i]
                if (subjSNR < minSnr) or (subjTFSNR < minTfSnr):
                    include = 0

            LOGGER.info(f"{subj} in {siteName} with snr = {subjSNR} and tfsnr = {subjTFSNR} was {'included' if include == 1 else 'excluded'}")
        except (RuntimeError):
            LOGGER.warning(f"Subject {subj} failed to be processed, here is some useful data:")
            LOGGER.warning(f"VARIABLE TYPES = subjSNR: {type(subjSNRValues)}, subjTFSNR: {type(subjTFSNRValues)}")
            errorDF = errorDF.append({"subject":subjName, "site":siteName, "abide":abideName, "error":"failed inclusion check"}, ignore_index=True)
            include = 0

        df.loc[df["subject"] == subj,'include'] = include

    df["extreme_value"] = 0
    df.loc[df["region_tfsnr"].isin([np.inf, -np.inf]), "extreme_value"] = 1
    df.loc[df["region_snr"].isin([np.inf, -np.inf]), "extreme_value"] = 1

    addSiteToCSV(siteName, df, os.path.join(outputPath, f"{siteName}/{siteName}_snr.csv"))
    addSiteToCSV(siteName, errorDF, os.path.join(outputPath, f"{siteName}/{siteName}_snr_errors.csv"))

    if (outputGraph):
        siteDir = os.path.join(outputPath, f"{siteName}")
        computeSiteSNRStats(siteDir)

#TODO: Take derivatives directory (derivatives/abide), output directory can also be set to derivatives/abide or a local outputs. This is where subjlist is stored.
def computeBidsSNR(pathToAbideDerivatives, pathToAbideBids, maxDeviationBelowMean=STD_BELOW_MEAN,outputDir=OUTPUT_PATH, space=SPACE, spaceorig=SPACEORIG):
    LOGGER.info(f"Running SNR script for space: {space} at {pathToAbideDerivatives} and {pathToAbideBids}")
    abideName = pathToAbideDerivatives.strip("/").split("/")[-1]

    ipdb.set_trace()
    for sitePath in glob.glob(os.path.join(pathToAbideDerivatives, "*")):
        siteFolderName = sitePath.strip("/").split("/")[-1] #With derivatives
        siteNameList = siteFolderName.split("_")
        siteNameList.remove("derivatives")
        siteName = '_'.join(siteNameList) #No _derivatives
        siteBidsPath = os.path.join(pathToAbideBids, siteName)
        LOGGER.info(siteFolderName) # DK

        if DERIVATIVES_ROOT is None:
            raise ValueError(f"DERIVATIVES_ROOT not defined, needs to be set in SNRSorter.py")
        # computeSiteSNR('/Shared/klie/data/projects/fca/data/mri/derivatives/', siteBidsPath, maxDeviationBelowMean, outputDir, space, spaceorig=spaceorig)
        computeSiteSNR(DERIVATIVES_ROOT, siteBidsPath, maxDeviationBelowMean, outputDir, space, spaceorig=spaceorig)

#        computeSiteSNR(sitePath, siteBidsPath, maxDeviationBelowMean, outputDir, space, spaceorig=spaceorig) DK

def computeSiteSNRStats(siteOutputPath):
    LOGGER.info(f"Producing snr and tsnr plots for {siteOutputPath}")
    siteName = siteOutputPath.strip("/").split("/")[-1]
    csvFilePath = (os.path.join(siteOutputPath, f"{siteName}_snr.csv"))

    if (os.path.exists(csvFilePath)):
        csvDF = pd.read_csv(csvFilePath)

        snrXVar=[] #Index represents list of xvars for seed
        snrYVar=[]
        tfsnrXVar=[]
        tfsnrYVar=[] #Index represents list of yvars for seed

        LOGGER.info(csvDF["seed"].unique())
        for seed in csvDF["seed"].unique():
            seedCSV = csvDF[csvDF["seed"]==seed]

            #snrValues = (val for val in seedCSV.loc[seedCSV["seed"] == seed, "region_snr"].values)
            #tfsnrValues = (val for val in seedCSV.loc[seedCSV["seed"] == seed, "region_tfsnr"].values)

            snrXVar.append(seed)
            tfsnrXVar.append(seed)
            snrYVar.append(seedCSV.loc[seedCSV["seed"] == seed, "region_snr"].values)
            tfsnrYVar.append(seedCSV.loc[seedCSV["seed"] == seed, "region_tfsnr"].values)

        fig, axs = plt.subplots(1,2, figsize = (14,10))
        for xe, ye in zip(snrXVar, snrYVar):
            axs[0].scatter([xe] * len(ye), ye)
        axs[0].tick_params(axis = 'x', labelsize = 6, labelrotation=25)
        axs[0].set_xlabel('seed file', size = 12)
        axs[0].set_ylabel('SNR', size = 12)
        for xe, ye in zip(tfsnrXVar, tfsnrYVar):
            axs[1].scatter([xe] * len(ye), ye)
        axs[1].tick_params(axis = 'x', labelsize = 6, labelrotation=25)
        axs[1].set_xlabel('seed file', size = 12)
        axs[1].set_ylabel('TFSNR', size = 12)
        
        fig.suptitle(f"Mean values for {siteName}", fontsize=18, fontweight="bold")

        outputPNGPath = os.path.join(siteOutputPath, f"{siteName}_snr_graph.png")
        plt.savefig(outputPNGPath, dpi=200)
        plt.close()
        LOGGER.info(f"Successfully saved snr displacement figure to {outputPNGPath}")


    else:
        LOGGER.warning(f"Failed to find site's snr csv: {csvFilePath}")

def computeSNRStats(snrOutputRoot):
    for siteOutputPath in glob.glob(os.path.join(snrOutputRoot, "*")):
        computeSiteSNRStats(siteOutputPath)
        

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("derivativesPath", default=None, type=str,
        help="Path to the derivatives root folder. derivatives/abide")
    ap.add_argument("bidsPath", default=None, type=str,
        help="Path to bids root folder. bids/abide")
    ap.add_argument("-c", "--site", required=False, default="*", type=str,
        help="Choice of site from bids path")
    ap.add_argument("-s", "--space", required=False, default=SPACE, type=str,
        help="Sets the space, used for finding correct seed binaries")
    ap.add_argument("-o", "--output", required=False, default=OUTPUT_PATH, type=str,
        help="Sets the path the output CSV file is written to")
    ap.add_argument("-d", "--spaceorig", required=False, default=SPACEORIG, type=str,
        help="Sets the space, used for finding correct seed binaries")
    ap.add_argument("-l", "--subject_list", default=None, type=Path,
        help="(HACK) Path to file containing list of subjects to process.")
    ap.add_argument("--DERIVATIVES_ROOT", required=False, default=DERIVATIVES_ROOT, type=str,
        help="Temporary fix to deal with generalizing paths")



    args = vars(ap.parse_args())
    derivativesPath = args["derivativesPath"]
    bidsPath = args["bidsPath"]
    space = args["space"]
    spaceorig = args["spaceorig"]
    outputPath = args["output"]
    site = args["site"]
    subjListPath = args["subject_list"]

    if (site == "*"):
        computeBidsSNR(derivativesPath, bidsPath, STD_BELOW_MEAN, outputPath, space,spaceorig)
    else:
        siteNameParts = site.split("_")
        if ("derivatives" in siteNameParts):
            siteNameParts.remove("derivatives")
        
        rawSiteName = "_".join(siteNameParts)
        siteNameDerivatives = "_".join(siteNameParts+["derivatives"])

        #computeSiteSNR(pathToSite, pathToAbideSite, ... #DK
        #computeSiteSNR(os.path.join(derivativesPath, siteNameDerivatives), os.path.join(bidsPath, rawSiteName), STD_BELOW_MEAN, outputPath, space, True,spaceorig) DK
        computeSiteSNR(derivativesPath, bidsPath, STD_BELOW_MEAN, outputPath, space, True, spaceorig, subjListPath=subjListPath) # DK

    #TODO, loop through all the site SNR files and compute graphs
    if (site == "*"):
        computeSNRStats(os.path.join(outputPath, "snr/"))

"""
DERIVATIVES="/Shared/klie/data/projects/ama/amyAbide/data/derivatives/abide"
BIDS_PATH="/Shared/klie/data/projects/ama/amyAbide/data/bids/abide"
SPACE="T1w_res-2"
OUTPUT_DIR="/Shared/klie/data/projects/ama/code/ama_repo/sortSubjData/bash/outputs"

sortScriptPath=/Shared/klie/data/projects/ama/code/ama_repo/sortSubjData

python3 "${sortScriptPath}/SNRSorter.py" "${DERIVATIVES}" "${BIDS_PATH}" -s "${SPACE}" -o "${OUTPUT_DIR}"""
# python3 SNRSorter.py "/Volumes/klie/data/projects/ama/amyAbide/data/derivatives/abide" "/Volumes/klie/data/projects/ama/amyAbide/data/bids/abide" -c "MaxMun_b_derivatives" -s "T1w_res-2" -o '/Volumes/klie/data/projects/ama/code/ama_repo/sortSubjData/bash/outputs/snr/abide'
# python3 SNRSorter.py '/Volumes/klie/data/projects/ama/amyAbide/data/derivatives/abide2' '/Volumes/klie/data/projects/ama/amyAbide/data/bids/abide2' -c 'BNI_1_derivatives' -s 'T1w_res-2' -o '/Volumes/klie/data/projects/ama/code/ama_repo/sortSubjData/bash/outputs/snr/abide2'   
