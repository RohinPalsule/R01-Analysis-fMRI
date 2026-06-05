#!/bin/bash

module load fsl/6.0.4

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <mask> <dialation> ex. ./dilate_mask.sh b_gray 2"
    exit 1
fi

MASK=$1
DILATION=$2

for sub_id in $(cat sublist_initials.txt); do
    SUBJECT_ID=${sub_id%%_*}
    fslmaths ./transformed_masks/sub-${SUBJECT_ID}/roi_t/${MASK} -kernel sphere $DIALATION -dilD ./transformed_masks/sub-${SUBJECT_ID}/roi_t/${MASK}_dilD_${DILATION}mm
done
