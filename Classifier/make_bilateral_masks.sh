#!/bin/bash
module load fsl/6.0.4

fslmaths cluster1mask.nii.gz -add cluster2mask.nii.gz -bin b_clustermask.nii.gz
