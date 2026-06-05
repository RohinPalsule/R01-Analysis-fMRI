#!/bin/bash

for sub_id in $(cat sublist_initials.txt); do
    number=${sub_id%%_*}
    func_path="./sub-${number}/smoothed_prepost/"
    output_path="./sub-${number}/betaseries/"
    cp $func_path/ses-1/func/*StimExposure*.json $func_path/ses-1/func/*.tsv $output_path
    ./make_events_tsv.sh $sub_id
    for run in {1..6}; do
        betaseries-bids \
        ./data/CB_${sub_id} \
        $func_path \
        $output_path \
        ${number} StimExposure $run T1w brain-mask \
	../../R01-fmri/fmriprep_pepolar/sub-${number}/ses-1/func/sub-${number}_ses-1_task-StimExposure_run-${run}_space-T1w_desc-brain_mask.nii.gz \
        node
    done
    python combineNifti.py --subject $number --block_number 3
done
