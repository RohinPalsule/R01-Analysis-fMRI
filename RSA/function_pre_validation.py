"""Dissimilarity measure"""

__docformat__ = 'restructuredtext'

import numpy
from numpy import *
from numpy.random import randint
# from scipy.stats.stats import *
from mvpa2.measures.base import Measure
from mvpa2.measures import rsa
from get_graph_distances import extract_shortest_paths
import sys
from prsa import perm_z
import matplotlib.pyplot as plt
masktype = sys.argv[2]
tester = 1
class function_pre_validation(Measure):
    def __init__(self, metric, output, niter, sample_attributes):
        Measure.__init__(self)

        self.metric = metric
        self.dsm = []
        self.output = output
        self.niter = niter
        self.tester = 1
        sa = sample_attributes

        edges = [
            [1,2], [2,4], [4,5], [4,12], [2,3], [3,4], [3,11], [11,12],
            [3,6], [6,7], [6,9], [9,11], [7,8], [8,9], [9,10], [8,10]
        ]

        # Each is a list of lists where in [[i,j],[n,m],...] i and j are different nodes that share an edge (1-indexed)
        dist1,dist2,dist3,dist4,dist5 = extract_shortest_paths(edges)

        # Initialized rsa mask that's shape is the length of the sample attributes / 2 since we compare post vs. pre
        dist_num_rsa = zeros((int(len(sa['node'])/2),int(len(sa['node'])/2))) 

        # Initializing for loops below, where n = length of one side of the matrix above
        n = len(dist_num_rsa)
        one_dist_idx = []
        two_dist_idx = []
        three_dist_idx = []
        four_dist_idx = []
        five_dist_idx = []

        for x in range(n): # for every line

            for y in range(x+1,n): # for every line one ahead of x (only doing forward comparison)
                
                if sa['run'][x] == sa['run'][y]: # making it same run, since comparing across runs
                
                    if sa['node'][x] != sa['node'][y]: # only doing across node comparisons
                    
                        # These get the indicies in the volinfo (also the index of the n x n matrix) that correspond for each edge distance comparison
                        if ([sa['node'][x],sa['node'][y]] in dist1)|([sa['node'][y],sa['node'][x]] in dist1):                         
                            one_dist_idx.append([x,y])	#this is comparing one edge (direct pair)
                            
                        elif ([sa['node'][x],sa['node'][y]] in dist2)|([sa['node'][y],sa['node'][x]] in dist2):                          
                            two_dist_idx.append([x,y])	#this is comparing two edge dist

                        elif ([sa['node'][x],sa['node'][y]] in dist3)|([sa['node'][y],sa['node'][x]] in dist3):
                            three_dist_idx.append([x,y])	#this is comparing three edge dist

                        elif ([sa['node'][x],sa['node'][y]] in dist4)|([sa['node'][y],sa['node'][x]] in dist4):
                            four_dist_idx.append([x,y])   #this is comparing four edge dist

                        elif ([sa['node'][x],sa['node'][y]] in dist5)|([sa['node'][y],sa['node'][x]] in dist5):
                            five_dist_idx.append([x,y])	#this is comparing five edge dist

        # Create a 3-D array mask where the shape is (n,n,len(idxs)) and each [:,:,x] is the (x+1)th distance boolean array
        idxs = [one_dist_idx,two_dist_idx,three_dist_idx,four_dist_idx,five_dist_idx]
        for i,idx_data in enumerate(idxs):
            for dist_x,dist_y in idx_data:
                dist_num_rsa[int(dist_x),int(dist_y)] = i+1 # Add the number corresponding to edge distance to this numeric rsa matrix
        # dist_num_rsa contains a matrix of 0 (not an edge i.e. same nodes, same runs, etc.), 1 (edges), 2,3,4,5 (all edge distances away)

        # self.masks makes the 3-D array only containing True and False, where in the dist_num_rsa[:,:,1] all the indices that were edges are marked as True
        self.masks = dist_num_rsa[..., None] == arange(1,6)
        print("dist_num_rsa:", dist_num_rsa.shape)
        # These are the true indices (0:n)
        node_max = int(numpy.max(sa['node'])) # 12
        run_max = len(numpy.unique(sa['run'])) # 3-4
        node_idx = arange(node_max) # 0-11
        row_idx = arange(node_max * run_max) # 0-35 or 0-47
        shuffled_idx = []
        for _ in range(niter):
            random.shuffle(node_idx) # shuffles 1-12
            shuffled = []
            for s in range(run_max): # for s in 0-2 or 0-3
                # Takes the indices 1-12 and randomizes them, and then keeps that consistant for every run (so the ordering of each block of 12 is the same across runs)
                block = row_idx[s*node_max:(s+1)*node_max]
                shuffled.append([block[i] for i in node_idx])
                # shuffled becomes a list of lists where each list is the ordering of a run, and then the code below shuffles the runs
                random.shuffle(shuffled)
            # Flattens the list of lists into one list where the nodes are randomized within runs (consistently) and then the runs are randomized
            shuffled = [item for sublist in shuffled for item in sublist]
            shuffled_idx.append([shuffled,shuffled])
        shuffled_idx
        # We can shuffle the indices and maintain the values for a range of N iterations to sample from and allows us to keep consistent randomizations across searchlight
        self.shuffled_idx_arr = shuffled_idx
        # First iteration is the true index
        self.shuffled_idx_arr[0] = [arange(dist_num_rsa.shape[0]),arange(dist_num_rsa.shape[1])]
        
    def __call__(self, dataset):
    
        self.dsm = rsa.PDist(\
                        square=True,\
                        pairwise_metric=self.metric,\
                        center_data=False)
        
        ### split up the data set into pre and post ###
        dataset = dataset[dataset.sa.phase == 1]
        # Make sure only pre
        run_a = dataset[dataset.sa.run == 1]
        run_b = dataset[dataset.sa.run == 3]
        
        ### calculate the dsm separately for each phase ###
        dsm_run_a = self.dsm(run_a)
        dsm_run_b = self.dsm(run_b)
        dsm_run_a = 1-dsm_run_a.samples
        dsm_run_b = 1-dsm_run_b.samples
        
        ### calculate the difference to determine representational change ###
        dsm_diff = numpy.subtract(arctanh(dsm_run_b),arctanh(dsm_run_a))
        self.tester +=1

        # Don't need below because we do it in random anyway but just in case
        # ### pre-calculate means for efficiency ###
        # onedist_mean = mean(one_dist_values)
        # twodist_mean = mean(two_dist_values)
        # threedist_mean = mean(three_dist_values)
        # fourdist_mean = mean(four_dist_values)        
        # fivedist_mean = mean(five_dist_values)
        
        # edge_nonedge_diff = onedist_mean - 0.25*(twodist_mean + threedist_mean + fourdist_mean + fivedist_mean)
        
        ### calculate the random statistic for N iterations (FIRST IS TRUE VALUES) ###

        rand_stats = []
        for iter in range(self.niter):
            # Recreate the DSM with new indices where self.shuffled_idx_arr is a list of indices of shape iterations X axis CHANGE HERE
            random_dsm = dsm_diff[ix_(self.shuffled_idx_arr[iter][0], self.shuffled_idx_arr[iter][1])]
            
            # # See the init comments near mask for help understanding structure
            # rand_dist1 = random_dsm[self.masks[:,:,0]]
            # rand_dist2 = random_dsm[self.masks[:,:,1]]
            # rand_dist3 = random_dsm[self.masks[:,:,2]]
            # rand_dist4 = random_dsm[self.masks[:,:,3]]
            # rand_dist5 = random_dsm[self.masks[:,:,4]]
            
            # ### pre-calculate means for efficiency (USING NANMEAN BC THERE ARE NAN VALUES BUT SHOULD LOOK INTO) ###
            # # might have to do with arctanh divide by 0 error
            # rand_onedist_mean = numpy.mean(rand_dist1)
            # rand_twodist_mean = numpy.mean(rand_dist2)
            # rand_threedist_mean = numpy.mean(rand_dist3)
            # rand_fourdist_mean = numpy.mean(rand_dist4)        
            # rand_fivedist_mean = numpy.mean(rand_dist5)

            rand_means = numpy.array([numpy.mean(random_dsm[self.masks[:,:,k]]) for k in range(5)])
            # Do edge - non_edge but get the mean of each edge dist with equal weighting
            rand_edge_nonedge_diff = rand_means[0] - 0.25*(rand_means[1] + rand_means[2] + rand_means[3] + rand_means[4])
            rand_stats.append(rand_edge_nonedge_diff)

            # Print commands to check stuff
            if (iter == 0)&(self.tester == 2):
                print("TRUE DIST: \n")
                plt.figure()
                plt.imshow(random_dsm, cmap="viridis", aspect="auto")
                plt.colorbar(label="Value")
                plt.title("Heatmap with True node values")
                plt.show()
                print("init sorted true", numpy.sort(random_dsm.flatten())[0:10])
                print('\n')
            if (iter == 100)&(self.tester==2):
                print("\nmean: ", rand_means[0])
                print("\nmask shape: ", self.masks.shape)
                print("\nrandom_dsm shape: ", random_dsm.shape)
                print("\nrand stat: ",rand_edge_nonedge_diff)
                plt.figure()
                plt.imshow(random_dsm, cmap="viridis", aspect="auto")
                plt.colorbar(label="Value")
                plt.title("Heatmap with shuffled node values")
                plt.show()
                print("init sorted true", numpy.sort(random_dsm.flatten())[0:10])
                print('\n')
                print("\nrandom sorted ", numpy.sort(random_dsm.flatten())[0:10])
        
        # Using Neal's code to get the z-scored p value *****FIND CITATION*****
        perm_stat = perm_z(numpy.array(rand_stats))
        if self.tester ==2:
            print("\nPermutation statistic: ",perm_stat)
        
        return perm_stat