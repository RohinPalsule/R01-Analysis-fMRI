# 9/6/26 RL: created
# 9/9/26 RL: adjust low+high pass
#9/17/26 RL: add smoothing, add fisher z to each square in matrix, changed standardize= to get rid of error messages, changed the path where filt confounds are located
#10/4/26 RL: changed order of roi masks in roi_files so heatmap will be pretty

# ROI-to-ROI functional connectivity
# Extracts one mean time series from every ROI mask,
# correlates every ROI with every other ROI,
# and saves Pearson r and Fisher z matrices.

import os
import sys
import glob
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nilearn.maskers import NiftiLabelsMasker


class ROIConnectivity():

    def __init__(
        self,
        sub_id: int = 5159,
        bold_path: str = "../../R01-fmri/fmriprep_pepolar/",
        roi_path: str = "ROI_masks"
    ):

        self.ID = sub_id

        # define gw bold data file (entire study phase)
        self.func_filename = os.path.join(
            bold_path,
            f"sub-{self.ID}",
            "ses-3",
            "func",
            f"sub-{self.ID}_ses-3_task-StudyGW_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz"
        )

        # define filtered confounds file
        self.confound_filename = os.path.join(
            "results",
            "filt_confounds_rumi", #changed
            f"sub-{self.ID}_ses-3_task-StudyGW_desc-confounds_timeseries_filtered.tsv"
        )

        # define folder containing all the roi masks
        self.roi_path = Path(roi_path)

        # define output folder
        self.output_dir = Path.cwd() / "results" / "roi_to_roi_rumi"
        self.output_dir.mkdir(exist_ok=True, parents=True)

        print(f"Subject: {self.ID}")
        print(f"ROI folder: {self.roi_path}")
        print(f"Output will be saved to: {self.output_dir}")


    def get_roi_files(self):
        """
        Finds all .nii.gz ROI masks in the ROI folder
        and arranges them so that roi_files is in a specified order (10/4/26 RL).
        """
        roi_order = [
            "LH_hip_ant",
            "LH_hip_body",
            "LH_hip_tail",
            "RH_hip_ant",
            "RH_hip_body",
            "RH_hip_tail",
            "LH_Par",
            "LH_pCunPCC",
            "LH_PFC",
            "LH_Temp",
            "RH_Par",
            "RH_pCunPCC",
            "RH_PFCdPFCm",
            "RH_PFCv",
            "RH_Temp"
        ]

        roi_files = [
            str(self.roi_path / f"{roi}.nii.gz")
            for roi in roi_order
        ]

        # make sure all expected masks actually exist
        for roi_file in roi_files:
            if not os.path.exists(roi_file):
                raise FileNotFoundError(
                    f"ROI mask not found: {roi_file}"
                )

        print(f"Found {len(roi_files)} ROI masks.")

        return roi_files


    def make_roi_masker(self, roi_file):
        """
        Makes a masker for one ROI.

        Because the ROI mask is treated as one label,
        fit_transform() returns one average time series
        across all voxels in that ROI.
        """

        roi_masker = NiftiLabelsMasker(
            labels_img=roi_file,
            smoothing_fwhm=4,
            detrend=True,
            standardize="zscore_sample", #9/17 RL: changed
            standardize_confounds=True,
            low_pass=0.09,
            high_pass=0.008,
            t_r=2,
        )

        return roi_masker


    def extract_roi_timeseries(self):
        """
        Loops through every ROI mask and extracts one mean
        BOLD time series for each ROI.

        Returns:
            roi_names: list of ROI names
            roi_timeseries: array of shape (n_TRs, n_ROIs)

        combines get_subco_seed() and fit_seed() functions from RP script
        """

        roi_files = self.get_roi_files()

        roi_names = []
        timeseries_list = []

        for roi_file in roi_files:

            # Example:
            # LH_hip_ant.nii.gz -> LH_hip_ant
            roi_name = Path(roi_file).name.replace(".nii.gz", "")

            print(f"Extracting ROI: {roi_name}")

            roi_masker = self.make_roi_masker(roi_file) #make masker

            roi_ts = roi_masker.fit_transform( #find ROI, extract time series, average across all vox in ROI, regress out confounds, etc.
                self.func_filename,
                confounds=[self.confound_filename]
            )

            if roi_ts.shape[1] != 1: #CHECK THAT IT'S ONLY 1 COLUMN (1 TIME SERIES)
                raise ValueError(
                    f"{roi_name} returned {roi_ts.shape[1]} time series instead of 1."
                )

            # NiftiLabelsMasker should return n_TRs x 1, so index first col
            roi_ts = roi_ts[:, 0]

            roi_names.append(roi_name)
            timeseries_list.append(roi_ts)

        # Each list element is one ROI.
        # Stack so columns = ROIs and rows = TRs.
        roi_timeseries = np.column_stack(timeseries_list)

        print(
            f"ROI time-series matrix shape: "
            f"{roi_timeseries.shape}"
        )

        return roi_names, roi_timeseries


    def calculate_connectivity(self, roi_timeseries):
        """
        Calculates ROI-to-ROI Pearson correlation matrix
        and Fisher z transformed matrix.

        conceptually does get_seed_voxel_correlations() and get_ROI_to_ROI_fisher_z() from RP script
        """

        # Rows = TRs, Columns = ROIs
        # np.corrcoef(..., rowvar=False) correlates columns
        r_matrix = np.corrcoef(
            roi_timeseries,
            rowvar=False
        )

        # Avoid arctanh(1) = infinity on the diagonal.
        # Clip only for numerical stability.
        r_for_z = np.clip(
            r_matrix,
            -0.999999,
            0.999999
        )

        z_matrix = np.arctanh(r_for_z) #convert r to z

        # Self-correlation is not meaningful for ROI-to-ROI FC.
        np.fill_diagonal(z_matrix, np.nan)

        return r_matrix, z_matrix


    def save_connectivity_matrices(
        self,
        roi_names,
        r_matrix,
        z_matrix
    ):
        """
        Saves Pearson r and Fisher z matrices as CSV files.
        """

        r_df = pd.DataFrame(
            r_matrix,
            index=roi_names,
            columns=roi_names
        )

        z_df = pd.DataFrame(
            z_matrix,
            index=roi_names,
            columns=roi_names
        )

        r_outfile = (
            self.output_dir /
            f"sub-{self.ID}_roi_to_roi_r.csv"
        )

        z_outfile = (
            self.output_dir /
            f"sub-{self.ID}_roi_to_roi_fisher_z.csv"
        )

        r_df.to_csv(r_outfile)
        z_df.to_csv(z_outfile)

        print(f"Saved Pearson r matrix: {r_outfile}")
        print(f"Saved Fisher z matrix: {z_outfile}")


    def plot_connectivity(self, z_matrix, roi_names):
        """
        Creates and saves a heatmap of the Fisher-z
        ROI-to-ROI connectivity matrix.

        Uses the same color scale for all subjects.
        """

        fig, ax = plt.subplots(figsize=(12, 10))

        im = ax.imshow(
            z_matrix,
            cmap="coolwarm",
            vmin=-1, #adjusting the scale!!! maybe change...?
            vmax=1
        )
 
        # add Fisher z value to each cell
        for i in range(len(roi_names)):
            for j in range(len(roi_names)):
                if not np.isnan(z_matrix[i, j]):
                    ax.text(
                        j, i,
                        f"{z_matrix[i, j]:.2f}",
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
            ax=ax,
            label="Fisher z"
        )

        ax.set_title(
            f"Subject {self.ID} ROI-to-ROI Connectivity"
        )

        plt.tight_layout()

        output_file = (
            self.output_dir /
            f"sub-{self.ID}_roi_to_roi_heatmap.png"
        )

        plt.savefig(output_file, dpi=300)
        plt.close()

        print(f"Saved heatmap: {output_file}")


    def run_roi_to_roi(self):
        """
        Main ROI-to-ROI workflow.
        """

        roi_names, roi_timeseries = (
            self.extract_roi_timeseries()
        )

        r_matrix, z_matrix = (
            self.calculate_connectivity(
                roi_timeseries
            )
        )

        self.save_connectivity_matrices(
            roi_names,
            r_matrix,
            z_matrix
        )

        self.plot_connectivity(
            z_matrix,
            roi_names
        )


if __name__ == "__main__":

    sub_id = sys.argv[1]

    FC = ROIConnectivity(
        sub_id=int(sub_id),
        roi_path="DMN_HCP_ROI-ROI_masks" #change to where masks are
    )

    FC.run_roi_to_roi()

    print("All done!")
