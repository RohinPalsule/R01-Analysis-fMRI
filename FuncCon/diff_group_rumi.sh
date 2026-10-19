#!/bin/bash

#8/27/26 RL

mkdir -p results/diff_group_rumi
module load fsl/6.0.4
fslmerge -t results/diff_group_rumi/study_func_grp.nii.gz results/early_late_diff_rumi/*.nii.gz #change path to where ur late early diff files are

randomise -i results/diff_group_rumi/study_func_grp -o \
	results/diff_group_rumi/study_func_rndm \
	-m /data/opt/apps/fsl/6.0.4/data/standard/MNI152_T1_2mm_brain.nii.gz \
	-1 -x --uncorrp -n 5000

