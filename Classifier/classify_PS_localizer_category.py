#!/usr/bin/python
#classify_paintings_localizer_category.py

from numpy import *
from pylab import *
from scipy.io import *
from scipy import stats #NV added this on 6/10/19 as a work-around for confusion matrix issue
stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df) #continuing work-around
from mvpa2.datasets.mri import *
from mvpa2.mappers.detrend import *
from mvpa2.mappers.zscore import *
from mvpa2.clfs.svm import *
from mvpa2.generators.partition import *
from mvpa2.measures.base import *
from mvpa2.measures import *
from mvpa2.measures.searchlight import *
from mvpa2.misc.stats import *
from mvpa2.mappers.fx import *
from mvpa2.generators.permutation import *
from mvpa2.clfs.stats import *
from mvpa2.generators.base import *
from mvpa2.base.node import *
from random import sample
import os
import sys

expdir = './'

subjects = [5152]
#masks = ['jacksonROIS/b_phc','jacksonROIS/b_prc']

for sbj in subjects: # because you're inputting a number it wants to parse it if you use a for loop

	## Read in volume information
	# phase
	# runs: what run the volume is from
	# training: what env the volume is from
	# artist: object number
	# painting

	volinfo = expdir+f'/volinfo/classifier/sub-{sbj}/{sbj}_volinfo_3TR.txt'
	runs,stim_types,TRs = loadtxt(volinfo,unpack=1)

	subjdir = expdir+'/sub-%s'%(sbj)

	maskdir = expdir + f'/cluster_maps/sub-{sbj}/transformed/dilD_345/b_masks/'

	boldir = expdir + f'/sub-{sbj}/smoothed_localizer/'

	resultsdir = expdir + '/results/localizer/2mm_smoothed/3TR_HRF'

	# Need to try smoothing 4mm and compare accuracy

	masks = [f for f in os.listdir(maskdir) if f.endswith('.nii.gz')]
	for mask in masks:
		classmask = maskdir+'/%s'%(mask)

		# CHANGE TO SMOOTHED FUNC DATA
		locfuncs = [boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-1.nii.gz',
			  		boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-2.nii.gz',
					boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-3.nii.gz']


		locds = fmri_dataset(locfuncs,mask=classmask,chunks=runs,targets=stim_types)

		poly_detrend(locds,polyord=1,chunks_attr='chunks')
		locds = locds[locds.targets != 0] # drop empty points
		zscore(locds,chunks_attr='chunks')

		clf = LinearCSVMC(probability=1,enable_ca=['probabilities'])
		ptf = NFoldPartitioner(attr='chunks')
		cv = CrossValidation(clf,ptf,enable_ca=['stats'])
		results = cv(locds)
		print(cv.ca.stats.as_string(description=True))

		cvdetails = "%s/%s_cv_details_%s.txt"%(resultsdir,sbj,mask.split('_mask_transformed_dilD_345.nii.gz')[0]) # this might not split properly if naming differently
		with open(cvdetails, 'w') as f:
			f.write(cv.ca.stats.as_string(description=True))

