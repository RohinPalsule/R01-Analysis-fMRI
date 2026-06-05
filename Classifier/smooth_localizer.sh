#!/bin/bash
module load fsl/6.0.4
if [[ $# -lt 1 ]]; then
  echo Usage: ./smooth_func_scans.sh subject_num smoothing_num_mm
fi
subject=$1
smoothing=$2

func_path="../../R01-fmri/fmriprep_pepolar/sub-${subject}/ses-2/func/"
output_path="sub-${subject}/smoothed_localizer/"

mkdir -p $output_path

for run in {1..3}; do
    func_file=$func_path/sub-${subject}_ses-2_task-Localizer_run-${run}_space-T1w_desc-preproc_bold.nii.gz
    mask_file=$func_path/sub-${subject}_ses-2_task-Localizer_run-${run}_space-T1w_desc-brain_mask.nii.gz

    cp "$func_file" "$output_path/"
    cp "$mask_file" "$output_path/"

    smooth_susan -f 32 \
        "$output_path/$(basename $func_file)" \
        "$output_path/$(basename $mask_file)" \
        $smoothing \
	$output_path/sub-${subject}_task-Localizer_${smoothing}mm_hpf32_run-${run}.nii.gz
done


