import networkx as nx

from .instances import ProblemInstance


def build_instance_graph(instance: ProblemInstance) -> nx.DiGraph:
    """
    Build a directed graph representation of a problem instance.
    Constructs a NetworkX directed graph where nodes represent jobs and edges
    represent precedence relationships between jobs.

    Args:
        instance: A problem instance containing precedence constraints.

    Returns:
        nx.DiGraph: A directed graph where edges represent job precedence relationships,
            with an edge from predecessor to successor for each precedence constraint.
    """
    edges = [(p.predecessor, p.successor) for p in instance.precedences]
    graph = nx.DiGraph(edges)
    return graph
