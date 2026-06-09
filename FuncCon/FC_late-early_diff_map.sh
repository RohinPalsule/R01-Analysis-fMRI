#!/bin/bash

mkdir -p results/late_early
fslmerge -t results/late_early/study_func_grp.nii.gz results/late_early/*.nii.gz

randomise -i results/late_early//study_func_grp -o \
	results/late_early/study_func_rndm \
	-m /Users/rohinpalsule/fsl/pkgs/fsl-data_standard-2208.0-0/data/standard/MNI152_T1_2mm_brain.nii.gz \
	-1 -x --uncorrp -n 5000
