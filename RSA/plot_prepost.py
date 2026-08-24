#!/usr/bin/env python
import networkx as nx
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def plot_prepost(datafile:str='rsa_results.npz'):

    datafile = np.load("./ROI_RSA/rsa_results.npz",allow_pickle=True)

    mask_names = datafile['mask_names']
    data = datafile['data']

    sns.set_theme("talk","white")
    for i,label in enumerate(mask_names):
        region_data = data[i]

        plt.figure(figsize=(8,6))

        # bars + SE
        sns.barplot(data=region_data, errorbar='se', color='lightgray',capsize=0.07)

        # participant dots
        palette = sns.color_palette("tab10", region_data.shape[0])

        for i in range(region_data.shape[0]):
            sns.stripplot(
                x=np.arange(region_data.shape[1]),
                y=region_data[i],
                color=palette[i],
                size=6
            )
            plt.plot(np.arange(region_data.shape[1]), region_data[i], color=palette[i], alpha=0.1)

            
        plt.title(f"{label} Region Post - Pre Correlations",fontsize=20,fontweight='bold',pad=20)
        plt.ylabel("Post - Pre Correlations",fontsize=20,fontweight='bold')
        plt.xticks(range(5),['Edge','Two','Three','Four','Five'])
        plt.xlabel("Edge Distance",fontsize=20,fontweight='bold')
        sns.despine()
        plt.show()
        plt.savefig(f"./figures/{label}_roi_rsa_3_runs.png")

def plot_validation_prepost(filename:str='rsa_validation_results_post.npz'):

    datafile = np.load(f"./ROI_RSA/{filename}",allow_pickle=True)

    mask_names = datafile['mask_names']
    data = datafile['data']

    sns.set_theme("talk","white")
    for i,label in enumerate(mask_names):
        region_data = data[i]

        plt.figure(figsize=(8,6))

        # bars + SE
        sns.barplot(data=region_data, errorbar='se', color='lightgray',capsize=0.07)

        # participant dots
        palette = sns.color_palette("tab10", region_data.shape[0])

        for i in range(region_data.shape[0]):
            sns.stripplot(
                x=np.arange(region_data.shape[1]),
                y=region_data[i],
                color=palette[i],
                size=6
            )
            plt.plot(np.arange(region_data.shape[1]), region_data[i], color=palette[i], alpha=0.1)

            
        plt.title(f"{label} Pre Self-Similarity",fontsize=20,fontweight='bold',pad=20)
        plt.ylabel("Spearman Correlation",fontsize=20,fontweight='bold')
        plt.xticks(range(3),['Run1Run2','Run1Run3','Run2Run3'])
        plt.xlabel("Run Comparison",fontsize=20,fontweight='bold')
        sns.despine()
        plt.show()
        plt.savefig(f"./figures/{label}_VALIDATION_roi_rsa_3_runs.png")

if __name__ == "__main__":
    plot_prepost()
