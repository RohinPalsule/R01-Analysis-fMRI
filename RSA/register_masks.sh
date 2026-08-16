#!/bin/bash
module load freesurfer/8.1.0
module load fsl/6.0.4
for sub_id in $(cat sublist_initials.txt); do
    SUBJECT_ID=${sub_id%%_*}
    python convert_freesurfer.py sub-${SUBJECT_ID} --study-dir '../../R01-fmri/fmriprep_pepolar/sourcedata/freesurfer'
    module load ants/2.3.5

    mkdir -p transformed_masks/
    mkdir -p transformed_masks/sub-${SUBJECT_ID}/
    mkdir -p transformed_masks/sub-${SUBJECT_ID}/roi_t/

    antsApplyTransforms \
    -d 3 \
    -i ../../R01-fmri/fmriprep_pepolar/sourcedata/freesurfer/sub-${SUBJECT_ID}/mri/aparc+aseg.nii.gz \
    -r ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_acq-mprage_desc-preproc_T1w.nii.gz \
    -t ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/anat/sub-${SUBJECT_ID}_acq-mprage_from-fsnative_to-T1w_mode-image_xfm.txt \
    -o ./transformed_masks/sub-${SUBJECT_ID}/aparc+aseg_in_T1w.nii.gz \
    -n NearestNeighbor

#    antsApplyTransforms \
#    -d 3 \
#    -i ../../R01-fmri/fmriprep_pepolar/sourcedata/freesurfer/sub-${SUBJECT_ID}/mri/aparc+aseg.nii.gz \
#    -r ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_desc-preproc_T1w.nii.gz \
#    -t ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/anat/sub-${SUBJECT_ID}_ses-3_acq-mprage_from-fsnative_to-T1w_mode-image_xfm.txt \
#    -o ./transformed_masks/sub-${SUBJECT_ID}/aparc+aseg_in_T1w.nii.gz \
#    -n NearestNeighbor

    antsApplyTransforms \
    -d 3 \
    -i ./transformed_masks/sub-${SUBJECT_ID}/aparc+aseg_in_T1w.nii.gz \
    -r ../../R01-fmri/fmriprep_pepolar/sub-${SUBJECT_ID}/ses-3/func/sub-${SUBJECT_ID}_ses-3_task-StimExposure_run-1_space-T1w_boldref.nii.gz \
    -o ./transformed_masks/sub-${SUBJECT_ID}/aparc+aseg_in_funcT1.nii.gz \
    -n NearestNeighbor

    ./roi_freesurfer.sh ./transformed_masks/sub-${SUBJECT_ID}/aparc+aseg_in_funcT1.nii.gz ./transformed_masks/sub-${SUBJECT_ID}/roi_t
done
