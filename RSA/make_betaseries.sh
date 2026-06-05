#!/bin/bash

for sub_id in $(cat sublist_initials.txt); do
    number=${sub_id%%_*}
    func_path="./smoothed_prepost/"
    output_path="./betaseries/"
    mkdir -p betaseries/sub-${number}/ses-3/func
    cp $func_path/sub-${number}/ses-3/func/*StimExposure*.json $func_path/sub-${number}/ses-3/func/*.tsv $output_path/sub-${number}/ses-3/func
    ./make_events_tsv.sh $sub_id
    for run in {1..6}; do
        betaseries-bids \
        ./data/GW_${sub_id} \
        $func_path \
        $output_path \
        ${number} StimExposure $run T1w brain-mask \
	${func_path}/sub-${number}/ses-3/func/sub-${number}_ses-3_task-StimExposure_run-${run}_space-T1w_desc-brain_mask.nii.gz \
        node
    done
    python combineNifti.py --subject $number --block_number 3
done
