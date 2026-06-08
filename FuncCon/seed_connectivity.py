# FuncCon
import os
import sys
import glob
from nilearn import datasets, plotting
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from nilearn.maskers import NiftiSpheresMasker
from nilearn.maskers import NiftiMasker
from pathlib import Path

class SeedConnectivity():
    def __init__(self,sub_id:int=5159,bold_path:str='/Users/rohinpalsule/Desktop/GLM/'):
        self.ID = sub_id
        self.func_filename = os.path.join(bold_path,f'sub-{self.ID}',f'sub-{self.ID}_ses-3_task-StudyGW_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz')

        # Need to deside what we want to use as confounds
        self.confound_filename = os.path.join(bold_path,f'sub-{self.ID}',f'sub-{self.ID}_ses-3_task-StudyGW_desc-confounds_timeseries_filtered.tsv')

        # THIS IS THE PCC FROM THE TUTORIAL, NEED TO CHANGE
        self.seed_sphere_coords = [(0, -52, 18)]

        self.output_dir = Path.cwd() / "results" / "plot_seed_to_voxel_correlation"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        print(f"Output will be saved to: {self.output_dir}")
        
    def get_seed(self):
        seed_masker = NiftiSpheresMasker(
            self.seed_sphere_coords,
            radius=8,
            detrend=True,
            standardize_confounds=True,
            standardize=True, # The original tutorial did not have this but this is how I got it mean centered and have the correlations interpretable 
            low_pass=0.1,
            high_pass=0.01,
            t_r=2,
            memory="nilearn_cache",
            memory_level=1,
            verbose=1,
        )
        return seed_masker
    
    def fit_seed(self,seed_masker):
        seed_time_series = seed_masker.fit_transform(
            self.func_filename, confounds=[self.confound_filename]
        )
        return seed_time_series
    
    def mask_timeseries(self):
        """
        Need to adjust all hyperparameters + add mask (mask_img=)
        """
        brain_masker = NiftiMasker(
            smoothing_fwhm=6,
            detrend=True,
            standardize_confounds=True,
            standardize=True, # The original tutorial did not have this but this is how I got it mean centered and have the correlations interpretable 
            low_pass=0.1,
            high_pass=0.01,
            t_r=2,
            memory="nilearn_cache",
            memory_level=1,
            verbose=1,
        )
        return brain_masker
    
    def fit_timeseries(self,brain_masker):
        brain_time_series = brain_masker.fit_transform(
            self.func_filename, confounds=[self.confound_filename]
        )
        return brain_time_series
    
    def plot_seed_timeseries(self,seed_time_series,region:str='Posterior Cingulate Cortex'):
        """
        Need to grab seed_time_series from self.fit_seed(), helper function for sanity checks
        """
        plt.figure(constrained_layout=True)
        plt.plot(seed_time_series)
        plt.title(f"Seed time series ({region})")
        plt.xlabel("Scan number")
        plt.ylabel("Normalized signal")

    def get_seed_voxel_correlations(self,brain_time_series,seed_time_series):
        """
        brain_time_series is from self.fit_timeseries\n
        seed_time_series is from self.fit_seed
        """
        seed_to_voxel_correlations = (
            np.dot(brain_time_series.T, seed_time_series) / seed_time_series.shape[0]
        )
        print("Seed-to-voxel correlation shape: ({}, {})".format(*seed_to_voxel_correlations.shape))

        print(f"Seed-to-voxel correlation: "
            f"min = {seed_to_voxel_correlations.min():.3f}; "
            f"max = {seed_to_voxel_correlations.max():.3f}")
        
        return seed_to_voxel_correlations
    
    def plot_seed_voxel_map(self,brain_masker,seed_to_voxel_correlations):
        """
        brain_masker is from self.mask_timeseries\n
        seed_to_voxel_correlations is from self.get_seed_voxel_correlations
        """

        seed_to_voxel_correlations_img = brain_masker.inverse_transform(
            seed_to_voxel_correlations.T
        )
        display = plotting.plot_stat_map(
            seed_to_voxel_correlations_img,
            threshold=0.5,
            vmax=1,
            cut_coords=self.seed_sphere_coords[0],
            title="Seed-to-voxel correlation (PCC seed)",
        )
        display.add_markers(
            marker_coords=self.seed_sphere_coords, marker_color="g", marker_size=300
        )

        display.savefig(self.output_dir / "pcc_seed_correlation.pdf")
    
    def save_fisher_nifti(self,brain_masker,seed_to_voxel_correlations):
        seed_to_voxel_correlations_fisher_z = np.arctanh(seed_to_voxel_correlations)
        seed_to_voxel_correlations_fisher_z_img = brain_masker.inverse_transform(
            seed_to_voxel_correlations_fisher_z.T
        )
        seed_to_voxel_correlations_fisher_z_img.to_filename(
            # Need to change pcc to smth else
            self.output_dir / f"sub-{self.ID}_pcc_seed_correlation_z.nii.gz"
        )
    
    def get_seed_connectivity_nifti(self):
        """
        Main workflow that generates fisher z nifit files for a specified seed
        """
        seed_masker = self.get_seed()
        seed_time_series = self.fit_seed(seed_masker)
        brain_masker = self.mask_timeseries()
        brain_time_series = self.fit_timeseries(brain_masker)

        seed_to_voxel_correlations = self.get_seed_voxel_correlations(
            brain_time_series,seed_time_series)
        
        self.save_fisher_nifti(brain_masker,seed_to_voxel_correlations)

if __name__ == "__main__":
    FC = SeedConnectivity()
    FC.get_seed_connectivity_nifti()
    print("All done!")