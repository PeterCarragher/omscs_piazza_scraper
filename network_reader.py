from os import listdir
from os.path import isfile, join
from functools import reduce
from operator import add

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import os

plt.style.use('ggplot')

mypath = 'spring/'
onlyfiles = [os.path.splitext(f)[0] for f in listdir(mypath) if isfile(join(mypath, f))]

centralities = {}
student_centralities = {}
student_centralities_normalised = {}

# # manually scraped from OSCAR
# class_sizes = {'CS6460-SP': 212,
#                'CS6460-SU': 171,
#                'CS6750-SP': 437,
#                'CS6750-SU': 504,
#                'CS7637-SP': 557,
#                'CS7637-SU': 376,
#                'CS7646-SP': 691,
#                'CS7646-SU': 841,
#                }

def stat(arr, num_nodes):
    return reduce(add, arr.values()) / num_nodes
    # for median: np.percentile(list(arr.values()), 50)

def Centralities(G):#, normalise_file=None):
    num_nodes = G.number_of_nodes()
    # if (normalise_file is not None):
    #     num_nodes = class_sizes[normalise_file]

    # betweenness (how often they appear on route between other students)
    # Betweenness centrality of a node v is the sum of the fraction of all-pairs shortest paths that pass through v
    b = nx.centrality.betweenness_centrality(G)
    bm = stat(b, num_nodes)

    # closeness (how many other students have a short path to that node)
    # Closeness centrality of a node u is the reciprocal of the average shortest path distance to u over all n-1 reachable nodes.
    c = nx.centrality.closeness_centrality(G)
    cm = stat(c, num_nodes)

    # degree (number of connections they have)
    # The degree centrality for a node v is the fraction of nodes it is connected to.
    d = nx.centrality.degree_centrality(G)
    dm = stat(d, num_nodes)

    # in degree (number of incoming connections they have)
    i = nx.centrality.in_degree_centrality(G)
    im = stat(i, num_nodes)

    # out degree (number of outoing connections they have)
    o = nx.centrality.out_degree_centrality(G)
    om = stat(o, num_nodes)

    # avr. weighted degree
    w = dict(nx.degree(G, weight='weight'))
    wm = stat(w, num_nodes)

    return ((bm, cm, dm, im, om, wm), (b, c, d, i, o, w))


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

print(centralities.keys())
    # get normalised scores
    # student_centralities_normalised[file] = Centralities(students, file)

def PlotCentrality(idx, centralities, student_centralities, name):
    ind = np.arange(len(centralities.keys()))
    width = 0.35
    plt.bar(ind, [c[0][idx] for (_, c)
                  in centralities.items()], width, label='All users')
    # plt.bar(ind + width, [c[0][idx] for (_, c) in student_centralities.items()], width,
    #         label='Students only')
    # comment this for median
    # plt.bar(ind + width*2.0, [centralities[idx] for (_, centralities) in student_centralities_normalised[0].items()], width,
    #         label='Students only (norm)')

    plt.ylabel(name)
    plt.title(name + ' by class and role')

    plt.xticks(ind + width / 2, onlyfiles, rotation=45)
    plt.tight_layout()
    plt.legend(loc='best')
    plt.savefig('imgs/' + name + '.png')
    plt.show()
    plt.close()

    plt.figure(figsize=(8,6))
    # for class in 
    for (file_name, value_dict) in centralities.items():
        # print(value_dict)
        plt.hist([x for x in value_dict[1][idx].values() if x > 0.05 and x < 0.55], bins=10, alpha=0.5, label=file_name)
    plt.xlabel(name, size=14)
    plt.ylabel("# of students", size=14)
    plt.title("Distribution of " + name)
    plt.legend(loc='upper right')
    plt.savefig('imgs/' + name+" distribution_filter.png")
    plt.show()
    plt.close()
    

print(len(centralities))
PlotCentrality(0, centralities, student_centralities, 'Betweenness Centrality')
PlotCentrality(1, centralities, student_centralities, 'Closeness Centrality')
PlotCentrality(2, centralities, student_centralities, 'Degree Centrality')
PlotCentrality(3, centralities, student_centralities, 'In Degree Centrality')
PlotCentrality(4, centralities, student_centralities, 'Out Degree Centrality')
PlotCentrality(5, centralities, student_centralities, 'Avr. Weighted Degree')
