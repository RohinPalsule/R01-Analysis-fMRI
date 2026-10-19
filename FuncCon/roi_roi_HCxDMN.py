# 9/19/26 RL: created
# average the left/right ant hip connectivity with all DMN ROIs for each sub

import glob
import pandas as pd
import numpy as np
from pathlib import Path

# Find all individual subject Fisher-z matrices
files = sorted(
    glob.glob(
        "results/roi_to_roi_rumi/sub-*_roi_to_roi_fisher_z.csv"
    )
)
print(f"Found {len(files)} subjects")


# All cortical DMN ROIs
dmn_rois = [
    "LH_Par",
    "LH_pCunPCC",
    "LH_PFC",
    "LH_Temp",
    "RH_Par",
    "RH_pCunPCC",
    "RH_PFCdPFCm", #only right hemi
    "RH_PFCv",
    "RH_Temp"
]


rows = []

for file in files:

    # Read subject's Fisher-z matrix
    df = pd.read_csv(file, index_col=0)

    # Get subject ID from filename
    # Example: sub-515_roi_to_roi_fisher_z.csv -> 515
    subject = (
        Path(file).name
        .split("_")[0]
        .replace("sub-", "")
    )

    # LH anterior hippocampus x all 9 DMN ROIs
    lh_values = df.loc[
        "LH_hip_ant",
        dmn_rois
    ].values

    # RH anterior hippocampus x all 9 DMN ROIs
    rh_values = df.loc[
        "RH_hip_ant",
        dmn_rois
    ].values

    # Average Fisher-z connectivity
    lh_mean = np.nanmean(lh_values)
    rh_mean = np.nanmean(rh_values)

    rows.append({
        "subject": subject,
        "LH_aHip_DMN_mean_z": lh_mean,
        "RH_aHip_DMN_mean_z": rh_mean
    })


# Make final dataframe
out = pd.DataFrame(rows)

# Add group average as final row
out.loc[len(out)] = {
    "subject": "GROUP_MEAN",
    "LH_aHip_DMN_mean_z": out["LH_aHip_DMN_mean_z"].mean(),
    "RH_aHip_DMN_mean_z": out["RH_aHip_DMN_mean_z"].mean()
}


# Save CSV
output_file = (
    "results/roi_to_roi_rumi/"
    "aHip_DMN_subject_means.csv"
)

out.to_csv(
    output_file,
    index=False
)


# Print results so you can inspect them immediately
print("\nSubject-level aHip-DMN connectivity:")
print(out.to_string(index=False))

print(f"\nSaved: {output_file}")