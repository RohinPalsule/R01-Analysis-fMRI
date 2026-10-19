#RL 8/27/26

import nibabel as nib
from nilearn import image,datasets,plotting
import glob
import os
import sys

in_path = "results/plot_seed_to_voxel_correlation_rumi" # change if needed
out_path = "results/early_late_diff_rumi" # make a new subdirectory if you want to put these somewhere else

def get_diff_z(id):
    z_maps = sorted( #sort alphabetically so its always early then late
        glob.glob(
            os.path.join(
                in_path, f"sub-{id}_Hippocampus_seed_*_correlation_z.nii.gz" # Make sure the files start like this, if not change the identifier
            )
        )
    )
    if len(z_maps) != 2:
        raise ValueError(f"Expected 2 maps for subject {id}, found {len(z_maps)}: {z_maps}")
    late_minus_early = image.math_img(
        "img1 - img2", #late – early
        img1=z_maps[1],
        img2=z_maps[0]
    )

    late_minus_early.to_filename(
        os.path.join(out_path, f"sub-{id}_late_minus_early_z.nii.gz")
        )


if __name__ == "__main__":
    # Run it like python3 XXXX.py 5214
    subject_id = sys.argv[1]
    get_diff_z(subject_id)
