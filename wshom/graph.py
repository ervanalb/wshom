from wshom.model import User, GraphNode, GraphEdge
from wshom.extensions import db
import networkx as nx

def to_undirected(g):
    g = g.copy()
    single_edges = [(u,v) for (u, v) in g.edges if not g.has_edge(v, u)]
    g.remove_edges_from(single_edges)
    g = g.to_undirected()
    return g

def graph_from_database(app):
    g = nx.DiGraph()
    for user, graph_node in db.session.query(User, GraphNode).outerjoin(GraphNode).filter(User.active == True):
        g.add_node(user.id, min_interval=user.min_interval, points=(graph_node.points if graph_node is not None else 0))

        for friend in user.friends:
            g.add_edge(user.id, friend.id, points=0)

    g = to_undirected(g)

    for graph_edge in GraphEdge.query:
        edge_pair = (graph_edge.user_a_id, graph_edge.user_b_id)
        if edge_pair in g.edges:
            g.add_edge(*edge_pair, points=graph_edge.points)

    return g

def save_graph_to_database(app, g):
    g = g.copy()

    for graph_edge in GraphEdge.query.with_for_update():
        uv = graph_edge.user_a_id, graph_edge.user_b_id
        if g.has_edge(*uv):
            graph_edge.points = g.edge[uv]["points"]
            g.remove_edge(*uv)

    for u, v in g.edges:
        points = g.edges[u, v]["points"]
        db.session.add(GraphEdge(user_a_id=u, user_b_id=v, points=points))

    for graph_node in GraphNode.query.with_for_update():
        node_id = graph_edge.user_id
        if g.has_node(node_id):
            graph_node.points = g.nodes[node_id]["points"]
            g.remove_node(*uv)

    for n in g.nodes:
        points = g.nodes[n]["points"]
        db.session.add(GraphNode(user_id=n, points=points))

    db.session.commit()

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

def arrange_hangouts(app):
    g = graph_from_database(app)
    increment_points(g)
    eg = without_ineligible(g)
    if eg.nodes:
        groupings = get_groupings(eg)
        for group in groupings:
            logger.debug(", ".join([repr(n) for n in group]) + " should hang out")
            zero_points(ug, group)
    else:
        groupings = []

    # TODO Do something with groupings

    save_graph_to_database(app, g)

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
