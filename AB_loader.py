import os

import numpy as np
import networkx as nx
from matplotlib import pyplot, patches
import pylab as plt
import dateutil.parser as dparser
import re
import random
import graph_utils as gu
# m is the Number of edges to attach from a new node to existing node
def AB_snapshot(G_prev, alpha, m):
    '''
    Does not run individually, use generate_AB_ChangePoint to get graphs
    :param G_prev: Uses a previous graph to modify the next timestep graph
    :param alpha: Will determine if the number of edges in a graph at a particular timestep needs to be altered
    :param m: Number of edges created along each node upon generation
    :return: Graph at the current timestep that has been generated using previous graph modification
    '''
    G_t = G_prev.copy()
    n = len(G_t)
    G_new = nx.barabasi_albert_graph(n, m)
    if (alpha == 1.0):
        return G_new

    for i in range(0, n):
        for j in range(i + 1, n):
            prob = random.uniform(0, 1)
            if (prob <= alpha):
                if (G_new.has_edge(i, j) and not G_t.has_edge(i, j)):
                    G_t.add_edge(i, j)
                if (not G_new.has_edge(i, j) and G_t.has_edge(i, j)):
                    G_t.remove_edge(i, j)


    return G_t





def generate_AB_ChangePoint(m_list, alpha, n=100, seed=0, outname="ab_graph_1"):
    '''

    :param m_list: A list of m values, which will determine how many edges will be created for each node when a timestep t graph is generated (length should be 1 greater than number of anomalies)
    :param alpha: Once the barasbasi albert graph is generated, this value will be used for the snapshot function above to determine edge creation, removal chance for the next graph
    :param n: Number of nodes each graph at all timesteps will have
    :param seed: unique value for graph generation
    :param outname: file where the graphs will be stored
    :return:
    '''

    random.seed(seed)
    np.random.seed(seed)



    cps=[100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900]


    if (len(m_list) <= len(cps)):
        raise Exception("there should be " + str(len(cps) + 1) + " m values for " + str(len(cps)) + " change points")


    fname = outname

    maxt = 2000
    p_idx = 0
    G_0 = nx.barabasi_albert_graph(n, m_list[p_idx])
    G_0 = nx.Graph(G_0)
    G_t = G_0
    G_times = []
    G_times.append(G_t)

    for t in range(maxt):
        if (t in cps):
            p_idx = p_idx + 1
            p = m_list[p_idx]
            G_t = AB_snapshot(G_t, alpha, p)
            G_times.append(G_t)
            #plot_degree_dis(G_t, t)
            print ("generating " + str(t), end="\r")

        else:
            p = m_list[p_idx]
            G_t = AB_snapshot(G_t, alpha, p)
            G_times.append(G_t)
            print ("generating " + str(t), end="\r")

    return G_times

