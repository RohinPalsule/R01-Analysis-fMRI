#!/usr/bin/python

### import python libraries needed for the analysis ###
import os
from random import sample
import numpy as np
# from pylab import *
from mvpa2.datasets.mri import *
from mvpa2.mappers.detrend import *
from mvpa2.mappers.zscore import *
from mvpa2.clfs.svm import *
from mvpa2.generators.partition import *
from mvpa2.measures.base import *
from mvpa2.measures import *
from mvpa2.measures.searchlight import sphere_searchlight
from mvpa2.misc.stats import *
from mvpa2.base.node import *
from mvpa2.clfs.meta import *
from mvpa2.clfs.stats import *
from mvpa2.featsel.base import *
from mvpa2.featsel.helpers import *
from mvpa2.generators.permutation import *
from mvpa2.generators.base import *
from mvpa2.mappers.fx import *
from mvpa2.measures.anova import *
from mvpa2.base.dataset import *
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
### import custom searchlight function ###
from function_prepost_react2 import *
from get_graph_distances import extract_shortest_paths
### set up expriment info ###
expdir = './'
resultdir = expdir+'searchlight'

if len(sys.argv) < 5 or sys.argv[1] in ("-h", "--help"):
    print("Usage: sl_prepost_SN.py <sbj> <masktype> <runtype> <niter>")
    print("Example: python sl_prepost_SN.py 1185 gm 4 1000")
    sys.exit(1)

sbj = sys.argv[1]
masktype = sys.argv[2]
runtype = sys.argv[3]
niter = sys.argv[4]
niter = int(niter)
edges = [
    [1,2], [2,4], [4,5], [4,12], [2,3], [3,4], [3,11], [11,12],
    [3,6], [6,7], [6,9], [9,11], [7,8], [8,9], [9,10], [8,10]
]

# convert to 0-based
edges0 = [(i-1, j-1) for i, j in edges]

### masks for data to analyze ###
if masktype == 'jROIS':
	masks = ['b_hip','b_mpfc']
elif masktype == 'fsROIS':
	masks = ['b_vtc','b_lo','b_imc']
elif masktype == 'mpfcROIS':
	masks = ['l_mid_ba','r_mid_ba','l_10m','r_10m','l_10p_anterior_ba','r_10p_anterior_ba','l_10r','r_10r','l_11m','r_11m','l_14c','r_14c','l_14r','r_14r','l_24','r_24','l_25','r_25','l_32pl','r_32pl','l_posterior_ba','r_posterior_ba']
#elif masktype == 'freesurfer':
#	masks = ['aparc+aseg_gm']
elif masktype == 'func':
	masks = ['mask']
elif masktype == 'gm':
	masks = [f'b_gray_dilD_2mm']

### searchlight information ###
phase,run,node = loadtxt(expdir+f'/volinfo/prepost_volinfo.txt',unpack=1)

### directories ###
subjdir = expdir+f'/transformed_masks/sub-{sbj}/'
# betadir = expdir+f'/fmri/sub-{sbj}/model/betaseries'
betadir = expdir+f'/betaseries/sub-{sbj}/ses-3/func/'

###
for mask in masks:
	if masktype == 'jROIS':
                slmask = subjdir+'/roi_t/%s.nii.gz'%(mask)
	elif masktype == 'fsROIS':
                slmask = subjdir+'/roi_t/%s.nii.gz'%(mask)
	elif masktype == 'mpfcROIS':
                slmask = subjdir+'/roi_t/%s.nii.gz'%(mask)
	elif masktype == 'func':
                slmask = subjdir+'/roi_t/%s.nii.gz'%(mask)
	elif masktype =='gm':
		slmask = subjdir+'/roi_t/%s.nii.gz'%(mask)
	#load in betaseries data
	#ds = fmri_dataset(betadir+'/prepost.nii.gz',mask=slmask)
fname = betadir + f'/sub-{sbj}_prepost_merged_betaseries.nii.gz'
ds = fmri_dataset(fname,mask=slmask)
#labeling volinfo columns
ds.sa['phase'] = phase[:]
ds.sa['run'] = run[:]
ds.sa['node'] = node[:]
	#similarity measure
	#sl_funcs = function_prepost_react2('correlation',1,niter)
	#for testing with whole roi
	#results = sl_func(ds)
	#os.chdir("/work/03158/smn776/lonestar/PS_Pilot/results/searchlight")
	#subjoutfile = "%s_prepost_%s_%s.txt"%(sbj,comparison,mask)
	#savetxt(subjoutfile,results,fmt="%.8f")
print(ds)
print(ds.sa)
sl_func = function_prepost_react2('correlation',1,niter,ds.sa)
#run the searchlight
sl = sphere_searchlight(sl_func,radius = 3)
sl_map = sl(ds)
print(sl_map)
print("searchlight complete")
comparisons = ["edge_nonedge_diff"]
for i, name in enumerate(comparisons):
	#save out map
	subjoutfile = resultdir+'/%s_%s_runs_smoothed_prepost_sl_%s_iterations_%s_%s_2mm.nii.gz'%(sbj,runtype,niter,name,mask)
	#map2nifti(ds,sl_map.samples).to_filename(subjoutfile) <- .samples not necessary?
	map2nifti(ds,sl_map[i]).to_filename(subjoutfile)
