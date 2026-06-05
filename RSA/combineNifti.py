#!/usr/bin/env python3
import nibabel as nib
import numpy as np
import argparse


parser = argparse.ArgumentParser(description="Process RSA output paths.")
parser.add_argument("--subject", type=int, required=True,
                    help="Subject ID (e.g., 1185)")
parser.add_argument("--block_number", type=int, default=4,
                    help="Run number (default: 4)")
parser.add_argument("--base_path", type=str, default="./betaseries/",
                    help="Base directory for betaseries outputs (default: /share/crsp/lab/bornstea/share/graphwalk_aging_project/analysis/betaseries-bids)")

args = parser.parse_args()

# Construct path using arguments
path = f"{args.base_path}/sub-{args.subject}/ses-3/func/"

files = []
runs = f'_{args.block_number}_runs'

for i in range(1,7):
	files.append(f'{path}sub-{args.subject}_ses-3_task-StimExposure_run-{i}_space-T1w_label-brain-mask_betaseries.nii.gz')
imgs = [nib.load(f) for f in files]
data = [img.get_fdata() for img in imgs]

# stack along time dimension (axis=3)
merged = np.concatenate(data, axis=3)

merged_img = nib.Nifti1Image(merged, imgs[0].affine, imgs[0].header)
nib.save(merged_img, f"{path}sub-{args.subject}_prepost_merged_betaseries.nii.gz")
