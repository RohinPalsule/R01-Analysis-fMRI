#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import networkx as nx
from plot_prepost import plot_validation_prepost

def validate_prepost(npz_name:str="rsa_validation_results.npz"):
    """Saves prepost roi rsa data to an npz"""
    betas = 0 # If you have multiple beta comparisons can adjust

    #subject_list = ['1181','1185','1202','1211','1224','1227']
    with open("sublist_initials.txt", "r") as f:
        subject_list = [line.strip().split("_")[0] for line in f if line.strip()]

    subjects = len(subject_list)

    masks = ['l_lo','r_lo','l_erc','r_erc','l_tpo','r_tpo','l_hip','r_hip',
            'l_put','r_put']

    betaseries = ['new_prepost']
    thisbeta = betaseries[betas]

    roi_rsa_result = [[] for _ in masks]    # directory from which we are working

    dir = os.getcwd()

    rsa_dir = os.path.join(".","ROI_RSA")

    for m in range(len(masks)):
        #get the mask and initialize the data
        mask = masks[m]
        maskdata = []
        
        for s in range(subjects):
            
            chunks = np.loadtxt(os.path.join('.','volinfo','prepost_volinfo.txt'))

            phase = chunks[:, 0]
            run   = chunks[:, 1]
            node  = chunks[:, 2]

            simdata = []

            rsa = np.loadtxt(os.path.join(rsa_dir,subject_list[s]+'_'+thisbeta+'_3_runs_'+mask+'.txt'))
            rsa = np.tanh(rsa)
            prepost_size = int(rsa.shape[0]/2)

            pre = rsa[:prepost_size, :prepost_size]
            # post = rsa[prepost_size:prepost_size*2, prepost_size:prepost_size*2]
            # diff = post - pre
            
            n = pre.shape[0]

            simdata = {
                (1, 2): [],
                (1, 3): [],
                (2, 3): []
            }

            for x in range(n):
                for y in range(x + 1, n):

                    if run[x] != run[y] and node[x] == node[y]:

                        pair = tuple(sorted([run[x], run[y]]))
                        simdata[pair].append(pre[x, y])

            # length is num of run comparisons
            subdata = [np.mean(simdata[pair]) for pair in [(1, 2), (1, 3), (2, 3)]]
            print(f"Subject {subject_list[s]}, Mask {mask}: {subdata}")
            # # Averages each bin per participant where each mean is per edge bin
            # subdata = [np.mean(simdata[0]),np.mean(simdata[1]), np.mean(simdata[2]),np.mean(simdata[3]),np.mean(simdata[4])]
            maskdata.append(subdata)

            # Adds to roi_rsa LofL where each m is the mask label
            roi_rsa_result[m] = maskdata

    # Saves RSA structure as an npz
    np.savez(
        os.path.join(rsa_dir,npz_name),
        data=roi_rsa_result,
        mask_names=masks
    )

if __name__ == "__main__":
    validate_prepost()
    plot_validation_prepost()
