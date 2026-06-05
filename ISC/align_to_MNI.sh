#!/bin/bash

usage() {
    echo "Usage: $0 <sublist.txt>"
    echo ""
    echo "Arguments:"
    echo "  sublist.txt   File with one subject ID per line"
    echo ""
    echo "Example:"
    echo "  $0 sublist.txt 4"
    exit 1
}

if [[ $# -lt 1 ]] || [[ $1 == "-h" ]] || [[ $1 == "--help" ]]; then
    usage
fi

SUBLIST=$1
RUNS=$2

module load ants/2.3.5

REF=/data/opt/apps/fsl/6.0.4/data/standard/MNI152_T1_2mm_brain.nii.gz
mkdir -p output/MNI_space
while read SUB; do
    SUBJECT_ID=${SUB%%_*}
    echo "Processing subject: $SUBJECT_ID with ${RUNS} runs"

    INFILE="./output/sub-${SUBJECT_ID}_isc_T1w.nii.gz"
    OUTFILE="./output/MNI_space/sub-${SUBJECT_ID}_isc_MNI152.nii.gz"
    TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"
    #TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mpragelowres_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"
   # TRANSFORM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_acq-mprage_from-T1w_to-MNI152NLin2009cAsym_mode-image_xfm.h5"
    antsApplyTransforms \
        -d 3 \
        -i $INFILE \
        -r $REF \
        -o $OUTFILE \
        -t $TRANSFORM

done < $SUBLIST
