import pandas as pd
import networkx as nx

'''
Calculates the scores for every edge in 'removed_edges' for every algorithm in 'algos'
Optional: With the option 'compare_with_original_graph' the scores for the 'reduced_graph' are being compared to the scores in the 'original_graph'
'''


def compare_normal_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges):
    df_n = pd.DataFrame(columns=["edge", "is_removed_edge"] + list(algos.keys()))

    sources, targets, first_scores = list(zip(*algos[list(algos.keys())[0]](reduced_graph)))
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

    df_n = pd.DataFrame(columns=["edge", "is_removed_edge"] + list(algos.keys()))

    sources, targets, first_scores = list(zip(*algos[list(algos.keys())[0]](reduced_graph)))
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
