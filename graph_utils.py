import networkx as nx

import matplotlib.pyplot as plt

import os
import numpy as np

from sklearn.manifold import TSNE

os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"

#Useful to import to other scripts
#Various methods for dealing with dynamic graph saving, loading, viewing, converting from directed to undirected, etc.

def save(graph, fileName):
    nx.write_weighted_edgelist(graph, fileName)

def saveDynamic(graphs, newDirName):
    os.mkdir(newDirName)
    for i in range(len(graphs)):
        save(graphs[i], newDirName + '/' + str(i))

def saveGexfDynamic(graphs, newDirName, filenames = []):
    os.mkdir(newDirName)
    if len(filenames) == 0:
        for i in range(len(graphs)):
            filenames.append(str(i))
    for i in range(len(graphs)):
        nx.write_gexf(graphs[i], newDirName +'/' + filenames[i])

def saveUnweighted(graph, fileName):
    nx.write_edgelist(graph, fileName, data=False)

def openGraph(fileName):
    return nx.read_weighted_edgelist(fileName, nodetype=int)

def openDynamic(dirName, start = 0):
    graphs = []
    for i in range(start, len(os.listdir(dirName)) + start):
        graphs.append(openGraph(dirName + '/' + str(i)))
    return graphs

def openGexfDynamic(dirName):
    graphs = []
    for file in sorted(os.listdir(dirName)):
        graphs.append(nx.read_gexf(dirName + '/' + file))
    return graphs
def openGexf(file):
    return nx.read_gexf(file)

def show(graph):
    widths = []
    for (u, v) in graph.edges():
        widths.append(graph.edges[u,v]['weight'])
    pos = nx.spring_layout(graph)
    nx.draw(graph, pos=pos, width = widths, with_labels=True)
    plt.show()

def getDiGraphs(graphs):
    newGraphs = []
    for i in range(len(graphs)):
        G = nx.DiGraph(graphs[i])
        newGraphs.append(G)
    return newGraphs

def saveEmb(emb, filePath):
    file = open(filePath, "w+")
    for i in range(len(emb)):
        line = str(i) + ' '
        for num in emb[i]:
            line = line + str(num) + ' '
        file.write(line + '\n')
    file.close()

def saveEmbs(embs, dirName, start = 0):
    if not os.path.isdir(dirName):
        os.mkdir(dirName)
    for i in range(len(embs)):
        saveEmb(embs[i], dirName + '/' + str(i + start))

def openEmb(filePath):
    embDict = {}
    file = open(filePath, "r")
    for line in file:
        data = line.split(' ')
        nums = []
        if len(data) <= 2:
            pass
        else:
            for num in data[1:]:
                thing = num.split('.')[0].strip('-')
                if thing.isdigit():
                    nums.append(float(num))
            embDict[int(data[0])] = nums
    return embDict

def openEmbs(dirName):
    embs = []
    for file in os.listdir(dirName):
        embs.append(openEmb(dirName + '/' + file))
    return embs

def dictToList(dict):
    list = []
    for i in range(len(dict.keys())):
        list.append(dict[i])
    return list

def dictsToList(dicts):
    list = []
    for dict in dicts:
        list.append(dictToList(dict))
    return list[0]

def getListNorm(list):
    return np.linalg.norm(list, 'fro')

def getListNormDiff(list1, list2):
    return (abs(getListNorm(list1) - getListNorm(list2)))

def getEmbDiff(emb1, emb2):
    return getListNormDiff(dictToList(emb1), dictToList(emb2))

def matToList(matrix):
    return np.array(matrix)

def getGraphDiff(graph1, graph2):
    return getListNormDiff(nx.to_numpy_array(graph1), nx.to_numpy_array(graph2))

def getEmbDiffSequence(embs):
    diffSequence = [0]
    for i in range(1, len(embs)):
        diffSequence.append(getEmbDiff(embs[i - 1], embs[i]))
    return diffSequence

def getGraphDiffSequence(graphs):
    diffSequence = [0]
    for i in range(1, len(graphs)):
        diffSequence.append(getGraphDiff(graphs[i - 1], graphs[i]))
    return diffSequence

def reduceEmbDim(embDict):
    if len(embDict[0]) > 2:
        print("Embedding dimension greater than 2, using tSNE to reduce it to 2")
        model = TSNE(n_components=2, random_state=42)
        embList = []
        for i in range(len(embDict.keys())):
            embList.append(embDict[i])
        reducedEmb = model.fit_transform(embList)
        reducedEmbDict = {}
        for i in range(len(reducedEmb)):
            reducedEmbDict[i] = reducedEmb[i]
        return reducedEmbDict

def reduceEmbsDim(embDicts):
    embs = []
    for embDict in embDicts:
        embs.append(reduceEmbDim(embDict))
    return embs

def directedToUndirected(diGraph):
    newGraph = nx.Graph()
    newGraph.add_nodes_from(diGraph)
    for (u, v) in diGraph.edges():
        if newGraph.has_edge(u, v):
            newGraph.edges[u,v]['weight'] = newGraph.edges[u,v]['weight'] + diGraph.edges[u, v]['weight']
        else:
            newGraph.add_edge(u, v)
            newGraph.edges[u,v]['weight'] = diGraph.edges[u, v]['weight']
    return newGraph

def dynamicDirectedToUndirected(diGraphs):
    graphs = []
    for diGraph in diGraphs:
        graphs.append(directedToUndirected(diGraph))
    return graphs