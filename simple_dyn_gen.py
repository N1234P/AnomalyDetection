import networkx as nx
import random

import copy
import os
import numpy as np
from itertools import combinations, product


os.environ["QT_LOGGING_RULES"] = "qt5ct.debug=false"

#Useful for generation of simple dynamic graphs
#Primarily used for martingale testing on synthetic data

def keepBounds(weight):
    if weight < 0:
        return 0
    elif weight > 1:
        return 1
    return weight

#Generate and return a random weighted graph
def generate(numNodes, edgeCreationChance):
    g = nx.erdos_renyi_graph(numNodes, edgeCreationChance)
    for (u, v) in g.edges():
        weight = keepBounds(round(np.random.normal(0.5, 0.25), 3))
        if(weight == 0):
            g.remove_edge(u, v)
        else:
            g.edges[u,v]['weight'] = weight
    return g

#Generate and return a random weighted graph made of numSub subgraphs
def generateSubgraphs(numNodesPerSub, numSub, edgeCreationChance):
    subgraphs = []
    for i in range(numSub):
        subgraphs.append(generate(numNodesPerSub, edgeCreationChance))
    g = subgraphs[0]
    for i in range(numSub - 1):
        g = nx.disjoint_union(g, subgraphs[i])

    return g


def diffSubgraph(node1, node2, numSub, numNodes):
    node1Val = -1
    node2Val = -1
    groups = []
    for i in range(numSub):
        groups.append(range(i * int(numNodes/numSub),(i + 1) * int(numNodes/numSub)))
    for i in range(len(groups)):
        if node1 in groups[i]:
            node1Val = i
        if node2 in groups[i]:
            node2Val = i
    return (not (node1Val == node2Val))


