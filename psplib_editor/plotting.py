import matplotlib.pyplot as plt
import networkx as nx

from .instances import ProblemInstance
from .graphs import build_instance_graph


def plot_instance_graph(
    instance: ProblemInstance,
    latest_layer: bool = True,
    ) -> None:
    """
    Plots the instance graph for a given problem instance.

    Args:
        instance: The problem instance to plot the graph for.
        latest_layer: Determines whether to draw jobs in the latest layer (True, default),
            or in the earliest layer (False).
    """
    graph = build_instance_graph(instance)

    # Build topological layers for the reverse graph
    generations_graph = (graph.reverse(copy=False) if latest_layer else graph)
    layers = {}
    for i_layer, generation in enumerate(nx.topological_generations(generations_graph)):
        layers[i_layer] = sorted(generation)

    if latest_layer:
        # Reverse the layers for the original graph
        n_layers = max(layers.keys())
        layers_ = {}
        for i_layer in layers.keys():
            layers_[n_layers - i_layer] = layers[i_layer]
        layers = layers_

    # Plot the graph
    plt.figure()
    pos = nx.multipartite_layout(graph, subset_key=layers)
    nx.draw(graph, pos)
