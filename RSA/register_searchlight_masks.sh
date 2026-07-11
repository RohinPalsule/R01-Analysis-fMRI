#!/bin/bash
module load freesurfer/8.1.0
module load fsl/6.0.4
module load ants/2.3.5

MASK="${1%.nii.gz}.nii.gz"

for sub_id in $(cat sublist_initials.txt); do
    SUBJECT_ID=${sub_id%%_*}

    if [ -f "../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_acq-mprage_desc-preproc_T1w.nii.gz" ]; then
        REF="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_acq-mprage_desc-preproc_T1w.nii.gz"
        XFM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5"

    elif [ -f "../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_desc-preproc_T1w.nii.gz" ]; then
        REF="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_desc-preproc_T1w.nii.gz"
        XFM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5"

    elif [ -f "../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3__acq-mpragelowres_desc-preproc_T1w.nii.gz" ]; then
        REF="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3__acq-mpragelowres_desc-preproc_T1w.nii.gz"
        XFM="../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_from-MNI152NLin2009cAsym_to-T1w_mode-image_xfm.h5"

    else
        echo "No anatomical image found for ${SUBJECT_ID}"
        exit 1
    fi

    antsApplyTransforms \
        -d 3 \
        -i "searchlight_masks/${MASK}" \
        -r "$REF" \
        -t "$XFM" \
        -o "./transformed_masks/sub-${SUBJECT_ID}/${MASK}" \
        -n NearestNeighbor

    antsApplyTransforms \
        -d 3 \
        -i ./transformed_masks/sub-${SUBJECT_ID}/${MASK}\
        -r ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/func/sub-${SUBJECT_ID}_ses-3_task-StimExposure_run-1_space-T1w_boldref.nii.gz \
        -o ./transformed_masks/sub-${SUBJECT_ID}/roi_t/${MASK} \
        -n NearestNeighbor

done