def evolveSubgraphsNew(graph, numSub, edgeEvolveChances, addVols, subVols, connectionProb, disconnectProb):
    newGraph = copy.deepcopy(graph)
    newSubgraphs = []
    #print(nx.get_edge_attributes(newGraph, 'weight'))

    for i in range(numSub):
        newSubgraphs.append(nx.Graph())
        newSubgraphs[-1].add_nodes_from(range(int(len(newGraph.nodes()) / numSub) * i, int(len(newGraph.nodes()) / numSub) * (i + 1)))
        newSubgraphs[-1].add_weighted_edges_from((newGraph.subgraph(range(int(len(newGraph.nodes()) / numSub) * i, int(len(newGraph.nodes()) / numSub) * (i + 1)))).edges.data('weight'))
    #print(nx.get_edge_attributes(newSubgraphs[0], 'weight'))

    for i in range(len(newSubgraphs)):
        newSubgraphs[i] = evolve(newSubgraphs[i], edgeEvolveChances[i], addVols[i], subVols[i])
        #print('evolving subgraph ' + str(i) + ' with ' +str(edgeEvolveChances[i]) + ', ' + str(addVols[i]) + ', ' + str(subVols[i]))

    g = newSubgraphs[0]
    for i in range(1, numSub):
        #print("im adding " + str(i))
        g = nx.disjoint_union(g, newSubgraphs[i])
    savedPairs = []
    for i in range(numSub):
        for j in range(numSub):
            if i != j:
                possConnections = list(product(range(i * int(len(newGraph.nodes()) / numSub), (i + 1) * int(len(newGraph.nodes()) / numSub)), range(j * int(len(newGraph.nodes()) / numSub), (j + 1) * int(len(newGraph.nodes()) / numSub))))
                for nodePair in possConnections:
                    if newGraph.has_edge(nodePair[0], nodePair[1]) and diffSubgraph(nodePair[0], nodePair[1], numSub, len(graph.nodes())):
                        savedPairs.append(nodePair)
    #print('\n\n')
    #print(savedPairs)
    for nodePair in savedPairs:
        g.add_weighted_edges_from([(nodePair[0], nodePair[1], newGraph.edges[nodePair[0], nodePair[1]]['weight'])])

    for i in range(numSub):
        for j in range(numSub):
            if i != j:
                possConnections = list(product(range(i * int(len(newGraph.nodes()) / numSub), (i + 1) * int(len(newGraph.nodes()) / numSub)), range(j * int(len(newGraph.nodes()) / numSub), (j + 1) * int(len(newGraph.nodes()) / numSub))))
                numConnections = 0
                maxConnections = int(len(possConnections) / 10)
                for nodePair in possConnections:
                    #print (nodePair)
                    if g.has_edge(nodePair[0], nodePair[1]):
                        numConnections += 1
                        g.edges[nodePair[0],nodePair[1]]['weight'] = g.edges[nodePair[0],nodePair[1]]['weight'] + round(np.random.normal(0, 0.2), 3)
                        g.edges[nodePair[0],nodePair[1]]['weight'] = round(keepBounds(g.edges[nodePair[0],nodePair[1]]['weight']), 3)
                        if(g.edges[nodePair[0],nodePair[1]]['weight'] == 0):
                            if len(g.edges(nodePair[0])) == 1 or len(g.edges(nodePair[1])) == 1:
                                print('wow saved from weight death on connection edge')
                                g.edges[nodePair[0],nodePair[1]]['weight'] = keepBounds(round(np.random.normal(0.15, 0.03), 3))
                            else:
                                g.remove_edge(nodePair[0], nodePair[1])
                for nodePair in possConnections:
                    if not g.has_edge(nodePair[0], nodePair[1]) and numConnections < maxConnections:
                        if random.randint(1, 100) <= int((connectionProb * 100) / 2):
                            g.add_edge(nodePair[0], nodePair[1])
                            g.edges[nodePair[0], nodePair[1]]['weight'] = round(np.random.normal(0.15, 0.03), 3)
                            numConnections += 1
                    if g.has_edge(nodePair[0], nodePair[1]):
                        if g.edges[nodePair[0], nodePair[1]]['weight'] < 0.5:
                            if random.randint(1, 100) <= (disconnectProb * 100):
                                if len(g.edges(nodePair[0])) == 1 or len(g.edges(nodePair[1])) == 1:
                                    print('wow saved from random deletion connection edge')
                                    g.edges[nodePair[0],nodePair[1]]['weight'] = keepBounds(round(np.random.normal(0.5, 0.25), 3))
                                else:
                                    g.remove_edge(nodePair[0], nodePair[1])
    return g

def evolve(graph, edgeEvolveChance, addVol, subVol):
    newGraph = copy.deepcopy(graph)
    for (u, v) in newGraph.edges():
        if random.randint(1, 100) <= (edgeEvolveChance * 100):
            newGraph.edges[u,v]['weight'] = newGraph.edges[u,v]['weight'] + round(np.random.normal(0, 0.1), 3)
            newGraph.edges[u,v]['weight'] = round(keepBounds(newGraph.edges[u,v]['weight']), 3)
            if(newGraph.edges[u,v]['weight'] == 0):
                if len(newGraph.edges(u)) == 1 or len(newGraph.edges(v)) == 1:
                #    print('wow saved from weight death')
                    newGraph.edges[u,v]['weight'] = keepBounds(round(np.random.normal(0.5, 0.25), 3))
                else:
                    newGraph.remove_edge(u, v)
    for nodePair in combinations(newGraph.nodes(), 2):
        if not newGraph.has_edge(nodePair[0], nodePair[1]):
            if random.randint(1, 100) <= (addVol * 100):
                newGraph.add_edge(nodePair[0], nodePair[1])
                newGraph.edges[nodePair[0], nodePair[1]]['weight'] = round(np.random.normal(0.15, 0.03), 3)
        else:
            if newGraph.edges[nodePair[0], nodePair[1]]['weight'] < 0.5:
                if random.randint(1, 100) <= (subVol * 100):
                    if len(newGraph.edges(nodePair[0])) == 1 or len(newGraph.edges(nodePair[1])) == 1:
                    #    print('wow saved from random deletion')
                        newGraph.edges[nodePair[0],nodePair[1]]['weight'] = keepBounds(round(np.random.normal(0.5, 0.25), 3))
                    else:
                        newGraph.remove_edge(nodePair[0], nodePair[1])
    return newGraph


