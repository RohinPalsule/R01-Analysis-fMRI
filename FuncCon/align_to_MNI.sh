#!/bin/bash

usage() {
    echo "Usage: $0 <subid> <run_type>"
    echo ""
    echo "Arguments:"
    echo "  subid   "
    echo ""
    echo "Example:"
    echo "  $0 5159"
    exit 1
}

if [[ $# -lt 1 ]] || [[ $1 == "-h" ]] || [[ $1 == "--help" ]]; then
    usage
fi

SUBJECT_ID=$1

module load ants/2.3.5

REF=/data/opt/apps/fsl/6.0.4/data/standard/MNI152_T1_2mm_brain.nii.gz
    echo "Processing subject: $SUBJECT_ID"

    INFILE="../RSA/transformed_masks/sub-${SUBJECT_ID}/roi_t/b_gray_dilD_2mm.nii.gz"
    OUTFILE="MNI_masks/sub-${SUBJECT_ID}_b_gray_dilD_2mm.nii.gz"
    TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_from-T1w_to-MNI152NLin6Asym_mode-image_xfm.h5"
    TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mpragelowres_from-T1w_to-MNI152NLin6Asym_mode-image_xfm.h5"
    TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_from-T1w_to-MNI152NLin6Asym_mode-image_xfm.h5"
    mkdir -p MNI_masks/

    antsApplyTransforms \
        -d 3 \
        -i $INFILE \
        -r $REF \
        -o $OUTFILE \
        -t $TRANSFORM
