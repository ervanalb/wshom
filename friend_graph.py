import networkx as nx
import logging
import itertools

logger = logging.getLogger(__name__)

def to_undirected(g):
    g = g.copy()
    single_edges = [(u,v) for (u, v) in g.edges if not g.has_edge(v, u)]
    g.remove_edges_from(single_edges)
    g = g.to_undirected()
    return g

def zero_points(g, nodes=None):
    if nodes is None:
        nodes = g.nodes
    nx.set_node_attributes(g, {n: {"points": 0} for n in nodes})
    nx.set_edge_attributes(g, {(u, v): {"points": 0} for (u, v) in g.edges if u in nodes and v in nodes})

def increment_points(g):
    nx.set_node_attributes(g, {n: {"points": g.nodes[n]["points"] + 1} for n in g.nodes})
    nx.set_edge_attributes(g, {e: {"points": g.edges[e]["points"] + 1} for e in g.edges})

def without_ineligible(g):
    g = g.copy()
    ineligible_nodes = [n for n in g.nodes if g.nodes[n]["points"] < g.nodes[n]["min_interval"]]
    g.remove_nodes_from(ineligible_nodes)
    return g

def get_isolated(g, size=4):
    g = g.copy()
    removed_edges = set()
    while True:
        newly_isolated = [e for e in g.edges if not get_best_group(g, e, size, return_exists=True)]
        if not newly_isolated:
            break
        logger.debug("These edges will never be used: {}".format(repr(newly_isolated)))
        g.remove_edges_from(newly_isolated)
        removed_edges = removed_edges.union(newly_isolated)
    return list(nx.isolates(g)), removed_edges

def get_best_group(g, edge, size, return_exists=False):
    logger.debug("Get best group for {}".format(repr(edge)))
    max_depth = size - 1
    (n1, n2) = [nx.bfs_tree(g, n, depth_limit=max_depth - 1).nodes for n in edge]
    nodes = set(n1).union(n2)
    nodes -= set(edge)
    combos = (set(edge) | set(c) for c in itertools.combinations(nodes, size - 2))
    combo_graphs = (g.subgraph(c) for c in combos)

    def score(gg):
        if not nx.is_k_edge_connected(gg, 2):
            return None
        #return sum(sorted(nx.get_edge_attributes(g, "points").values())[-4:])
        return sum(nx.get_edge_attributes(g, "points").values())

    scores = ((c, score(c)) for c in combo_graphs)
    scores = ((c, s) for (c, s) in scores if s is not None)

    if return_exists:
        return any(True for _ in scores)

    scores = list(scores)
    logger.debug("Found {} valid groups of {}".format(len(scores), size))
    best_group, best_score = max(scores, key=lambda x: x[1], default=(None, None))

    if best_group is not None:
        logger.debug("Chosen group has score {}".format(best_score))
        return set(best_group.nodes)
    else:
        return None

def get_groupings(g, size=4):
    orig_size = len(g.nodes)
    g = g.copy()
    groupings = []
    while True:
        if not g.edges:
            break
        # Find edge with highest points
        starting_edge, starting_points = max(nx.get_edge_attributes(g, "points").items(), key=lambda x: x[1])
        logger.debug("Starting edge is {} with {} points".format(starting_edge, starting_points))
        group = get_best_group(g, starting_edge, size)
        if group:
            logger.debug("Formed a group: {}".format(group))
            groupings.append(group)
            g.remove_nodes_from(group)
        else:
            logger.debug("Failed to make a group")
            g.remove_edge(*starting_edge)
    logger.debug("Was able to put {} / {} eligible people into groups".format(orig_size - len(g.nodes), orig_size))
    return groupings

def simulate(g, steps=100):
    ug = to_undirected(g)
    isolates, isolated_edges = get_isolated(ug)
    logger.debug("{} / {} nodes are isolated: {}".format(len(isolates), len(ug.nodes), ", ".join([repr(n) for n in isolates])))
    ug.remove_nodes_from(isolates)
    remaining_edges = isolated_edges.intersection(ug.edges)
    logger.debug("{} edges are isolated: {}".format(len(remaining_edges), ", ".join([repr(n) for n in remaining_edges])))
    ug.remove_edges_from(isolated_edges)

    zero_points(ug)

    import matplotlib.pyplot as plt
    nx.draw(ug, with_labels=True)
    plt.show()

    results = []

    i = 0
    for i in range(steps):
        logger.debug("Step {}".format(i))
        increment_points(ug)
        eg = without_ineligible(ug)
        if eg.nodes:
            groupings = get_groupings(eg)
            for group in groupings:
                logger.debug(", ".join([repr(n) for n in group]) + " should hang out")
                zero_points(ug, group)
        else:
            groupings = []
        results.append(groupings)

        #print(nx.get_node_attributes(eg, "points"))
        #print(nx.get_edge_attributes(eg, "points"))

    return ug, results

def main():
    import time
    import random

    #nodes = {
    #    "A": {"min_interval": 5},
    #    "B": {"min_interval": 6},
    #    "C": {"min_interval": 7},
    #    "D": {"min_interval": 3},
    #    "E": {"min_interval": 3},
    #    "F": {"min_interval": 3},
    #}

    #edges = [
    #    ("A", "B"),
    #    ("B", "A"),
    #    ("C", "B"),
    #    ("B", "C"),
    #    ("D", "E"),
    #    ("E", "D"),
    #    ("D", "A"),
    #    ("A", "D"),
    #    ("E", "C"),
    #    ("C", "E"),
    #    ("E", "F"),
    #    ("E", "A"),
    #    ("A", "E"),
    #]

    logging.basicConfig(level=logging.DEBUG)

    #g = nx.DiGraph()
    #g.add_nodes_from(nodes.items())
    #g.add_edges_from(edges)

    g = nx.Graph()
    with open("hub-spoke.txt") as f:
        for l in f:
            group = [n.strip() for n in l.split(",") if n.strip()]
            for n in group[1:]:
                g.add_edge(group[0], n)

    with open("complete.txt") as f:
        for l in f:
            group = [n.strip() for n in l.split(" ") if n.strip()]
            for n1 in group:
                for n2 in group:
                    if n1 != n2:
                        g.add_edge(n1, n2)

    for i in range(1):
        random.seed(i)
        #g = nx.fast_gnp_random_graph(10, 0.5, directed=True)
        nx.set_node_attributes(g, {n: {"min_interval": random.randint(5, 8)} for n in g.nodes})
        ug, results = simulate(g)
        hangouts = {n: 0 for n in ug.nodes}
        for groupings in results:
            for group in groupings:
                for n in group:
                    hangouts[n] += 1

        print("Total hangouts: {}".format(hangouts))
        for i, hangouts in enumerate(results):
            print("On day {}, hangouts were".format(i), hangouts)

if __name__ == "__main__":
    main()