def multipleEvolveShow(graph, edgeEvolveChance, addVol, subVol, numSteps, anomalies):
    save(graph, '0')
    printInfo(graph, 'TimeStep 0')
    #show(graph)
    for i in range(1, numSteps + 1):
        if i in anomalies:
            graph = evolve(graph, 0.3, 0.2, 0.5)
        else:
            graph = evolve(graph, edgeEvolveChance, addVol, subVol)
        save(graph, str(i))
        printInfo(graph, 'TimeStep ' + str(i))
        #show(graph)


def checkIndexing(graph):
    numeric_indices = [index for index in range(graph.number_of_nodes())]
    node_indices = sorted([node for node in graph.nodes()])
    print(numeric_indices)
    print(node_indices)

def getRandDynGraph(numNodes, numTimesteps, numAnomalies):
    graph = generate(numNodes, 0.4)
    graphs = [graph]
    index = 0
    for i in range(numAnomalies + 1):
        num = ((random.randint(0, 9) / 10), (random.randint(0, 9) / 10), (random.randint(0, 9) / 10))
        print('New parameters picked at timestep ' + str(index))
        print(num)
        for j in range(int(numTimesteps / (numAnomalies + 1))):
            graphs.append(evolve(graphs[index - 1], num[0], num[1], num[2]))
            index += 1
            for i in range(0, numNodes):
                if(len(graphs[-1].edges(i)) == 0):
                    print('Broken Timestep ' + str(j))
    return graphs

def getRandDynSubGraph(numNodesPerSub, numSub, numTimesteps, numAnomalies, connectionProb, disconnectionProb):
    graph = generateSubgraphs(numNodesPerSub, numSub, 0.6)
    graphs = [graph]
    index = 0
    params = []
    for j in range(numSub):
        num = ((random.randint(0, 9) / 10), (random.randint(0, 9) / 10), (random.randint(0, 9) / 10))
        params.append(num)
    for i in range(numAnomalies + 1):
        num = ((random.randint(0, 9) / 10), (random.randint(0, 9) / 10), (random.randint(0, 9) / 10))
        paramIndex = random.randint(0, numSub-1)

        while (abs(num[0] - params[paramIndex][0]) + abs(num[1] - params[paramIndex][1]) + abs(num[2] - params[paramIndex][2])) < 1:
            num = ((random.randint(0, 9) / 10), (random.randint(0, 9) / 10), (random.randint(0, 9) / 10))
        params[paramIndex] = num
        print("Subgraph " + str(paramIndex) + " got anomaly at timestep " + str(index))

        edgeEvolveChances = []
        addVols = []
        subVols = []
        for paramSet in params:
            edgeEvolveChances.append(paramSet[0])
            addVols.append(paramSet[1])
            subVols.append(paramSet[2])

        for j in range(int(numTimesteps / (numAnomalies + 1))):
            graphs.append(evolveSubgraphsNew(graphs[index - 1], numSub, edgeEvolveChances, addVols, subVols, connectionProb, disconnectionProb))
            index += 1
            #for i in range(0, numNodes):
                #if(len(graphs[-1].edges(i)) == 0):
                    #print('Broken Timestep ' + str(j))
        for param in params:
            print(param)

    return graphs

def getDynGraph(numNodes):
    graph = generate(numNodes, 0.3)
    graphs = [graph]
    for i in range(1, 50):
        graphs.append(evolve(graphs[i - 1], 0.1, 0.1, 0.1))
    for i in range(50, 100) :
        graphs.append(evolve(graphs[i - 1], 0.9, 0.9, 0.9))
    for i in range(100, 150) :
        graphs.append(evolve(graphs[i - 1], 0.5, 0.1, 0.5))
    for i in range(150, 200) :
        graphs.append(evolve(graphs[i - 1], 0.5, 0.7, 0))
    return graphs