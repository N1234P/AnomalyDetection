import random

import graph_centralities as gc
import martingale as mg
from itertools import combinations
import os
# import simple_dyn_gen as sd
import graph_utils as gu
import AB_loader as AB

# Run one of these methods on a dynamic graph to generate martingale results for many centrality measures
graph_gu = gu.openDynamic("graph_11")





graphs_2 = AB.generate_AB_ChangePoint([1,2,3,4,5,6,7,8,9,10,11,10,9,8,7,6,5,4,3,2], .1) # .1 alpha

graphs = AB.generate_AB_ChangePoint([1,2,3,4,5,6,7,8,9,10,11,10,9,8,7,6,5,4,3,2], .9) # .9 alpha

# graphs = AB.generate_AB_ChangePoint([1,2,3,4,5,6,7,8,9,10,11,10,9,8,7,6,5,4,3,2], .5) # intervals of 1

# graphs = AB.generate_AB_ChangePoint([1,3,6,9,12,15,18,21,24,27,30,27,24,21,18,15,12,9,6,3], .5) # intervals of 3






def undirectedTests(graphs, dirname='1 (.9 alpha)', offset=50, anomalies=[]):
    datas = [
        gc.dynamicCentralities(1, graphs),
       # gc.dynamicCentralities(2, graphs),
        # gc.dynamicCentralities(3, graphs),
       # gc.dynamicCentralities(4, graphs),
        # gc.dynamicCentralities(5, graphs),
       # gc.dynamicCentralities(6, graphs),
        # gc.dynamicCentralities(7, graphs),
       # gc.dynamicCentralities(8, graphs),
       # gc.dynamicCentralities(9, graphs)
    ]

    titles = [
        'degree_centrality',
       # 'closeness_centrality',
        # 'information_centrality',
       # 'harmonic_centrality',
        # 'customDegreeWeighted',
       # 'average_neighbor_degree',
        # 'second_order_centrality',
       #'triangles',
       # 'local_reaching_centrality'
    ]
    print(datas)
    mg.calculateAndSaveManyMartingales(datas=datas, offset=offset, anomalies=anomalies, dirName=dirname, titles=titles)

#undirectedTests(graphs,
#                      anomalies=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500,
#                       1600, 1700, 1800, 1900])

def undirectedEnsembleTests(graphs, dirname, combs, offset=50, anomalies=[]):

    indices = [0, 1, 2, 3, 4, 5]
   # combs = list(combinations(indices, 4))

   #  combs = [(0,3,4,5)]





    datas = [
        gc.dynamicCentralities(1, graphs),
        gc.dynamicCentralities(2, graphs),
        # gc.dynamicCentralities(3, graphs),
        gc.dynamicCentralities(4, graphs),
        # gc.dynamicCentralities(5, graphs),
        gc.dynamicCentralities(6, graphs),
        # gc.dynamicCentralities(7, graphs),
        gc.dynamicCentralities(8, graphs),
        gc.dynamicCentralities(9, graphs)
    ]

    titles = [
        'degree_centrality',
        'closeness_centrality',
        # 'information_centrality',
        'harmonic_centrality',
        # 'customDegreeWeighted',
        'average_neighbor_degree',
        # 'second_order_centrality',
        'triangles',
        'local_reaching_centrality'
    ]

    os.mkdir(dirname)
    os.chdir(dirname)

    for comb in combs:
        print('Starting ' + str(comb))
        currentDatas = []
        currentTitles = []
        for index in comb:
            currentDatas.append(datas[index])
            currentTitles.append(titles[index])
        mg.calculateAndSaveMultiMartingales(datas=currentDatas, offset=offset, filename=str(comb), threshold=10,
                                            epsilon=0.92, anomalies=anomalies, title=str(currentTitles))



undirectedEnsembleTests(graphs, '4 (.9 alpha)', [(0,3,4,5)],
                     anomalies=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500,
                         1600, 1700, 1800, 1900])

undirectedEnsembleTests(graphs_2, '4 (.1= alpha)', [(0,3,4,5)],
                     anomalies=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500,
                         1600, 1700, 1800, 1900])














