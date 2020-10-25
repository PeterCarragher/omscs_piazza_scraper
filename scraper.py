from piazza_api import Piazza
import networkx as nx
import pprint
from functools import reduce
from operator import add
import time
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

p = Piazza()
p.user_login()
# if students did have capability to create secret student to student groups, I wouldnt see it. 
# However piazza doesnt have that capability: you can only create posts for all students or just for the instructors eyes
# This means it is unlikely that we would ever be able to manipulate the Piazza community into a student led one
# Time to look into the slack API

# cs6460 = p.network("kd0xb0u5r4amc")
# output_file = 'cs4641_test.gexf'
cs6460 = p.network("kdthrjcjhp660s")
output_file = 'cs6460_test.gexf'

posts = cs6460.iter_all_posts(limit=10000)
edges = dict()
nodes = set()
node_sizes = dict()

i = 0
# only getting i = 60 when I should get 180 posts
# this is why Ken Brooks does not appear in list of names - or most of the other instructors for that matter

post = next(posts, None)
while (post is not None):
    i += 1
    logging.debug('begin: ' + str(i))

    assert(post['change_log'][0]['type'] == 'create')
    if 'uid' not in post['change_log'][0]:
        # anonymous
        try:    
            post = next(posts, None)
        except:
            time.sleep(1)
            post = next(posts, None)
        continue
    author = post['change_log'][0]['uid']
    nodes.add(author)
    node_sizes[author] = node_sizes.get(author, 1) + 10

    followups = post['children']

    logging.debug('Num followups: ' + str(len(followups)))


    for followup in followups:
        if 'uid' not in followup:
            # anonymous
            continue
        follower = followup['uid']
        nodes.add(follower)
        node_sizes[follower] = node_sizes.get(follower, 1) + 1
        
        if not follower in edges:
            edges[follower] = dict()
        edges[follower][author] = edges[follower].get(author, 0) + 1

        comments = followup['children']

        logging.debug('Num comments: ' + str(len(comments)))
        for comment in comments:
            if 'uid' not in comment:
                # anonymous
                continue
            commentor = comment['uid']

            nodes.add(commentor)
            node_sizes[commentor] = node_sizes.get(commentor, 1) + 1

            if not commentor in edges:
                edges[commentor] = dict()
            edges[commentor][follower] = edges[commentor].get(follower, 0) + 1

    logging.debug(i)
    try:    
        post = next(posts, None)
    except:
        time.sleep(1)
        post = next(posts, None)

logging.debug(i)
node_data = cs6460.get_users(list(nodes))
node_roles = {node['id']: node['role'] for node in node_data}
node_names = {node['id']: node['name'] for node in node_data}

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(edges)
pp.pprint(len(nodes))
# pp.pprint(node_roles)

G = nx.Graph() # Initialize a Graph object
G.add_nodes_from([(node, {'color':node_roles[node], 'size':node_sizes[node], 'name':node_names[node]}) for node in nodes]) # Add nodes to the Graph
G.add_weighted_edges_from(reduce(add, [[(a,b,edges[a][b]) for b in edges[a]] for a in edges])) # Add edges to the Graph
logging.debug(nx.info(G)) # Print information about the Graph
nx.write_gexf(G, output_file)

# plot centralities on another graph where colour is still role, but size is sum of these 3 centralities. Assumption is that 'leaders' are the TAs / instructors
# betweenness (how often they appear on route between other students) 
# logging.debug('Betweenness centrality: ' + str(nx.centrality.betweenness_centrality(G)))
# closeness (how many other students have a short path to that node)
# logging.debug('Closeness centrality: ' + str(nx.centrality.closeness_centrality(G))) 
#  degree (number of connections they have)
# logging.debug('Degree centrality: ' + str(nx.centrality.degree_centrality(G))) 
