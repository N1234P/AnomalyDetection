import networkx as nx
import inspect

#Methods for getting centralities from graphs and using them in martingale

def customDegreeWeighted(graph):
    nodeDict = {}
    for node in graph.nodes():
        totalWeight = 0
        for edge in graph.edges(node, data=True):
            totalWeight += edge[2]['weight']
        nodeDict[node] = totalWeight
    return nodeDict

def local_reaching_centrality(graph):
    nodeDict = {}
    for node in sorted(graph.nodes):
        nodeDict[node] = nx.local_reaching_centrality(graph, node)
    return nodeDict

centralities = {
    1 : nx.degree_centrality, #Great
    2 : nx.closeness_centrality, #Great
    3 : nx.information_centrality, #Only undirected NEEDS connected
    4 : nx.harmonic_centrality, #Great
    5 : customDegreeWeighted, #Ok
    6 : nx.average_neighbor_degree, #Good
    7 : nx.second_order_centrality, #only undirected
    8 : nx.triangles, #only undirected (Similar to generalized degree)
    9 : local_reaching_centrality, #only undirected Great

    #10 : nx.structuralholes.constraint, #Takes Long Time
    #11 : nx.structuralholes.effective_size #Takes Long Time
    #12 : nx.closeness_vitality, #Takes Long Time
    #13 : nx.eigenvector_centrality, #BAD
    #14 : nx.betweenness_centrality, #BAD
    #15 : nx.eccentricity, #BAD
    #16 : nx.pagerank, #BAD

    17 : nx.in_degree_centrality, #Uncomment if graph is directed
    18 : nx.out_degree_centrality, #Uncomment if graph is directed

    #19 : nx.katz_centrality, #Sometimes PowerIteration Fails to Converge - BAD
    #20 : nx.global_reaching_centrality, #Returns a double - Turns graph into a double - Probably not enough info mantained to be useful
    #21 : nx.percolation_centrality, #Requires states parameter == Needs attributed nodes with 0.0 - 1.0 value
}


def getCentrality(num, graph):
    if 'weight' in inspect.getfullargspec(centralities[num])[0]:
        print('Weight parameter detected')
        return centralities[num](graph, weight = 'weight')

    return centralities[num](graph)

def dictToSortedList(dict):
    list = []
    for key in sorted(dict.keys()):
        list.append(dict[key])
    return list

def dynamicCentralities(num, graphs):
    centralities = []
    i = 0

    for graph in graphs:
        print('Getting centrality ' + str(i))
        i+=1
        centralities.append(dictToSortedList(getCentrality(num, graph)))

    return centralities

