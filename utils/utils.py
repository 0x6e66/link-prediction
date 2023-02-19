import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random

'''
Calculates the scores for every edge in 'removed_edges' for every algorithm in 'algos'
Optional: With the option 'compare_with_original_graph' the scores for the 'reduced_graph' are being compared to the scores in the 'original_graph'
'''
def compare_normal_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges):
    df_n = pd.DataFrame(
        columns=["edge", "is_removed_edge"] + list(algos.keys()))

    sources, targets, first_scores = list(
        zip(*algos[list(algos.keys())[0]](reduced_graph)))
    edges = list(zip(sources, targets))
    removed = []
    scores = {list(algos.keys())[0]: first_scores}

    for edge in edges:
        if edge in removed_edges or edge[::-1] in removed_edges:
            removed.append(True)
        else:
            removed.append(False)

    for key in list(algos.keys())[1:]:
        _, _, tmp_scores = list(zip(*algos[key](reduced_graph)))
        scores[key] = tmp_scores

    df_n["edge"] = edges
    df_n["is_removed_edge"] = removed
    for key in algos.keys():
        df_n[key] = scores[key]

    return df_n


'''
Calculates the scores for every edge in 'removed_edges' for every algorithm in 'algos'
Optional: With the option 'compare_with_original_graph' the scores for the 'reduced_graph' are being compared to the scores in the 'original_graph'
'''
def compare_community_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges, communities):
    for i, community in enumerate(communities):
        for v in community:
            reduced_graph.nodes[v]['community'] = i + 1

    df_n = pd.DataFrame(
        columns=["edge", "is_removed_edge"] + list(algos.keys()))

    sources, targets, first_scores = list(
        zip(*algos[list(algos.keys())[0]](reduced_graph)))
    edges = list(zip(sources, targets))
    removed = []
    scores = {list(algos.keys())[0]: first_scores}

    for edge in edges:
        if edge in removed_edges or edge[::-1] in removed_edges:
            removed.append(True)
        else:
            removed.append(False)

    for key in list(algos.keys())[1:]:
        _, _, tmp_scores = list(zip(*algos[key](reduced_graph)))
        scores[key] = tmp_scores

    df_n["edge"] = edges
    df_n["is_removed_edge"] = removed
    for key in algos.keys():
        df_n[key] = scores[key]

    return df_n


def compare_combined(algos, reduced_graph, removed_edges, communities):
    df1 = compare_normal_algorithms_for_reduced_graph(
        algos["normal_algos"], reduced_graph, removed_edges)
    df2 = compare_community_algorithms_for_reduced_graph(
        algos["community_algos"], reduced_graph, removed_edges, communities)

    return pd.concat([df1, df2.loc[:, list(algos["community_algos"].keys())]], axis=1)


def remove_edges(graph, percentages):
    reduced_graphs = []
    removed_edges = []

    for p in percentages:
        num_of_edges_to_remove = int(graph.number_of_edges() * p)
        edges_to_remove = random.sample(list(graph.edges()), k=num_of_edges_to_remove)
        
        removed_edges.append(edges_to_remove)

        tmp_graph = graph.copy()
        tmp_graph.remove_edges_from(edges_to_remove)
        reduced_graphs.append(tmp_graph)

    return reduced_graphs, removed_edges


def plot_results(graph_num, result, scope=None, num_of_intervals=10):
    if scope:
        assert (scope[0] < scope[1]+num_of_intervals)

    algo_dict = {
        "rai": "Resource Allocation Index",
        "jc": "Jaccard Coefficient",
        "aai": "Adamic Adar Index",
        "pa": "Preferential Attachment",
        "cnc": "Common Neighbor Centrality",
        "cnsh": "Commoin Neghbor von Soundarajan und Hopcroft",
        "raish": "Resource Allocation Index von Soundarajan und Hopcroft",
        "wiccn": "Within- and Inter-Cluster Common Neighbors"
    }

    bar_width = 0.1
    fig = plt.subplots(figsize=(20, 5))

    list_of_indexlists = []
    ranges = []
    disp_ranges = []
    y_values_for_algorithms = []

    for algo in result.columns[2:]:
        data = result.sort_values(by=algo, ascending=False)
        data = data.reset_index(drop=True)

        list_of_indexlists.append(
            list(data[data['is_removed_edge'] == True].index))

    max_val = max(list(zip(*list_of_indexlists))[-1])
    if scope:
        width_of_interval = int((scope[1] - scope[0]) / num_of_intervals)
    else:
        width_of_interval = int(max_val / num_of_intervals)
        scope = (0, max_val)

    for j in range(num_of_intervals):
        left, right = j*width_of_interval+1, (j+1)*width_of_interval
        disp_ranges.append(f"{left}-{right}")
        ranges.append((left, right))

    if scope[1] < max_val:
        disp_ranges[-1] = (f"{ranges[-1][1]}-{max_val}")
        ranges[-1] = (ranges[-1][1], max_val)
    elif scope[1] > max_val:
        disp_ranges[-1] = (f"{ranges[-1][0]}-{max_val}")
        ranges[-1] = (ranges[-1][0], max_val)

    for j, algo in enumerate(result.columns[2:]):
        tmp_list = []
        for left, right in ranges:
            val_of_interval = len(
                list(filter(lambda x: left <= x < right, list_of_indexlists[j])))
            tmp_list.append(val_of_interval)
        y_values_for_algorithms.append(tmp_list)

    for j, algo in enumerate(result.columns[2:]):
        y = y_values_for_algorithms[j]
        x = [x + bar_width*j for x in range(len(y))]
        plt.bar(x, y, width=bar_width, edgecolor='grey', label=algo_dict[algo])

    plt.title(f"Graph n{graph_num}")
    plt.xlabel(xlabel=f"Rang berechnet von der Methode",
               fontweight='bold',
               fontsize=15)
    plt.ylabel(ylabel="Anzahl an zuvor gelöschten Kanten",
               fontweight='bold',
               fontsize=15)
    
    num_of_algos = len(result.columns[2:])
    if num_of_algos % 2 == 0:
        plt.xticks([r + bar_width*(num_of_algos/2-0.5) for r in range(num_of_intervals)], disp_ranges)
    elif num_of_algos % 2 != 0:
        plt.xticks([r + bar_width*(num_of_algos/2-1) for r in range(num_of_intervals)], disp_ranges)

    plt.legend()
    plt.show()
