import EdAPI 
import networkx as nx
import pprint
from functools import reduce
from operator import add
import time
import logging
import sys
import queue


logging.basicConfig(filename='session_log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(level=logging.INFO)
rootLogger.addHandler(consoleHandler)
ed = EdAPI.EdAPI()

add_another_class = True
classes = dict()
pp = pprint.PrettyPrinter(indent=4)

while add_another_class:
    print('Classes added so far:')
    pp.pprint(classes)
    class_code = input('Please enter the course code or enter to start parsing. To find the course code, visit the Piazza class and copy the last part of the URL (i.e for https://piazza.com/class/asdfghjkl, paste in \'asdfghjkl\'): ')
    if class_code == '':
        add_another_class = False
        continue
    class_name = input('Please enter the class name for this code: ')
    classes[class_code] = class_name
    continue_input = input(
        'Enter "begin" to start parsing the Piazza networks OR press enter to add another class: ')
    if continue_input == 'begin':
        add_another_class = False

total_posts = 0

# TODO refactor this procedural logic into a more readable class
for class_code, class_name in classes.items():
    output_file = class_name + '_network.gexf'

    threads = ed.readThreadsFromClass(class_code)
    
    edges = dict()
    nodes = set()
    node_sizes = dict()
    node_interactions = dict()

    comments = None

    rootLogger.info('Parsing class %s with code %s', class_name, class_code)
    i = 0

    for (post_id, author) in threads.items():
        try_fetch = True
        attempt = 0
        max_attempts = 20
        while try_fetch and attempt < max_attempts:
            try:
                time.sleep(attempt)
                comments = ed.readCommentsFromThread(post_id)
                try_fetch = False
            except:
                attempt += 1
                rootLogger.info('sleep for %d and retry %s', attempt, post_id)
                continue

        if attempt >= max_attempts:
            rootLogger.info('skip %s', post_id)
            continue

        i += 1
        total_posts += 1
        rootLogger.info('Processing post %s, num %d: ', post_id, i)

        nodes.add(author)
        node_sizes[author] = node_sizes.get(author, 1) + 10
        node_interactions[author] = node_interactions.get(author, 1) + 1

        rootLogger.debug('Num top level comments: ' + str(len(comments)))

        unseen = queue.Queue()   

        for comment in comments:
            unseen.put((author, comment))
        
        while unseen.qsize() > 0:
            recipient, comment = unseen.get()
            if 'user_id' not in comment:
                continue
            sender = comment['user_id']
            children = comment['comments']
            rootLogger.debug('Num child comments: ' + str(len(children)))

            for child in children:
                if 'user_id' not in child:
                    continue
                unseen.put((sender, child))
            
            
            follower = hash(sender)
            nodes.add(sender)
            interaction_weight = 2 if recipient == author else 1
            node_sizes[follower] = node_sizes.get(follower, 1) + interaction_weight
            node_interactions[follower] = node_interactions.get(
                follower, 1) + 1

            if not follower in edges:
                edges[follower] = dict()
            edges[follower][recipient] = edges[follower].get(recipient, 0) + 1



    # node_data = piazza_class.get_users(list(nodes))
    # node_roles = {hash(node['id']): node['role'] for node in node_data}

    G = nx.DiGraph()  # Initialize a directed graph object
    # G.add_nodes_from([(hash(node), {'color': node_roles[hash(node)], 'size':node_sizes[hash(node)],
    #                           'interactions':node_interactions[hash(node)]}) for node in nodes])  # Add nodes to the Graph
    G.add_nodes_from([(hash(node), {'size':node_sizes[hash(node)],
                            'interactions':node_interactions[hash(node)]}) for node in nodes]) 
    G.add_weighted_edges_from(reduce(
        add, [[(a, b, edges[a][b]) for b in edges[a]] for a in edges]))  # Add edges to the Graph
    rootLogger.info(nx.info(G))  # Print information about the Graph
    nx.write_gexf(G, output_file)

    # plot centralities on another graph where colour is still role, but size is sum of these 3 centralities. Assumption is that 'leaders' are the TAs / instructors
    # betweenness (how often they appear on route between other students)
    rootLogger.info('Betweenness centrality: ' +
                    str(nx.centrality.betweenness_centrality(G)))
    # closeness (how many other students have a short path to that node)
    rootLogger.info('Closeness centrality: ' +
                    str(nx.centrality.closeness_centrality(G)))
    #  degree (number of connections they have)
    rootLogger.info('Degree centrality: ' +
                    str(nx.centrality.degree_centrality(G)))
