# 9/7/26 RL: created
# Average ROI-to-ROI Fisher z matrices across subjects and make a group heatmap.

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# find all subject Fisher z matrices
files = glob.glob(
    "results/roi_to_roi_rumi/sub-*_roi_to_roi_fisher_z.csv"
)

print(f"Found {len(files)} subjects")

# read all matrices
matrices = []

for file in files:
    df = pd.read_csv(file, index_col=0)
    matrices.append(df.values)

# get ROI names
roi_names = df.columns

# average across subjects
group_mean = np.nanmean(
    matrices,
    axis=0
)

# make group mean Fisher z table
group_mean_df = pd.DataFrame(
    group_mean,
    index=roi_names,
    columns=roi_names
)

# save group mean Fisher z table
group_mean_df.to_csv(
    "results/roi_to_roi_rumi/group_mean_fisher_z.csv"
)

print("Saved group mean Fisher z matrix")

# make heatmap
fig, ax = plt.subplots(figsize=(12, 10))

im = ax.imshow(
    group_mean,
    cmap="coolwarm",
    vmin=-1,
    vmax=1
)

# add Fisher z value to each cell
for i in range(len(roi_names)):
    for j in range(len(roi_names)):
        if not np.isnan(group_mean[i, j]):
            ax.text(
                j, i,
                f"{group_mean[i, j]:.2f}",
                ha="center",
                va="center",
                fontsize=7
            )

ax.set_xticks(range(len(roi_names)))
ax.set_xticklabels(roi_names, rotation=90)

ax.set_yticks(range(len(roi_names)))
ax.set_yticklabels(roi_names)

plt.colorbar(
    im,
    label="Mean Fisher z"
)

ax.set_title(
    f"Group Mean ROI-to-ROI Connectivity (N={len(files)})"
)

plt.tight_layout()

plt.savefig(
    "results/roi_to_roi_rumi/group_mean_heatmap.png",
    dpi=300
)

plt.close()

print("Saved group mean heatmap")
print("Done!")