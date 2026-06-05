#!/bin/bash
module load fsl/6.0.4
if [[ $# -lt 1 ]]; then
  echo Usage: ./smooth_func_scans.sh subject_num smoothing_num_mm
fi
subject=$1
smoothing=$2

func_path="/share/crsp/lab/bornstea/share/R01-fmri/fmriprep_pepolar/sub-${subject}/ses-3/func/"
output_path="smoothed_prepost/sub-${subject}/ses-3/func/"

mkdir -p $output_path

for run in {1..6}; do
    func_file=$func_path/sub-${subject}_ses-3_task-StimExposure_run-${run}_space-T1w_desc-preproc_bold.nii.gz
    mask_file=$func_path/sub-${subject}_ses-3_task-StimExposure_run-${run}_space-T1w_desc-brain_mask.nii.gz

    cp "$func_file" "$output_path/"
    cp "${func_path}"/*.tsv "$output_path/"
    cp "${func_path}"/*Stim*.json "$output_path/"
    cp "$mask_file" "$output_path/"

    smooth_susan -f 32 \
        "$output_path/$(basename $func_file)" \
        "$output_path/$(basename $mask_file)" \
        $smoothing \
	$output_path/sub-${subject}_ses-3_task-StimExposure_run-${run}_space-T1w_desc-preproc_bold.nii.gz
done

echo "All done!"
