# GLM
import os
import sys
import glob
from nilearn.image import mean_img
from nilearn.plotting import plot_anat, plot_img, plot_stat_map, show
from nilearn.glm.first_level import FirstLevelModel
from nilearn.plotting import plot_design_matrix
from nilearn.plotting import plot_contrast_matrix
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# PCA
from nilearn.maskers import NiftiMasker
from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
from nilearn import image

# Classifier
from copy import deepcopy
from sklearn.model_selection import PredefinedSplit
from time import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVC

#/Users/rohinpalsule/Desktop/GLM/
class LocalizerGLM:
    """
    Pipeline and helper functions for getting contrast maps for our Localizer Task
    """
    def __init__(self,initials:str="5160_LL", bold_dir:str=f"/Users/rohinpalsule/Desktop/GLM/",output_dir:str="/Users/rohinpalsule/Desktop/localizer_outputs"):
        self.SUB_INITIALS = initials
        self.SUB_ID = self.SUB_INITIALS.split("_")[0]
        self.loc_path = f"{bold_dir}/sub-{self.SUB_ID}/smoothed/"

        # Grabs and sorts functional localizer scans in order
        self.func_scans = glob.glob(os.path.join(self.loc_path,f"sub-{self.SUB_ID}_ses-2_task-Localizer_run-*_space-MNI152NLin6Asym_res-2_desc-preproc_bold_sm6.nii"))
        self.func_scans = sorted(self.func_scans)

        # Creates a path for Localzier outputs
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def plot_mean_func(self):
        """
        Helper function to see func scans
        """
        mean_img = mean_img(self.func_scans)
        plot_img(mean_img, cbar_tick_format="%i")
        show()

    def define_first_level(self):
        """
        Define GLM Model, our scanner uses these for everything so I have left it fixed but adjust TR if needed
        """
        fmri_glm = FirstLevelModel(
            t_r=2,
            noise_model="ar1",
            standardize=False,
            hrf_model="spm",
            drift_model="cosine",
            high_pass=1/128,
            verbose=1,
            mask_img=f"MNI_masks/sub-{self.SUB_ID}/b_gray_dilD_2mm.nii.gz"
        )
        return fmri_glm
    
    def make_events_df(self):
        """
        returns concat_event_dfs which is a list of pd.DataFrames
        """
        events = glob.glob(f"/Users/rohinpalsule/Documents/GitHub/R01-Scanner/CB_PrePost/data/CB_{self.SUB_INITIALS}/CB_{self.SUB_INITIALS}_localizer_*.txt")
        concat_event_dfs = []

        # Does it for every run
        for file in events:
            events_df = pd.read_csv(file, sep="\t")

            # Labels block by repetition (this is messy can be refactored)
            events_df['block'] = (
                (events_df['stimtype'] != events_df['stimtype'].shift()) |
                (events_df['stimtype'].isna()) |
                (events_df['stimtype'].shift().isna())
            ).cumsum()

            # Removes NAs and factorizes blocks so it is just 9 blocks
            events_df = events_df.dropna(subset=['stimtype'])
            events_df['block'] = pd.factorize(events_df['block'])[0] + 1
            
            # Creates an events_df by block
            block_df = events_df.groupby('block').agg(run=("run","first"),onset=('onset', 'first'),trial_type=('stimtype', 'first')).reset_index(drop=True)
            block_df['duration'] = 24
            block_df['trial_type']=block_df['trial_type'].map({1:'objects',2:'scenes',3:'scrambled'})
            concat_event_dfs.append(block_df)

            # Concats and sorts event_dfs so it is a list of Dfs
            concat_event_dfs = sorted(concat_event_dfs, key=lambda df: df['run'].iloc[0])
        return concat_event_dfs

    def make_confounds_df(self):

        # Loads all confound tsv files
        confound_files = glob.glob(f"/Users/rohinpalsule/Desktop/GLM/sub-{self.SUB_ID}/sub-{self.SUB_ID}_ses-2_task-Localizer_run-*_desc-confounds_timeseries.tsv")

        confound_dfs = []

        # Grabs just motion and rotation, labels run so I can sort properly
        for c_file in confound_files:
            confound_df = pd.read_csv(c_file,sep='\t')[['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']]
            confound_df['run'] = c_file.split("_run-")[1].split("_")[0]
            confound_dfs.append(confound_df)
        confound_dfs = sorted(confound_dfs, key=lambda df: df['run'].iloc[0])
        confound_dfs = [df.drop(columns='run') for df in confound_dfs]

        return confound_dfs

    def fit_glm(self):
        concat_event_dfs = self.make_events_df()
        confound_dfs = self.make_confounds_df()
        fmri_glm = fmri_glm.fit(run_imgs=self.func_scans, events=concat_event_dfs,confounds=confound_dfs)

        return fmri_glm

    def plot_loc_design_matrix(self,run_idx):
        """
        Visualizes the design matrix for a localizer run
        """
        glm = self.fit_glm()
        design_matrix = glm.design_matrices_[run_idx]
        plot_design_matrix(design_matrix)
        show()
        # Shows each stim type and its HRF
        plt.plot(design_matrix["objects"])
        plt.plot(design_matrix["scenes"])
        plt.plot(design_matrix["scrambled"])
        plt.xlabel("Seconds")
        plt.title("Scene Response")
        show()

    def make_contrast_map(self,obj_reg:int,scene_reg:int,scram_reg:int):
        glm = self.fit_glm()
        design_matrix = glm.design_matrices_[0] # Just a dummy matrix for regressors
        n_regressors = design_matrix.shape[1]
        contrasts = np.zeros(n_regressors)
        contrasts[0] = obj_reg
        contrasts[1] = scene_reg
        contrasts[3] = scram_reg

        return contrasts
    
    def get_contrast_nii(self,contrasts:list,map_name:str):
        fmri_glm = self.fit_glm()

        z_map = fmri_glm.compute_contrast(contrasts, stat_type='t')
    
        output_path = os.path.join(self.output_dir,"contrast_maps")
        output_path.mkdir(exist_ok=True, parents=True)

        z_map.to_filename(os.path.join(output_path,map_name,".nii.gz"))

        return z_map
        
    def plot_contrast_map(self,name:str='scene > object and scrambled',contrasts:list=[-0.5,1,-0.5]):
        contrasts = self.make_contrast_map(contrasts[0],contrasts[1],contrasts[2])
        z_map = self.get_contrast_nii(contrasts,name)
        plotting_config = {
            "bg_img": mean_img(self.func_scans),
            "display_mode": "z",
            "cut_coords": 5,
            "black_bg": True,
        }
        plot_stat_map(
            z_map,
            threshold=3,
            title=name,
            figure=plt.figure(figsize=(10, 4)),
            **plotting_config,
        )
        show()

