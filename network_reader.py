from os import listdir
from os.path import isfile, join
from functools import reduce
from operator import add

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('ggplot')

mypath = 'piazza/'
onlyfiles = [os.path.splitext(f)[0] for f in listdir(mypath) if isfile(join(mypath, f))]

centralities = {}
student_centralities = {}

def Centralities(G):
    # betweenness (how often they appear on route between other students)
    # Betweenness centrality of a node v is the sum of the fraction of all-pairs shortest paths that pass through v
    b = nx.centrality.betweenness_centrality(G)
    b = reduce(add, b.values()) / len(b)

    # closeness (how many other students have a short path to that node)
    # Closeness centrality of a node u is the reciprocal of the average shortest path distance to u over all n-1 reachable nodes.
    c = nx.centrality.closeness_centrality(G)
    c = reduce(add, c.values()) / len(c)

    # degree (number of connections they have)
    # The degree centrality for a node v is the fraction of nodes it is connected to.
    d = nx.centrality.degree_centrality(G)
    d = reduce(add, d.values()) / len(d)

    # avr. weighted degree
    w = dict(nx.degree(G, weight='weight'))
    w = reduce(add, w.values()) / len(w)

    return (b, c, d, w)


for file in onlyfiles:
    print(file)
    G = nx.read_gexf(join(mypath, file + '.gexf'))
    scores = Centralities(G)
    centralities[file] = scores
    print(scores)

    # create student only subgraph
    students = G.copy()
    roles = nx.get_node_attributes(G, 'color')
    values = set(roles.values())
    students.remove_nodes_from([node for node, role in roles.items() if not role == 'student'])
    roles = nx.get_node_attributes(students, 'color')
    values = set(roles.values())
    scores = Centralities(students)
    student_centralities[file] = scores
    print(scores)

print(centralities)

def PlotCentrality(idx, centralities, student_centralities, name):
    ind = np.arange(len(centralities.keys())) 
    width = 0.35       
    plt.bar(ind, [centralities[idx] for (_, centralities) in centralities.items()], width, label='All users')
    plt.bar(ind + width, [centralities[idx] for (_, centralities) in student_centralities.items()], width,
        label='Students only')

    plt.ylabel(name)
    plt.title(name + 'by class and role')

    plt.xticks(ind + width / 2, onlyfiles, rotation=45)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig(name + '.png')
    plt.show()

PlotCentrality(0, centralities, student_centralities, 'Betweenness Centrality')
PlotCentrality(1, centralities, student_centralities, 'Closeness Centrality')
PlotCentrality(2, centralities, student_centralities, 'Degree Centrality')
PlotCentrality(3, centralities, student_centralities, 'Avr. Weighted Degree')