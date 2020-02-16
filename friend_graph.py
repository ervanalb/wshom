import networkx as nx
import logging

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

def get_isolated(g, size=4, max_depth=2):
    g = g.copy()
    isolated = []
    while True:
        newly_isolated = [n for n in g.nodes if len(nx.bfs_tree(g, n, depth_limit=max_depth).nodes) < size]
        if not newly_isolated:
            break
        g.remove_nodes_from(newly_isolated)
        isolated.extend(newly_isolated)
    return isolated

def get_groupings(g, size=4, max_depth=2):
    orig_size = len(g.nodes)
    g = g.copy()
    groupings = []
    while True:
        if not g.edges:
            break
        # Find edge with highest points
        starting_edge, starting_points = max(nx.get_edge_attributes(g, "points").items(), key=lambda x: x[1])
        logger.debug("Starting edge is {} with {} points".format(starting_edge, starting_points))
        group = set(starting_edge)
        (n1, n2) = [nx.bfs_tree(g, n, depth_limit=max_depth - 1).nodes for n in starting_edge]
        nodes = set(n1).union(n2)
        subgraph = g.subgraph(nodes).copy()
        subgraph.remove_edge(*starting_edge)
        current_nodes = set(starting_edge)
        while True:
            if not subgraph.edges(current_nodes):
                group = set()
                break
            logger.debug("Current nodes are {}".format(current_nodes))
            best_edge, best_points = max([(edge, subgraph.edges[edge]["points"]) for edge in subgraph.edges(current_nodes)], key=lambda x: x[1])
            logger.debug("Best next edge is {} with {} points".format(best_edge, best_points))
            if set(best_edge).issubset(group):
                logger.debug("{} are already in group".format(best_edge))
            else:
                new_node = (set(best_edge) - current_nodes).pop()
                logger.debug("Adding {} to group".format(new_node))
                group.add(new_node)
                if len(group) == size:
                    break
                current_nodes -= set(best_edge)
                current_nodes.add(new_node)
            subgraph.remove_edge(*best_edge)
            if subgraph.has_edge(*current_nodes):
                subgraph.remove_edge(*current_nodes)
        if group:
            logger.debug("Formed a group: {}".format(group))
            groupings.append(group)
            g.remove_nodes_from(group)
        else:
            logger.debug("Failed to make a group")
            g.remove_edge(*starting_edge)
    logger.debug("Was able to put {} / {} eligible people into groups".format(orig_size - len(g.nodes), orig_size))
    return groupings

def main():
    import matplotlib.pyplot as plt
    import time
    import random

    nodes = {
        "A": {"min_interval": 5},
        "B": {"min_interval": 6},
        "C": {"min_interval": 7},
        "D": {"min_interval": 3},
        "E": {"min_interval": 3},
        "F": {"min_interval": 3},
    }

    edges = [
        ("A", "B"),
        ("B", "A"),
        ("C", "B"),
        ("B", "C"),
        ("D", "E"),
        ("E", "D"),
        ("D", "A"),
        ("A", "D"),
        ("E", "C"),
        ("C", "E"),
        ("E", "F"),
        ("E", "A"),
        ("A", "E"),
    ]

    logging.basicConfig(level=logging.DEBUG)

    #g = nx.DiGraph()
    #g.add_nodes_from(nodes.items())
    #g.add_edges_from(edges)

    random.seed(2)

    g = nx.fast_gnp_random_graph(10, 0.5, directed=True)
    nx.set_node_attributes(g, {n: {"min_interval": random.randint(5, 10)} for n in g.nodes})

    ug = to_undirected(g)
    isolates = get_isolated(ug)
    print("{} / {} nodes are isolated".format(len(isolates), len(ug.nodes)))
    ug.remove_nodes_from(isolates)

    zero_points(ug)

    nx.draw(ug, with_labels=True)
    plt.show()

    i = 0
    for i in range(100):
        print(i)
        increment_points(ug)
        eg = without_ineligible(ug)
        if eg.nodes:
            groupings = get_groupings(eg)
            for group in groupings:
                print(",".join([str(n) for n in group]), "should hang out")
                zero_points(ug, group)

        print(nx.get_node_attributes(eg, "points"))
        print(nx.get_edge_attributes(eg, "points"))

if __name__ == "__main__":
    main()
