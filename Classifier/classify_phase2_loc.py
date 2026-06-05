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
#TR=int(sys.argv[1])
subjects = [5152]
cond="raw"

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

	maskdir = expdir + f'/cluster_maps/sub-{sbj}/transformed/dilD_345/b_masks/'

	loc_boldir = expdir + f'/sub-{sbj}/smoothed_localizer/'

	p2_boldir = expdir + f'/sub-{sbj}/smoothed_phase2/'
	# Need to try smoothing 4mm and compare accuracy

	masks = [f for f in os.listdir(maskdir) if f.endswith('.nii.gz')]
	for mask in masks:
		classmask = maskdir+'/%s'%(mask)

		# CHANGE TO SMOOTHED FUNC DATA
		locfuncs = [loc_boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-1.nii.gz',
			  		loc_boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-2.nii.gz',
					loc_boldir + f'/sub-{sbj}_task-Localizer_2mm_hpf32_run-3.nii.gz']


		locds = fmri_dataset(locfuncs,mask=classmask,chunks=runs,targets=stim_types)

		poly_detrend(locds,polyord=1,chunks_attr='chunks')
		locds = locds[locds.targets != 0] # drop empty points
		zscore(locds,chunks_attr='chunks')

		clf = LinearCSVMC(probability=1,enable_ca=['probabilities'])
		#ptf = NFoldPartitioner(attr='chunks')

		############################ PHASE 2  DATA ############################

		p2_volinfo = expdir+f'/volinfo/phase2/sub-{sbj}/{sbj}_phase2_{cond}_volinfo.txt'
		context,category,TR_window,TRs = loadtxt(p2_volinfo,unpack=1)

		p2funcs = [p2_boldir + f'/sub-{sbj}_task-ChoiceCB_2mm_hpf32.nii.gz']
		p2_ds = fmri_dataset(p2funcs, mask=classmask, targets=category)
		#p2_ds = p2_ds[p2_ds.targets != 0] # drop empty points
		p2_ds.sa['window'] = TR_window
		p2_ds.sa['chunks'] = np.zeros(len(p2_ds), dtype=int)
		print(type(p2_ds.sa['window'].value))
		print(p2_ds.sa['window'].value.shape)
		p2_ds = p2_ds[p2_ds.sa['window'].value != 100]
		#poly_detrend(pre_ds, polyord=1, chunks_attr='chunks')
		zscore(p2_ds,chunks_attr='chunks')

		############################ PRE POST DATA ############################
		print("training started")
		clf.train(locds)
		print('trained!')
		pre_pred = clf.predict(p2_ds)

		print(type(clf))
		print(clf.ca)
		prob = [p[1].values() for p in clf.ca.probabilities]
		prob = array([list(p[1].values()) for p in clf.ca.probabilities], dtype=float)

		prefile = f"results/{sbj}_{cond}_label_betas_p2_{mask.split('_mask_transformed_dilD_345.nii.gz')[0]}.txt"
		savetxt(prefile,pre_pred,fmt='%.8f')
		print('prefile saved!')

		base = mask.split('_mask_transformed_dilD_345.nii.gz')[0]
		savetxt(f"results/{sbj}_{cond}_prob_betas_p2_{base}.txt",prob,fmt='%.8f')

		# cv = CrossValidation(clf,ptf,enable_ca=['stats'])
		# results = cv(locds)
		# print(cv.ca.stats.as_string(description=True))

		# cvdetails = "%s/%s_cv_details_%s.txt"%(resultsdir,sbj,mask.split('cb_')[1].split('_t3')[0]) # this might not split properly if naming differently
		# with open(cvdetails, 'w') as f:
		# 	f.write(cv.ca.stats.as_string(description=True))
