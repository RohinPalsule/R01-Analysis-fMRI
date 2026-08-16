#!/bin/bash
threshold=$1
module load fsl/6.0.4
echo cluster maps for $threshold

if [ -z "$1" ]; then
    echo "Error: No thresholf provided."
    echo "Usage: $0 <threshold (0.95)>"
    exit 1
fi

inpath="/share/crsp/lab/bornstea/share/R01-Analysis/RSA/searchlight/MNI_space/"

fslmaths ${inpath}/prepost_sl_UCI_new_b_gray_func_rndm_vox_p_tstat1.nii.gz \
-thr ${threshold} \
-bin ${inpath}/thresh_bin_group_map_p_${threshold}.nii.gz

cluster \
  --in=${inpath}/thresh_bin_group_map_p_${threshold}.nii.gz \
  --thresh=0.5 \
  --minextent=10 \
  --oindex=${inpath}/group_cluster_index_p_${threshold}.nii.gz \
  --osize=${inpath}/group_cluster_size_p_${threshold}.nii.gz \
  > ${inpath}/cluster_report_p_${threshold}.txt

cat ${inpath}/cluster_report_p_${threshold}.txt
