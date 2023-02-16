import pandas as pd

def compare_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges, original_graph):
    df_n1 = pd.DataFrame(columns=["source", "target", "rai", "jc", "aai", "pa",  "cnc"]) # "cnsh", "raish", "wiccn",
    df_n1["source"], df_n1["target"] = list(zip(*removed_edges))
    for key in algos:
        df_n1[key] = list(algos[key](reduced_graph, removed_edges))[0][2]


    df_g = pd.DataFrame(columns=["source", "target", "rai", "jc", "aai", "pa",  "cnc"]) # "cnsh", "raish", "wiccn",
    df_g["source"], df_g["target"] = list(zip(*removed_edges))
    for key in algos:
        df_g[key] = list(algos[key](original_graph, removed_edges))[0][2]

    delta = df_g.loc[:, ["rai", "jc", "aai", "pa",  "cnc"]].subtract(df_n1.loc[:, ["rai", "jc", "aai", "pa",  "cnc"]])
    res = pd.concat([df_n1.loc[:, ["source", "target"]], delta], axis=1)
    return res