class GWF_StudyGLM:
    """
    Pipeline and helper functions for getting contrast maps for our GW Study Task
    """
    def __init__(self,sub_id:str="5159", bold_dir:str=f"smoothed_func",output_dir:str="results/GLM_Study"):

        self.SUB_ID = sub_id
        self.study_path = f"{bold_dir}/sub-{self.SUB_ID}/"

        # Grabs and sorts functional localizer scans in order
        self.func_scans = glob.glob(os.path.join(self.study_path,f"sub-{self.SUB_ID}_ses-3_task-StudyGW_space-T1w_desc-preproc_bold_sm6.nii.gz"))
        self.func_scans = sorted(self.func_scans)

        # Creates a path for Localzier outputs
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def plot_mean_func(self):
        """
        Helper function to see func scans
        """
        mean_img_ = mean_img(self.func_scans)
        plot_img(mean_img_, cbar_tick_format="%i")
        show()

    def define_first_level(self):
        """
        Define GLM Model, our scanner uses these for everything so I have left it fixed but adjust TR if needed
        """
        fmri_glm = FirstLevelModel(
            t_r=2,
            noise_model="ar1",
            standardize=False,
            hrf_model="spm",
            drift_model="cosine",
            high_pass=1/128,
            verbose=1,
            mask_img=f"../RSA/transformed_masks/sub-{self.SUB_ID}/roi_t/b_gray_dilD_2mm.nii.gz"
        )
        return fmri_glm
    
    def make_events_df(self):
        """
        returns concat_event_dfs which is a list of pd.DataFrames
        """
        df = pd.read_csv(f"study_data/study.{self.SUB_ID}.result-2-Study.csv",on_bad_lines="skip")


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
        event_df.to_csv(
            os.path.join(self.output_dir,f'sub-{self.SUB_ID}_ses-03_task-StudyGW_events.tsv'),
            sep='\t',
            index=False
        )
        return event_df

    def make_confounds_df(self):
        confound_df = pd.read_csv(f"../../R01-fmri/fmriprep_pepolar/sub-{self.SUB_ID}/ses-3/func/sub-{self.SUB_ID}_ses-3_task-StudyGW_desc-confounds_timeseries.tsv",sep='\t')[['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']]

        return confound_df

    def fit_glm(self):
        concat_event_dfs = self.make_events_df()
        confound_dfs = self.make_confounds_df()
        fmri_glm = self.define_first_level()
        fit_glm = fmri_glm.fit(run_imgs=self.func_scans, events=concat_event_dfs,confounds=confound_dfs)

        return fit_glm

    # def plot_loc_design_matrix(self,run_idx):
    #     """
    #     Visualizes the design matrix for a localizer run
    #     """
    #     glm = self.fit_glm()
    #     design_matrix = glm.design_matrices_[run_idx]
    #     plot_design_matrix(design_matrix)
    #     show()
    #     # Shows each stim type and its HRF
    #     plt.plot(design_matrix["objects"])
    #     plt.plot(design_matrix["scenes"])
    #     plt.plot(design_matrix["scrambled"])
    #     plt.xlabel("Seconds")
    #     plt.title("Scene Response")
    #     show()

    def make_contrast_map(self,glm,block_1:int,block_2:int,block_3:int,block_4:int):
        if glm is None:
            glm = self.fit_glm()
        design_matrix = glm.design_matrices_[0] # Just a dummy matrix for regressors
        n_regressors = design_matrix.shape[1]
        contrasts = np.zeros(n_regressors)
        contrasts[0] = block_1
        contrasts[1] = block_2
        contrasts[3] = block_3
        contrasts[4] = block_4

        return contrasts
    
    def get_contrast_nii(self,glm,contrasts:list,map_name:str):
        if glm:
            fmri_glm = glm
        else:
            fmri_glm = self.fit_glm()


        z_map = fmri_glm.compute_contrast(contrasts, stat_type='t')
    
        output_path = self.output_dir / "contrast_maps"
        print(output_path)
        output_path.mkdir(exist_ok=True, parents=True)

        z_map.to_filename(output_path / f"{map_name}.nii.gz")

        return z_map
        
    def plot_contrast_map(self,glm,name:str='late > early block',contrasts:list=[-1,0,0,1]):
        if glm == None:
            fit_glm = self.fit_glm()
        else:
            fit_glm = glm #self.fit_glm()
        contrasts = self.make_contrast_map(fit_glm,contrasts[0],contrasts[1],contrasts[2],contrasts[3])
        z_map = self.get_contrast_nii(fit_glm,contrasts,name)
        plotting_config = {
            "bg_img": mean_img(self.func_scans),
            "display_mode": "z",
            "cut_coords": 5,
            "black_bg": True,
        }
        plot_stat_map(
            z_map,
            threshold=3,
            title=name,
            figure=plt.figure(figsize=(10, 4)),
            **plotting_config,
        )
        show()

if __name__ == "__main__":
    sub_id = sys.argv[1]

    glm = GWF_StudyGLM(sub_id=str(sub_id))
    fit_glm = glm.fit_glm()
    glm.plot_contrast_map(glm=fit_glm,name=f"{glm.SUB_ID}_pure_late_early",contrasts=[-1,0,0,1])
