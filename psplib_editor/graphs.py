import networkx as nx

from .instances import ProblemInstance


def build_instance_graph(instance: ProblemInstance, ignore_dummy_jobs: bool = False) -> nx.DiGraph:
    """
    Build a directed graph representation of a problem instance.
    Constructs a NetworkX directed graph where nodes represent jobs and edges
    represent precedence relationships between jobs.

    Args:
        instance: A problem instance containing precedence constraints.
        ignore_dummy_jobs: If True, dummy jobs will be ignored when building the graph. Default is False.

    Returns:
        nx.DiGraph: A directed graph where edges represent job precedence relationships,
            with an edge from predecessor to successor for each precedence constraint.
    """
    edges = [(p.predecessor, p.successor) for p in instance.precedences]
    graph = nx.DiGraph(edges)

    if ignore_dummy_jobs:
        graph.remove_nodes_from(instance.dummy_job_ids)

    return graph
