#!/usr/bin/env python

import os
import numpy as np
import pandas as pd
import networkx as nx
from plot_prepost import plot_prepost

def extract_shortest_paths(edges0):
    """Gets shortest node lengths (make sure to give 0 indexed edge list)"""
    # Make a graph from the edge list (0 indexed)
    G = nx.Graph()
    G.add_edges_from(edges0)

    # Built in function to get all shortest paths
    all_pairs = dict(nx.all_pairs_shortest_path_length(G))

    # Init distance edge lists
    dist1 = []
    dist2 = []
    dist3 = []
    dist4 = []
    dist5 = []
    for u, dists in all_pairs.items():
        for v, dist in dists.items():
            if u < v:  # avoid duplicates (since undirected)
                # Gives us all the node pairs (where lower node is first) for each distance
                if dist == 1:
                    dist1.append([u, v])
                elif dist == 2:
                    dist2.append([u, v])
                elif dist == 3:
                    dist3.append([u, v])
                elif dist == 4:
                    dist4.append([u, v])
                elif dist ==5:
                    dist5.append([u, v])

    return dist1,dist2,dist3,dist4,dist5


def analyze_prepost(npz_name:str="rsa_results.npz"):
    """Saves prepost roi rsa data to an npz"""
    betas = 0 # If you have multiple beta comparisons can adjust

    #subject_list = ['1181','1185','1202','1211','1224','1227']
    subject_list = ['5153','5159','5152','700','5155','5156','5169','515','516','517','5191']
    subjects = len(subject_list) #number of subjects

    masks = ['l_lo','r_lo','l_erc','r_erc','l_tpo','r_tpo','l_hip','r_hip','l_put','r_put']

    betaseries = ['prepost']
    thisbeta = betaseries[betas]

    roi_rsa_result = [[],[],[],[],[],[],[],[],[],[]] #Initializes roi_rsa where each list is a mask label and within will be subjectxbin averages
    # directory from which we are working
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

            simdata = [[],[],[],[],[]]

            rsa = np.loadtxt(os.path.join(rsa_dir,subject_list[s]+'_'+thisbeta+'_3_runs_'+mask+'.txt'))
            rsa = np.tanh(rsa)
            prepost_size = int(rsa.shape[0]/2)

            pre = rsa[:prepost_size, :prepost_size]
            post = rsa[prepost_size:prepost_size*2, prepost_size:prepost_size*2]
            diff = post - pre
            
            n = diff.shape[0]

            edges = [
                [1,2], [2,4], [4,5], [4,12], [2,3], [3,4], [3,11], [11,12],
                [3,6], [6,7], [6,9], [9,11], [7,8], [8,9], [9,10], [8,10]
            ]

            # Each is a list of lists where in [[i,j],[n,m],...] i and j are different nodes that share an edge (1-indexed)
            dist1,dist2,dist3,dist4,dist5 = extract_shortest_paths(edges)

            for x in range(n):
                
                offset = x + 1

                for y in range(offset,n):

                    temp = diff[x,y]

                    if run[x] != run[y]: #only compare across runs
                        
                        if node[x] != node[y]: #only compare diff nodes

                            if [node[x],node[y]] in dist1:
                                simdata[0].append(temp)

                            elif [node[x],node[y]] in dist2:
                                simdata[1].append(temp)

                            elif [node[x],node[y]] in dist3:
                                simdata[2].append(temp)

                            elif [node[x],node[y]] in dist4:
                                simdata[3].append(temp)

                            elif [node[x],node[y]] in dist5:
                                simdata[4].append(temp)

            # Averages each bin per participant where each mean is per edge bin
            subdata = [np.mean(simdata[0]),np.mean(simdata[1]), np.mean(simdata[2]),np.mean(simdata[3]),np.mean(simdata[4])]
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
    analyze_prepost()
    plot_prepost()
