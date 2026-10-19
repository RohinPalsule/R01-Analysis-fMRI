#!/bin/bash

#last edited: 9/1/26 RL
#9/1/26 RL: duped it from the diff one and changed paths

mkdir -p results/seedcon_allblocks_group_rumi
module load fsl/6.0.4
fslmerge -t results/seedcon_allblocks_group_rumi/study_func_grp.nii.gz results/plot_seed_to_voxel_correlation_allblocks_rumi/*.nii.gz #change path to where files are

randomise -i results/seedcon_allblocks_group_rumi/study_func_grp -o \
	results/seedcon_allblocks_group_rumi/study_func_rndm \
	-m /data/opt/apps/fsl/6.0.4/data/standard/MNI152_T1_2mm_brain.nii.gz \
	-1 -x --uncorrp -n 5000

