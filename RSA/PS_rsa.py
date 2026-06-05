#!/usr/bin/env python

### import python libraries needed for the analysis ###
from mvpa2.misc.fsl.base import *
from mvpa2.datasets.mri import fmri_dataset
from mvpa2.measures.rsa import PDist
import numpy as N
import nibabel
import scipy.stats
from scipy.stats.mstats import zscore
from scipy.ndimage import convolve1d
from scipy.sparse import spdiags
from scipy.linalg import toeplitz
from mvpa2.datasets.mri import *
import os
import sys
from copy import copy

### set up expriment info ###
expdir = './'
resultdir = expdir+'searchlight'
sbj = sys.argv[1]
masktype = sys.argv[2]

### masks for data to analyze ###
if masktype == 'jROIS':
	masks = ['l_hip_ant','r_hip_ant','l_hip_body','r_hip_body','l_hip_tail','r_hip_tail','l_hip','r_hip','l_phc', 'r_phc']
elif masktype == 'fsROIS':
	masks = ['l_erc','r_erc','l_lo','r_lo','l_tpo','r_tpo','l_put','r_put','l_hip','r_hip']
elif masktype == 'mpfcROIS':
	masks = ['l_mid_ba','r_mid_ba','l_10m','r_10m','l_10p_anterior_ba','r_10p_anterior_ba','l_10r','r_10r','l_11m','r_11m','l_14c','r_14c','l_14r','r_14r','l_24','r_24','l_25','r_25','l_32pl','r_32pl','l_posterior_ba','r_posterior_ba']
elif masktype == 'grpROI':
	masks = ['grp_sl_bli_b_gray_p05_863_mask']
	
### directories ###
subjdir = expdir+f'/transformed_masks/sub-{sbj}/'
# betadir = expdir+f'/fmri/sub-{sbj}/model/betaseries'
betadir = expdir+f'/betaseries/sub-{sbj}/ses-3/func/'

### rsa design and data to analyze
rsafx = PDist(square=True)

betadata = betadir+f'/sub-{sbj}_prepost_merged_betaseries.nii.gz'
print(betadata)
print(subjdir)
### runs ###
for mask in masks:
	
		#mask
		if masktype == 'jROIS':
			rsamask = subjdir+'/anatomy/bbreg/data/jacksonROIS/%s.nii.gz'%(mask)
		elif masktype == 'fsROIS':
			rsamask = subjdir+'/roi_t/%s.nii.gz'%(mask)
		elif masktype == 'mpfcROIS':
			rsamask = subjdir+'/../pfc_drawn_MS/%s.nii.gz'%(mask)
		elif masktype == 'grpROI':
			rsamask = subjdir+'/anatomy/bbreg/data/grpROI/%s.nii.gz'%(mask)

		#load in the data
		ds = fmri_dataset(betadata, mask=rsamask)
		rs = rsafx(ds)

		#save as text file
		#subjoutfile = "%s_prepost_%s.txt"%(sbj,mask)
		subjoutfile = "./ROI_RSA/%s_prepost_3_runs_%s.txt"%(sbj,mask)
	
		# convert to similairty (1-rs) before output
		N.savetxt(subjoutfile,1-rs.samples,fmt="%.8f")
