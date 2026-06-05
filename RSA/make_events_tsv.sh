#!/bin/bash

# Check for two arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <subject_id> (###_AA)"
    exit 1
fi

SUBJECT_ID=$1

for infile in ./data/GW_${SUBJECT_ID}/GW_*_prepost_*.txt; do
    echo "Processing $infile..."

    # Example filename: GW_1202_JR_prepost_1_2.txt
    fname=$(basename "$infile" .txt)

    subj=$(echo "$fname" | cut -d'_' -f2)      # 1202
    task=$(echo "$fname" | cut -d'_' -f4)      # prepost
    prepost=$(echo "$fname"  | cut -d'_' -f5)      # 1
    run=$(echo "$fname"  | cut -d'_' -f6)      # 2

    [ "$prepost" -eq 1 ] && add_val=0
    [ "$prepost" -eq 2 ] && add_val=3
    run_offset=$((add_val + run))
    # Build BIDS-compliant output filename
    outfile="./data/GW_${SUBJECT_ID}/sub-${subj}_ses-3_task-StimExposure_run-${run_offset}_events.tsv"

    # Write header
    echo -e "onset\tduration\tnode\tresponse_time\taccuracy" > "$outfile"

    # Convert columns: onsent, rt, acc, item
    awk 'NR>1 && $5 != "NaN" {print $4 "\t1\t" $5 "\t" $10 "\t" $9}' "$infile" >> "$outfile"

    echo "Saved $outfile"
done
