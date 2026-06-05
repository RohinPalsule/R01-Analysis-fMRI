#!/usr/bin/python

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
resultdir = expdir+'/results/prepost/' # change based on classifier type

subjects = [5160]
#masks = ['jacksonROIS/b_phc','jacksonROIS/b_prc']
#os.chdir(resultdir)

for sbj in subjects: # because you're inputting a number it wants to parse it if you use a for loop

	## Read in volume information
	# phase
	# runs: what run the volume is from
	# training: what env the volume is from
	# artist: object number
	# painting

	loc_volinfo = expdir+f'/volinfo/classifier/sub-{sbj}/{sbj}_volinfo_3TR.txt'
	runs,stim_types,TRs = loadtxt(loc_volinfo,unpack=1)

	subjdir = expdir+'/sub-%s'%(sbj)

	maskdir = expdir  + f'/cluster_maps/sub-{sbj}/transformed/dilD_345/'

	boldir = expdir + f'/sub-{sbj}/smoothed_localizer/'

	resultsdir = expdir + '/results/prepost/pre_validation/'

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

		############################ PRE POST DATA ############################

		pp_volinfo = expdir+f'/volinfo/prepost/prepost_cv_volinfo.txt'
		phase,pp_runs,scene,stim_type = loadtxt(pp_volinfo,unpack=1)

		betadir = subjdir + "/merged_betaseries/"
		prepostfuncs = [betadir + f'/sub-{sbj}_prepost_merged_betaseries.nii.gz']

		pp_ds = fmri_dataset(prepostfuncs, chunks=pp_runs, mask=classmask, targets=stim_type)
		pp_ds.sa.phase = phase
		print(pp_ds)
		print('test')
		print(prepostfuncs)
		### PRE
		pre_ds = pp_ds[pp_ds.sa.phase == 1]
		print(pre_ds)
		poly_detrend(pre_ds, polyord=1, chunks_attr='chunks')
		zscore(pre_ds, chunks_attr='chunks')

		### POST
		post_ds = pp_ds[pp_ds.sa.phase == 2]
		print('post made!')

		poly_detrend(post_ds, polyord=1, chunks_attr='chunks')
		zscore(post_ds, chunks_attr='chunks')

		############################ PRE POST DATA ############################
		print("training started")
		clf.train(pre_ds)
		print('trained!')
		#pre_pred = clf.predict(pre_ds)
		#prefile = "results/prepost/b_masks/%s_label_betas_pre_%s.txt"%(sbj,mask.split('_mask_transformed_dilD_345.nii.gz')[0])
		#savetxt(prefile,pre_pred,fmt='%.8f')
		#print('prefile saved!')

		#post_pred = clf.predict(post_ds)
		#postfile = "results/prepost/b_masks/%s_label_betas_post_%s.txt"%(sbj,mask.split('_mask_transformed_dilD_345.nii.gz')[0])
		#savetxt(postfile,post_pred,fmt='%.8f')

		cv = CrossValidation(clf,ptf,enable_ca=['stats'])
		results = cv(pre_ds)
		print(cv.ca.stats.as_string(description=True))

		cvdetails = "%s/%s_cv_details_pp_%s.txt"%(resultsdir,sbj,mask.split('_mask_transformed_dilD_345.nii.gz')[0]) # this might not split properly if naming differently
		with open(cvdetails, 'w') as f:
		 	f.write(cv.ca.stats.as_string(description=True))

