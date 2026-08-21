#!/bin/bash

module load fsl/6.0.4
EXPNAME=uh
EXPDIR=/share/crsp/lab/bornstea/share/R01-Analysis/RSA
SLDIR=${EXPDIR}/searchlight/MNI_space/

cd ${SLDIR}

MASKS="b_gray"
COMP_BASE="UCI_new"

CMRR_IDS="5152 5153 5155 5156 5159"
SMS_IDS="5216 5214 5203 5169 5201"

GROUP_NAMES="CMRR SMS"

for mask in $MASKS
do
  for group in $GROUP_NAMES
  do
    comparison="${COMP_BASE}_${group}"

    if [ "$group" = "CMRR" ]; then
      ids="$CMRR_IDS"
    else
      ids="$SMS_IDS"
    fi

    # Build the list of this group's subject files, anchored on ID prefix
    files=""
    for id in $ids
    do
      files="${files} ${SLDIR}/${id}_*3.45mm_2mm_MNI.nii.gz"
    done

    fslmerge -t "${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz" ${files}

    randomise -i ${SLDIR}/prepost_sl_${comparison}_${mask}_func_grp.nii.gz \
      -o ${SLDIR}/prepost_sl_${comparison}_${mask}_func_rndm \
      -m $FSLDIR/data/standard/MNI152_T1_2mm_brain_mask.nii.gz \
      -1 -x --uncorrp -n 5000
  done
done
