from piazza_api import Piazza
import networkx as nx
import pprint
from functools import reduce
from operator import add
import time
import logging
import sys

logging.basicConfig(filename='session_log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setLevel(level=logging.INFO)
rootLogger.addHandler(consoleHandler)
p = Piazza()
print('Please enter your Piazza login credentials.')
p.user_login()

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
    piazza_class = p.network(class_code)
    output_file = class_name + '_network.gexf'

    feed = piazza_class.get_feed(limit=10000)
    cids = [post['id'] for post in feed["feed"]]
    edges = dict()
    nodes = set()
    node_sizes = dict()
    node_interactions = dict()

    post = None

    rootLogger.info('Parsing class %s with code %s', class_name, class_code)
    i = 0

    for post_id in cids:
        if total_posts > 0 and total_posts % 60 == 0:
            rootLogger.info('Waiting for Piazza response...')
            time.sleep(15)
        try_fetch = True
        attempt = 0
        max_attempts = 20
        while try_fetch and attempt < max_attempts:
            try:
                time.sleep(attempt)
                post = piazza_class.get_post(post_id)
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

        assert(post['change_log'][0]['type'] == 'create')
        if 'uid' not in post['change_log'][0]:
            rootLogger.debug('missing uid for %s', post_id)
            continue

        author = hash(post['change_log'][0]['uid'])
        nodes.add(author)
        node_sizes[author] = node_sizes.get(author, 1) + 10
        node_interactions[author] = node_interactions.get(author, 1) + 1

        followups = post['children']

        rootLogger.debug('Num followups: ' + str(len(followups)))

        for followup in followups:
            if 'uid' not in followup:
                # anonymous
                continue
            follower = hash(followup['uid'])
            nodes.add(follower)
            node_sizes[follower] = node_sizes.get(follower, 1) + 1
            node_interactions[follower] = node_interactions.get(
                follower, 1) + 1

            if not follower in edges:
                edges[follower] = dict()
            edges[follower][author] = edges[follower].get(author, 0) + 1
            # TODO add timestamps / dates to edges

            comments = followup['children']

            rootLogger.debug('Num comments: ' + str(len(comments)))
            for comment in comments:
                if 'uid' not in comment:
                    # anonymous
                    continue
                commentor = hash(comment['uid'])

                nodes.add(commentor)
                node_sizes[commentor] = node_sizes.get(commentor, 1) + 2
                node_interactions[commentor] = node_interactions.get(
                    commentor, 1) + 1

                if not commentor in edges:
                    edges[commentor] = dict()
                edges[commentor][follower] = edges[commentor].get(
                    follower, 0) + 1

    node_data = piazza_class.get_users(list(nodes))
    node_roles = {node['id']: node['role'] for node in node_data}

    G = nx.DiGraph()  # Initialize a directed graph object
    G.add_nodes_from([(node, {'color': node_roles[node], 'size':node_sizes[node],
                              'interactions':node_interactions[node]}) for node in nodes])  # Add nodes to the Graph
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
