#!/bin/bash
type=$1

fslmerge -t study_func_grp_${type}.nii.gz *${type}*MNI.nii.gz

randomise -i study_func_grp_${type} -o \
	study_func_rndm_${type} \
	-m /Users/rohinpalsule/fsl/pkgs/fsl-data_standard-2208.0-0/data/standard/MNI152_T1_2mm_brain.nii.gz \
	-1 -x --uncorrp -n 5000
