'''
Original Code: Alex Lam
Modified By: Kiefer Montenero
This code will generate directed graphs from the Philadelphia bikesharing data and store them as a list of DiGraphs
'''
import csv
import networkx as nx
import os

def getNodes():
    filepathData = 'DC_Stations.csv'
    data = open(filepathData)
    routeReader = csv.DictReader(data)
    ids = []
    dict = {}
    altDict = {}
    for line in routeReader:
        ids.append(int(line['station_id']))
        dict[line['station_name']] = int(line['station_id'])
        altDict[line['alt_name']] = int(line['station_id'])
    return (ids, dict, altDict)



filenames = []


def getGraphs():
    # CSV file
    baseStartPath = '../2020-recentNew/'
    baseEndPath = '-capitalbikeshare-tripdata.csv'

    years = ['2019', '2020', '2021']
    monthss = [['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'], ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'], ['01']]
    monthEnds = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    days = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31']

    #Create an empty list of stations (nodes) Goes from ??
    stuff = getNodes()
    nodes = stuff[0]
    dict = stuff[1]
    altDict = stuff[2]
##########################################################
    # List to hold all DiGraphs.  Each day is one DiGraph.
    graphs = []
    for k in range(len(years)):
        for i in range(len(monthss[k])):
            baseStartPath = '../2020-recentNew/'
            startDate = 'started_at'
            startStation ='start_station_name'
            endStation = 'end_station_name'
            if ((years[k] == '2019') or ((years[k] == '2020') and (int(monthss[k][i]) <= 3))):
                startDate = 'Start date'
                startStation = 'Start station'
                endStation = 'End station'
                baseStartPath = '../2019-2020Old/'

            filepathData = baseStartPath + years[k] + monthss[k][i] + baseEndPath
            data = open(filepathData)
            routeReader = csv.DictReader(data)
            for j in range(1, monthEnds[i] + 1):
                #Add a DiGraph to the list
                graphs.append(nx.DiGraph())
                #Set up DiGraph with all nodes - We want all instances to have same number of nodes, even if some have no edges
                graphs[-1].add_nodes_from(nodes)
                if j <= 9:
                    date = str(years[k]) + '-' + str(monthss[k][i]) + '-0' + str(j)
                    filenames.append(date)
                else:
                    date = str(years[k]) + '-' + str(monthss[k][i]) + '-' + str(j)
                    filenames.append(date)

                for line in routeReader:
                    if (line[startDate][:10] == date):
                        startNodeStr = line[startStation]
                        endNodeStr = line[endStation]
                        if startNodeStr in dict.keys():
                            startNodeStr = str(dict[startNodeStr])
                        elif startNodeStr in altDict.keys():
                            startNodeStr = str(altDict[startNodeStr])
                        else:
                            startNodeStr = '1'

                        if endNodeStr in dict.keys():
                            #print('its in')
                            endNodeStr = str(dict[endNodeStr])
                        elif endNodeStr in altDict.keys():
                            endNodeStr = str(altDict[endNodeStr])
                        else:
                            endNodeStr = '2'

                        if startNodeStr != '' and endNodeStr != '':
                            startNode = int(startNodeStr)
                            endNode = int(endNodeStr)
                            if graphs[-1].has_edge(startNode, endNode):
                                graphs[-1][startNode][endNode]['weight'] += 1
                            else:
                                graphs[-1].add_edge(startNode, endNode, weight = 1)

                data = open(filepathData)
                routeReader = csv.DictReader(data)
                print('Done Day ' + str(j))
            print('Done Month ' + monthss[k][i])

    return graphs

graphs = getGraphs()
os.mkdir('EverythingAllAtOnceDirected')
for i in range(len(graphs)):
    nx.write_gexf(graphs[i],'EverythingAllAtOnceDirected/' + filenames[i] + '.gexf')