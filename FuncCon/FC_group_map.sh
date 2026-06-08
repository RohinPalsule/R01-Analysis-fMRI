#!/bin/bash

mkdir -p results/group_maps
fslmerge -t results/group_maps/study_func_grp.nii.gz results/plot_seed_to_voxel_correlation/*.nii.gz

randomise -i results/group_maps/study_func_grp -o \
	results/group_maps/study_func_rndm \
	-m /Users/rohinpalsule/fsl/pkgs/fsl-data_standard-2208.0-0/data/standard/MNI152_T1_2mm_brain.nii.gz \
	-1 -x --uncorrp -n 5000
