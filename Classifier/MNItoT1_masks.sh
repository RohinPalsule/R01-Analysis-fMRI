#!/bin/bash

# these rois are in mni space; this script transforms them into native space
# mni space --> native anatomical space --> native functional space

module load ants/2.3.5
module load fsl/6.0.4

EXPDIR=.
SUBS=$1

MASKDIR=$EXPDIR/cluster_maps/sub-$SUBS

mkdir -p $MASKDIR/transformed
OUTDIR=$MASKDIR/transformed

for SUBNUM in $SUBS; do

  SUBNAME=sub-$SUBNUM
  BOLDDIR=/share/crsp/lab/bornstea/share/R01-fmri/fmriprep_pepolar/

  for MASK in "$MASKDIR"/*.nii*; do

    BASENAME=$(basename "$MASK")
    
    echo "Processing $BASENAME ..."

    # WarpImageMultiTransform 3 \
    #   $MASKDIR/overlap_${MASK}_mask.nii.gz \
    #   $OUTDIR/overlap_${MASK}.nii.gz -R $BOLDDIR/refvol.nii.gz \
    #   $TRANSDIR/brain2${REFRUN}unwarp_Affine.txt \
    #   -i $TRANSDIR/brain2${TEMPLATE}_Affine.txt \
    #   $TRANSDIR/brain2${TEMPLATE}_InverseWarp.nii.gz --use-NN


      # -t $BOLDDIR/${SUBNAME}_ses-2_task-Localizer_run-1_from-T1w_to-scanner_mode-image_xfm.txt \
    antsApplyTransforms -d 3 \
      -i $MASK \
      -o "$OUTDIR/${BASENAME%.nii*}_transformed.nii.gz"  \
      -r $BOLDDIR/${SUBNAME}/ses-2/func/${SUBNAME}_ses-2_task-Localizer_run-1_space-T1w_boldref.nii.gz \
      -t $BOLDDIR/${SUBNAME}/anat/${SUBNAME}_acq-mprage_from-MNI152NLin6Asym_to-T1w_mode-image_xfm.h5 \
      -n NearestNeighbor

    fslmaths "$OUTDIR/${BASENAME%.nii*}_transformed.nii.gz" -kernel sphere 3.45 -dilD "$OUTDIR/${BASENAME%.nii*}_transformed_dilD_345.nii.gz"
  done

done