def directedTests(graphs, dirname='DirectedMartingaleTestResults', offset=50, anomalies=[]):
    datas = [
        gc.dynamicCentralities(1, graphs),
        gc.dynamicCentralities(2, graphs),
        gc.dynamicCentralities(4, graphs),
        gc.dynamicCentralities(5, graphs),
        gc.dynamicCentralities(6, graphs),
        # gc.dynamicCentralities(7, graphs),
        # gc.dynamicCentralities(8, graphs),
        gc.dynamicCentralities(17, graphs),
        gc.dynamicCentralities(18, graphs)
    ]

    titles = [
        'degree_centrality',
        'closeness_centrality',
        'harmonic_centrality',
        'customDegreeWeighted',
        'average_neighbor_degree',
        # 'second_order_centrality',
        # 'triangles',
        'in-degree',
        'out-degree'

    ]

    mg.calculateAndSaveManyMartingales(datas=datas, offset=offset, anomalies=anomalies, dirName=dirname, titles=titles)


def directedEnsembleTests(graphs, dirname='DirectedEnsembleTestResults', offset=50, anomalies=[]):
    indices = [0, 1, 2, 3, 4, 5, 6]
    combs = list(combinations(indices, 3))


    datas = [
        gc.dynamicCentralities(1, graphs),
        gc.dynamicCentralities(2, graphs),
        gc.dynamicCentralities(4, graphs),
        gc.dynamicCentralities(5, graphs),
        gc.dynamicCentralities(6, graphs),
        # gc.dynamicCentralities(7, graphs),
        # gc.dynamicCentralities(8, graphs),
        gc.dynamicCentralities(17, graphs),
        gc.dynamicCentralities(18, graphs)
    ]

    titles = [
        'degree_centrality',
        'closeness_centrality',
        'harmonic_centrality',
        'customDegreeWeighted',
        'average_neighbor_degree',
        # 'second_order_centrality',
        # 'triangles',
        'in-degree',
        'out-degree'

    ]

    os.mkdir(dirname)
    os.chdir(dirname)
    for comb in combs:
        print('Starting ' + str(comb))
        currentDatas = []
        currentTitles = []
        for index in comb:
            currentDatas.append(datas[index])
            currentTitles.append(titles[index])
        mg.calculateAndSaveMultiMartingales(datas=currentDatas, offset=offset, filename=str(comb), threshold=5,
                                            epsilon=0.92, anomalies=anomalies, title=str(comb))






def specifiedEnsembleTests(graphs, concurrentTests, dirname, allTests,
                                     offset=50, anomalies=[]):
    datas = [
        gc.dynamicCentralities(1, graphs),
        gc.dynamicCentralities(2, graphs),
        # gc.dynamicCentralities(3, graphs),
        gc.dynamicCentralities(4, graphs),
        # gc.dynamicCentralities(5, graphs),
        gc.dynamicCentralities(6, graphs),
        # gc.dynamicCentralities(7, graphs),
        gc.dynamicCentralities(8, graphs),
        gc.dynamicCentralities(9, graphs)
    ]
    # [[[graph vals for that centrality measurement ]]]
    titles = [
        'degree_centrality',
        'closeness_centrality',
        # 'information_centrality',
        'harmonic_centrality',
        # 'customDegreeWeighted',
        'average_neighbor_degree',
        # 'second_order_centrality',
        'triangles',
        'local_reaching_centrality'
    ]

    try:
        if allTests and concurrentTests == 2:
            os.mkdir(dirname)
            os.chdir(dirname)

        elif not allTests:
            os.mkdir(dirname)
            os.chdir(dirname)

    except FileExistsError:
        pass

    if concurrentTests > len(datas):
        print("number of concurrent tests specified exceeds dataset length " + str(len(datas)))
        return

    index_centralities = []
    while len(index_centralities) < concurrentTests:
        x = random.randint(0, len(datas) - 1)
        if x not in index_centralities:
            index_centralities.append(x)

    stipulatedDatas = []
    stipulatedTitles = []
    for indice in index_centralities:
        stipulatedDatas.append(datas[indice])
        stipulatedTitles.append(titles[indice])

    mg.calculateAndSaveMultiMartingales(datas=stipulatedDatas, offset=offset, filename=str(tuple(index_centralities)),
                                        threshold=5, epsilon=0.92, anomalies=anomalies, title=str(stipulatedTitles))








def allEnsembleTests(graphs, dataset_length, anomalies=[]):
    for i in range(2, dataset_length + 1):
        print("Starting " + str(i) + " concurrent tests")

        specifiedEnsembleTests(graphs, i, "All Undirected Ensemble Test Results", True, anomalies=anomalies)


# allEnsembleTests(loaded_graph, 6,
#                           anomalies=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500,
#                                      1600, 1700, 1800, 1900])
