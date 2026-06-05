#!/usr/bin/env python

## Import all python libraries we need

from numpy import *
from pylab import *
from scipy.io import *
#from mvpa2.datasets.mri import *
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
from mvpa2.datasets.mri import *
from random import sample
import os
import sys
print(os.getcwd())
expdir = os.getcwd()+'/'
resultdir = expdir+'/results/' # change based on classifier type
#resultdir = expdir+'/results_classification_func_WB_sl_post' # WB_func
#needs to be run by participant because localizer block order is participant-specific
#subjects = [102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,122,125,126,127,128]
subjects = [5152]
#masks = ['brain_GMmask']
# masks = ['l_vtc','l_imc','l_lo','l_phc','r_vtc','r_imc','r_lo','r_phc','b_vtc','b_imc','b_lo','b_phc','b_vtc','b_imc','b_lo','b_phc','l_tpo','r_tpo','b_tpo'] 

os.chdir(resultdir)

for sbj in subjects: # because you're inputting a number it wants to parse it if you use a for loop

	## Read in volume information
	# phase
	# runs: what run the volume is from
	# training: what env the volume is from
	# artist: object number
	# painting

	volinfo = expdir+'volinfo/volinfo.txt'
	runs,stim_type = loadtxt(volinfo,unpack=1)

	#volinfo_loc = expdir+'/batch/misc/beta_chunks_classify_loc_tsTRs_%s.txt'%(sbj)
	#runs_loc,env_loc,trl_loc = loadtxt(volinfo_loc,unpack=1)

	subjdir = expdir+'/sub-%s'%(sbj)
	
	betadir = subjdir+'/merged_betaseries/'
	maskdir = subjdir + '/masks/'
	#locdir = subjdir+'/model/localizer_betaseries/betaseries/'
	masks = [f for f in os.listdir(maskdir) if f.endswith('.nii.gz')]
	for mask in masks:

		if mask == 'brain_GMmask':
			classmask = subjdir+'/anatomy/bbreg/data/jacksonROIS/%s.nii.gz'%(mask)
		else:
			#classmask = expdir+'/results_classification_WB_sl/clusters/significantClusters/%s_%s.nii.gz'%(sbj,mask) # WB reactivation clusters
			classmask = maskdir+'/%s'%(mask)
			#classmask = subjdir+'/anatomy/bbreg/data/freesurferROIS/b_%s.nii.gz'%(mask)
			#classmask = expdir+'/results_classification/clusters/nativePHC/%s_%s.nii.gz'%(sbj,mask) # PHC ROIs
		
		# localizer (BOLD) timeseries data   
		#locfuncs = [bolddata+'/localizer_1_sm.nii.gz',bolddata+'/localizer_2_sm.nii.gz',bolddata+'/localizer_3_sm.nii.gz'] 
		#locds = fmri_dataset(locfuncs,mask=classmask,chunks=runs_loc,targets=env_loc)    
		   
		# post betaseries data 
		funcs = [betadir+f'/sub-{sbj}_merged_betaseries.nii.gz'] 
		psds = fmri_dataset(funcs,mask=classmask,chunks=runs,targets=stim_type)   
		# psds.sa['phase'] = phase
		# psds.sa['schedule'] = schedule
		 
		## Remove linear trends (note: setting chunks_attr to runs means
		## detrending will occur within runs)
		#poly_detrend(locds,polyord=1,chunks_attr='chunks')
		poly_detrend(psds,polyord=1,chunks_attr='chunks')
		
		## Remove null events (volumes labeled with non-target env)
		# psds = psds[psds.sa.phase != 1] # keep TRs of interest (remove pre)
		# psds = psds[psds.sa.schedule != 2] # keep TRs of interest (remove interleaved)
		
		## Z-score data within runs
		#zscore(locds,chunks_attr='chunks')
		zscore(psds,chunks_attr='chunks')
		   
		## Set up classification scheme
		# linear SVM classifier
		clf = LinearCSVMC(probability=1,enable_ca=['probabilities'])
		
		## Only use the top 1000 Fzs as classifer
		# This classifier will include only the top 1000 classifiers, so clf line is commented below.
		from mvpa2.featsel.base import SensitivityBasedFeatureSelection
		from mvpa2.clfs.meta import FeatureSelectionClassifier
		from mvpa2.measures.anova import OneWayAnova
		from mvpa2.featsel.helpers import FixedNElementTailSelector
		fsel = SensitivityBasedFeatureSelection(OneWayAnova(),FixedNElementTailSelector(int(1000), mode='select',tail='upper'))
		clf = FeatureSelectionClassifier(clf, fsel)
		# partition the data by runs
		ptf = NFoldPartitioner(attr='chunks')
		# cross validate the classifier using the partitioner
		# note: test performance stats are enabled (enable_ca=['stats'])
		cv = CrossValidation(clf,ptf,enable_ca=['stats'])

		## Run the cross validation of the classifier
		#results = cv(locds)
		results = cv(psds)
		#print cv.ca.stats.as_string(description=True)
		#cvdetails = "%s_cv_details_%s.txt"%(sbj,mask)
		#with open(cvdetails, 'w') as f:
		#	f.write(cv.ca.stats.as_string(description=True))
		
		## Now train and predict
		# linear SVM classifier
		#clf = LinearCSVMC(probability=1,enable_ca=['probabilities'])
		# train on localizer dataset
		#clf.train(locds)
		clf.train(psds)
		label = clf.predict(psds)
		#label = clf.predict(postdataset)
		# import pdb
		#pdb.set_trace()
		prob = [p[1].values() for p in clf.clf.ca.probabilities]
		prob = array([list(p[1].values()) for p in clf.clf.ca.probabilities], dtype=float)
		## Cross-validation accuracy
		acc1 = 1-mean(results) # cross validation output error term

		# save accuracy to text file
		cvoutfile = "%s_cv_betas_%s.txt"%(sbj,mask)
		labeloutfile = "%s_label_betas_%s.txt"%(sbj,mask)
		proboutfile = "%s_prob_betas_%s.txt"%(sbj,mask)
		savetxt(cvoutfile,[acc1],fmt='%.6f')
		savetxt(labeloutfile,label,fmt='%.8f')
		print(type(prob))
		print(prob[:5])  # preview first 5 entries
		savetxt(proboutfile,prob,fmt='%.8f')
