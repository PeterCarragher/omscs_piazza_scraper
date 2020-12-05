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
onlyfiles = [os.path.splitext(f)[0]
             for f in listdir(mypath) if isfile(join(mypath, f))]

centralities = {}
student_centralities = {}
student_centralities_normalised = {}

# manually scraped from OSCAR
class_sizes = {'CS6460-SP': 212,
               'CS6460-SU': 171,
               'CS6750-SP': 437,
               'CS6750-SU': 504,
               'CS7637-SP': 557,
               'CS7637-SU': 376,
               'CS7646-SP': 691,
               'CS7646-SU': 841,
               }


def Centralities(G, normalise_file=None):
    num_nodes = G.number_of_nodes()
    if (normalise_file is not None):
        num_nodes = class_sizes[normalise_file]

    # betweenness (how often they appear on route between other students)
    # Betweenness centrality of a node v is the sum of the fraction of all-pairs shortest paths that pass through v
    b = nx.centrality.betweenness_centrality(G)
    b = reduce(add, b.values()) / num_nodes

    # closeness (how many other students have a short path to that node)
    # Closeness centrality of a node u is the reciprocal of the average shortest path distance to u over all n-1 reachable nodes.
    c = nx.centrality.closeness_centrality(G)
    c = reduce(add, c.values()) / num_nodes

    # degree (number of connections they have)
    # The degree centrality for a node v is the fraction of nodes it is connected to.
    d = nx.centrality.degree_centrality(G)
    d = reduce(add, d.values()) / num_nodes

    # degree (number of connections they have)
    # The degree centrality for a node v is the fraction of nodes it is connected to.
    i = nx.centrality.in_degree_centrality(G)
    i = reduce(add, i.values()) / num_nodes

    # degree (number of connections they have)
    # The degree centrality for a node v is the fraction of nodes it is connected to.
    o = nx.centrality.out_degree_centrality(G)
    o = reduce(add, o.values()) / num_nodes

    # avr. weighted degree
    w = dict(nx.degree(G, weight='weight'))
    w = reduce(add, w.values()) / num_nodes

    return (b, c, d, i, o, w)


for file in onlyfiles:
    print(file)
    G = nx.read_gexf(join(mypath, file + '.gexf'))
    print(G.number_of_nodes())
    centralities[file] = Centralities(G)

    # create student only subgraph
    students = G.copy()
    roles = nx.get_node_attributes(G, 'color')
    values = set(roles.values())
    students.remove_nodes_from(
        [node for node, role in roles.items() if not role == 'student'])
    roles = nx.get_node_attributes(students, 'color')
    values = set(roles.values())
    student_centralities[file] = Centralities(students)

    # get normalised scores
    student_centralities_normalised[file] = Centralities(students, file)


print(centralities)


def PlotCentrality(idx, centralities, student_centralities, name):
    ind = np.arange(len(centralities.keys()))
    width = 0.25
    plt.bar(ind, [centralities[idx] for (_, centralities)
                  in centralities.items()], width, label='All users')
    plt.bar(ind + width, [centralities[idx] for (_, centralities) in student_centralities.items()], width,
            label='Students only')
    plt.bar(ind + width*2.0, [centralities[idx] for (_, centralities) in student_centralities_normalised.items()], width,
            label='Students only (norm)')

    plt.ylabel(name)
    plt.title(name + ' by class and role')

    plt.xticks(ind + width / 2, onlyfiles, rotation=45)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig(name + '.png')
    plt.show()


PlotCentrality(0, centralities, student_centralities, 'Betweenness Centrality')
PlotCentrality(1, centralities, student_centralities, 'Closeness Centrality')
PlotCentrality(2, centralities, student_centralities, 'Degree Centrality')
PlotCentrality(3, centralities, student_centralities, 'In Degree Centrality')
PlotCentrality(4, centralities, student_centralities, 'Out Degree Centrality')
PlotCentrality(5, centralities, student_centralities, 'Avr. Weighted Degree')
