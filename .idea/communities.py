import community as community_louvain
import networkx as nx
import csv

#Partitions graph and returns list of list of nodes
def partitionGraph(graph):
    partition = community_louvain.best_partition(graph)
    nodeLists = []
    for node in partition.keys():
        while(len(nodeLists) - 1 < partition[node]):
            nodeLists.append([])
    for node in partition.keys():
        nodeLists[partition[node]].append(node)
    return nodeLists

#For mapping nodes to longs and lats using csv file
def getNodeToLocDict(file):
    data = open(file)
    routeReader = csv.DictReader(data)
    dict = {}
    for line in routeReader:
        dict[line['station_id']] = (float(line['station_long']), float(line['station_lat']))
    return dict

#Will always partition into a rectangle/square of partitions
#Number of total partitions is numXPartitions * numYPartitions
def partitionGraphByLoc(graph, numXPartitions, numYPartitions, nodeToLocDict):
    minLong = list(nodeToLocDict.values())[0][0]
    minLat = list(nodeToLocDict.values())[0][1]
    maxLong = minLong
    maxLat = minLat
    for value in nodeToLocDict.values():
        if value[0] < minLong:
            minLong = value[0]
        if value[0] > maxLong:
            maxLong = value[0]
        if value[1] < minLat:
            minLat = value[1]
        if value[1] > maxLat:
            maxLat = value[1]
    longRange = maxLong - minLong
    latRange = maxLat - minLat
    longBlockSize = longRange / numXPartitions
    latBlockSize = latRange / numYPartitions
    partitions = []
    nodePartitions = []
    xRange = (0, 0)
    yRange = (0, 0)
    for x in range(numXPartitions):
        xRange = (((x * longBlockSize) + minLong), (((x + 1) * longBlockSize) + minLong))
        for y in range(numYPartitions):
            nodePartitions.append([])
            yRange = (((y * latBlockSize) + minLat), (((y + 1) * latBlockSize) + minLat))
            partitions.append((xRange[0], xRange[1], yRange[0], yRange[1]))
    for node in graph.nodes():
        if nodeToLocDict[node][0] == partitions[-1][1] or nodeToLocDict[node][1] == partitions[-1][3]:
            nodePartitions[-1].append(node)
        for i in range(len(partitions)):
            if nodeToLocDict[node][0] >= partitions[i][0] and nodeToLocDict[node][0] < partitions[i][1] and nodeToLocDict[node][1] >= partitions[i][2] and nodeToLocDict[node][1] < partitions[i][3]:
                nodePartitions[i].append(node)
    return nodePartitions

#Grabs a subset of nodes within a radius, centered at lat, long
def partitionByRadius(graph, lat, long, radius, nodeToLocDict):
    nodes = []
    center = (lat, long)
    for node in graph.nodes():
        point = (nodeToLocDict[node][1], nodeToLocDict[node][0])
        distance = (((point[1] - center[1]) ** 2) + ((point[0] - center[0]) ** 2)) ** (1/2)
        if distance <= radius:
            nodes.append(node)
    return nodes

#Applies full graph edge data to a subset of nodes, only adding edges that existed between them beforehand
def nodeListToGraph(nodeList, graph):
    newGraph = nx.Graph()
    newGraph.add_nodes_from(nodeList)
    newGraph.add_weighted_edges_from((graph.subgraph(nodeList)).edges.data('weight'))
    return newGraph

#Apply nodeListToGraph on many nodelists
def nodeListsToGraphs(nodeLists, graph):
    subgraphs = []
    for nodeList in nodeLists:
        subgraphs.append(nx.Graph())
        subgraphs[-1].add_nodes_from(nodeList)
        subgraphs[-1].add_weighted_edges_from((graph.subgraph(nodeList)).edges.data('weight'))
    return subgraphs

#Method to call for basic paritioning, returns subgraphs
def getSubgraphs(graph):
    return nodeListsToGraphs(partitionGraph(graph), graph)

#Turns a dynamic graph into multiple dynamic subgraphs
def getDynSubgraphs(graphs):
    nodeLists = partitionGraph(graphs[0])
    dynSubgraphs = []
    for nodeList in nodeLists:
        dynSubgraphs.append([])
    for graph in graphs:
        subgraphs = nodeListsToGraphs(nodeLists, graph)
        for i in range(len(subgraphs)):
            dynSubgraphs[i].append(subgraphs[i])
    return dynSubgraphs

#Tuns a dynamic graph into multiple dynamic subgraphs, partitioned based on location data
def getDynSubgraphsLoc(graphs, numXPartitions, numYPartitions, nodeToLocDict):
    nodeLists = partitionGraphByLoc(graphs[0], numXPartitions, numYPartitions, nodeToLocDict)
    dynSubgraphs = []
    for nodeList in nodeLists:
        dynSubgraphs.append([])
    for graph in graphs:
        subgraphs = nodeListsToGraphs(nodeLists, graph)
        for i in range(len(subgraphs)):
            dynSubgraphs[i].append(subgraphs[i])
    return dynSubgraphs

#Tuns a dynamic graph into multiple dynamic subgraphs, partitioned based on location data
def getDynSubLocRad(graphs, lat, long, radius, nodeToLocDict):
    nodeList = partitionByRadius(graphs[0], lat, long, radius, nodeToLocDict)
    newGraphs = []
    for graph in graphs:
        newGraphs.append(nodeListToGraph(nodeList, graph))
    return newGraphs