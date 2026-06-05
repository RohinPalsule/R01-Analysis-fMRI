#!/bin/bash
module load fsl/6.0.4
if [[ $# -lt 1 ]]; then
  echo Usage: ./smooth_phase2.sh subject_num smoothing_num_mm
fi
subject=$1
smoothing=$2
#func_path="../../R01-fmri/fmriprep_pepolar/sub-${subject}/ses-2/func/"
func_path="fmriprep_pepolar/sub-${subject}/ses-2/func/"
output_path="sub-${subject}/smoothed_phase2/"

mkdir -p $output_path

func_file=$func_path/sub-${subject}_ses-2_task-ChoiceCB_space-T1w_desc-preproc_bold.nii.gz
mask_file=$func_path/sub-${subject}_ses-2_task-ChoiceCB_space-T1w_desc-brain_mask.nii.gz

cp "$func_file" "$output_path/"
cp "$mask_file" "$output_path/"

smooth_susan -f 32 \
	"$output_path/$(basename $func_file)" \
        "$output_path/$(basename $mask_file)" \
        $smoothing \
	$output_path/sub-${subject}_task-ChoiceCB_${smoothing}mm_hpf32.nii.gz


