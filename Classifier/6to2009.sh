in=$1
ref=$2

# split off extension (handles .nii.gz and .nii)
case "$in" in
  *.nii.gz) base=${in%.nii.gz}; ext=.nii.gz ;;
  *.nii)    base=${in%.nii};    ext=.nii ;;
  *)        echo "Unrecognized extension: $in" >&2; exit 1 ;;
esac

antsApplyTransforms -d 3 \
  -i "$in" \
  -r "$ref" \
  -t tpl-MNI152NLin2009cAsym_from-MNI152NLin6Asym_mode-image_xfm.h5 \
  -n NearestNeighbor \
  -o "${base}_2009${ext}"
