#!/bin/bash

module load fsl/6.0.4
EXPNAME=uh
EXPDIR=/share/crsp/lab/bornstea/share/R01-Analysis/RSA
SLDIR=${EXPDIR}/searchlight/MNI_space/

cd ${SLDIR}

#MASKS="b_hip b_hip_dil2 b_hipPlus b_hipPlus_dil2 b_mpfc b_mpfc_dil2 b_mtlc b_mtlc_dil2"
MASKS="b_gray"
COMPS="UCI_new"
CMRR_IDS="5152 5153 5155 5156 5159"

for mask in $MASKS
do
	for comparison in $COMPS	
	do
  		fslmerge -t "${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz" ${SLDIR}/*3.45mm_2mm_MNI.nii.gz
  		randomise -i ${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz -o ${SLDIR}/prepost_sl_${comparison}_${mask}_func_rndm -m $FSLDIR/data/standard/MNI152_T1_2mm_brain_mask.nii.gz -1 -x --uncorrp -n 5000
  		
	done

done
