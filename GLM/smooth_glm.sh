#!/bin/bash

# Usage:
# ./batch_smooth.sh /path/to/input_dir /path/to/output_dir 6

# Should not take more than 1-3 mins

indir=$1
outdir=$2
fwhm=$3

if [[ -z "$indir" || -z "$outdir" || -z "$fwhm" ]]; then
    echo "Usage: $0 <input_dir> <output_dir> <fwhm_mm>"
    exit 1
fi

mkdir -p "$outdir"

# Convert FWHM → sigma
sigma=$(python3 -c "print($fwhm / 2.355)")

echo "FWHM: $fwhm mm"
echo "Sigma: $sigma mm"

for file in "$indir"/*_ses-3_task-StudyGW_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz; do
(
    base=$(basename "$file" .nii.gz)
    out="$outdir/${base}_sm${fwhm}.nii"
    fslmaths "$file" -s "$sigma" "$out"
) &
done

wait

echo Smoothed functional data at ${fwhm}mm
