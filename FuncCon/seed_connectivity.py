# FuncCon
import os
import sys
import glob
from nilearn import datasets, plotting, image
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from nilearn.maskers import NiftiSpheresMasker
from nilearn.maskers import NiftiMasker
from nilearn.maskers import NiftiLabelsMasker
from pathlib import Path
import pandas as pd

class SeedConnectivity():
    def __init__(self,sub_id:int=5159,bold_path:str='../../R01-fmri/fmriprep_pepolar/',seed_region:str="Hippocampus"):
        self.ID = sub_id
        self.func_filename = os.path.join(bold_path,f'sub-{self.ID}','ses-3','func',f'sub-{self.ID}_ses-3_task-StudyGW_space-MNI152NLin6Asym_res-2_desc-preproc_bold.nii.gz')

        # Need to deside what we want to use as confounds
        self.confound_filename = os.path.join(bold_path,f'sub-{self.ID}','ses-3','func',f'sub-{self.ID}_ses-3_task-StudyGW_desc-confounds_timeseries_filtered.tsv')

        # THIS IS THE PCC FROM THE TUTORIAL, NEED TO CHANGE
        self.seed_sphere_coords = [(0, -52, 18)]

        self.output_dir = Path.cwd() / "results" / "plot_seed_to_voxel_correlation"
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.seed_region=seed_region
        print(f"Output will be saved to: {self.output_dir}")
        print(f"Running seed for {self.seed_region}. Make sure coordinates are correct!")
    
    def make_events_df(self):
        """
        returns concat_event_dfs which is a list of pd.DataFrames
        """
        df = pd.read_csv(f"study_data/study.{self.ID}.result-2-Study.csv",on_bad_lines="skip")
        # df = pd.read_csv(f"/Users/rohinpalsule/Documents/GitHub/R01-Scanner/GWF-Scanner/results/study.{self.ID}.result-2-Study.csv",on_bad_lines="skip")

        event_df = df[['trial_timestamp']]
        event_df = event_df.copy()
        event_df['duration'] = 3
        event_df['accuracy'] = df['accuracy']
        event_df = event_df.rename(columns={"trial_timestamp":"onset"})
        event_df['block'] = np.repeat(np.arange(1, 9), 16)
        event_df['trial_type']=np.select([event_df['block'].isin([1,2]),
                                        event_df['block'].isin([3,4]),
                                        event_df['block'].isin([5,6]),
                                        event_df['block'].isin([7,8])],
                                        [1,2,3,4])
        event_df['trial'] = event_df.index +1
        event_df[['node_l','node_r',]] = df[['node_l','node_r',]]
        event_df['TR'] = np.ceil(event_df['onset']/2)
        return event_df

    def get_sphere_seed(self):
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
    
    def get_subco_seed(self,coords:tuple=(9,19),bilateral:bool=True):
        """
        Different way to get seed 
        \n IMPORTANT: if only left/right, make coords a tuple (l,r) with the empty one == 0 and set bilateral to False
        """
        sub_atlas = datasets.fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm")
        # sub_labels = sub_atlas.labels

        if bilateral:
            l_mask = image.math_img(f"img == {coords[0]}", img=sub_atlas.maps) # l_hippocampus
            r_mask = image.math_img(f"img == {coords[1]}", img=sub_atlas.maps) # r_hippocampus

            b_mask = image.math_img(
                "img1 + img2",
                img1=l_mask,
                img2=r_mask
            )
        else:
            b_mask = image.math_img(f"img == {np.max(coords)}", img=sub_atlas.maps) # l_hippocampus

        seed_masker = NiftiLabelsMasker(
            labels_img=l_mask,
            detrend=True,
            standardize=True,
            standardize_confounds=True,
            low_pass=0.1,
            high_pass=0.01,
            t_r=2,
        )
        return seed_masker
    
    def fit_seed(self,seed_masker,func_file=None,confound_file=None):
        if func_file is None:
            func_file = self.func_filename
        if confound_file is None:
            confound_file = self.confound_filename
        
        seed_time_series = seed_masker.fit_transform(
            func_file, confounds=[confound_file]
        )
        return seed_time_series
    
    def mask_timeseries(self):
        """
        Need to adjust all hyperparameters + add mask (mask_img=)
        """
        brain_masker = NiftiMasker(
            mask_img=f"MNI_masks/sub-{self.ID}_b_gray_dilD_2mm.nii.gz",
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
    
    def fit_timeseries(self,brain_masker,func_file=None,confound_file=None):
        if func_file is None:
            func_file = self.func_filename
        if confound_file is None:
            confound_file = self.confound_filename
        
        brain_time_series = brain_masker.fit_transform(
            func_file, confounds=[confound_file]
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
    
    def save_fisher_nifti(self,brain_masker,seed_to_voxel_correlations,partition=None):
        seed_to_voxel_correlations_fisher_z = np.arctanh(seed_to_voxel_correlations)
        seed_to_voxel_correlations_fisher_z_img = brain_masker.inverse_transform(
            seed_to_voxel_correlations_fisher_z.T
        )

        if partition is None:
            outfile = f"sub-{self.ID}_{self.seed_region}_seed_correlation_z.nii.gz"
        else:
            outfile = f"sub-{self.ID}_{self.seed_region}_seed_{partition}_correlation_z.nii.gz"

        seed_to_voxel_correlations_fisher_z_img.to_filename(
            self.output_dir / outfile
        )
    
    def get_seed_connectivity_nifti(self,func_file=None,confound_file=None, partition=None):
        """
        Main workflow that generates fisher z nifit files for a specified seed
        """
        seed_masker = self.get_subco_seed()
        seed_time_series = self.fit_seed(seed_masker,func_file,confound_file)
        brain_masker = self.mask_timeseries()
        brain_time_series = self.fit_timeseries(brain_masker,func_file,confound_file)

        seed_to_voxel_correlations = self.get_seed_voxel_correlations(
            brain_time_series,seed_time_series)
        
        self.save_fisher_nifti(brain_masker,seed_to_voxel_correlations,partition)
    
    def partition_data(self):
        """
        Right now I'm going to partition the data into 4 blocks, and compare late vs early, same as GLM
        """
        event_df = self.make_events_df()
        
        early_tr = np.array(event_df[event_df['trial_type']==1]['TR'])
        early_min = int(early_tr.min() - 1)
        early_max = int(early_tr.max())

        early_confound = pd.read_csv(self.confound_filename,sep='\t').iloc[early_min:early_max].reset_index(drop='index')
        early_func = image.index_img(self.func_filename, slice(early_min, early_max))

        late_tr = np.array(event_df[event_df['trial_type']==4]['TR'])
        late_min = int(late_tr.min() - 1)
        late_max = int(late_tr.max())

        late_confound = pd.read_csv(self.confound_filename,sep='\t').iloc[late_min:late_max].reset_index(drop='index')
        late_func = image.index_img(self.func_filename, slice(late_min, late_max))

        return (early_func,late_func), (early_confound,late_confound)
    
    def run_seed_con_differences(self):
        """
        Tuples are (early,late), saves 2 niftis w early and late in filename
        """
        func_tup, conf_tup = self.partition_data()

        for i,segment in enumerate(["early","late"]):
            self.get_seed_connectivity_nifti(func_file=func_tup[i],confound_file=conf_tup[i],partition=segment)
            print("Finished ", segment)


if __name__ == "__main__":
    sub_id=sys.argv[1]
    FC = SeedConnectivity(sub_id=int(sub_id))
    FC.run_seed_con_differences()
    print("All done!")

