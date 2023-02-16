import pandas as pd
import networkx as nx


def compare_normal_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges, original_graph):
    df_n = pd.DataFrame(columns=["source", "target"] + list(algos.keys()))
    df_n["source"], df_n["target"] = list(zip(*removed_edges))
    for key in algos:
        df_n[key] = list(algos[key](reduced_graph, removed_edges))[0][2]

    df_g = pd.DataFrame(columns=["source", "target"] + list(algos.keys()))
    df_g["source"], df_g["target"] = list(zip(*removed_edges))
    for key in algos:
        df_g[key] = list(algos[key](original_graph, removed_edges))[0][2]

    delta = df_g.loc[:, algos.keys()].divide(df_n.loc[:, algos.keys()])
    res = pd.concat([df_n.loc[:, ["source", "target"]], delta], axis=1)
    return res


def compare_community_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges, original_graph, communities):
    for i, community in enumerate(communities):
        for v in community:
            reduced_graph.nodes[v]['community'] = i + 1
            original_graph.nodes[v]['community'] = i + 1

    df_n = pd.DataFrame(columns=["source", "target"] + list(algos.keys()))
    df_n["source"], df_n["target"] = list(zip(*removed_edges))
    for key in algos:
        df_n[key] = list(algos[key](reduced_graph, removed_edges))[0][2]

    df_g = pd.DataFrame(columns=["source", "target"] + list(algos.keys()))
    df_g["source"], df_g["target"] = list(zip(*removed_edges))
    for key in algos:
        df_g[key] = list(algos[key](original_graph, removed_edges))[0][2]

    delta = df_g.loc[:, algos.keys()].divide(df_n.loc[:, algos.keys()])
    res = pd.concat([df_n.loc[:, ["source", "target"]], delta], axis=1)
    return res


def compare_combined(n_algos, c_algos, reduced_graph, removed_edges, original_graph, communities):
    df1 = compare_normal_algorithms_for_reduced_graph(n_algos, reduced_graph, removed_edges, original_graph)
    df2 = compare_community_algorithms_for_reduced_graph(c_algos, reduced_graph, removed_edges, original_graph, communities)

    return pd.concat([df1, df2.loc[:, list(c_algos.keys())]], axis=1)

