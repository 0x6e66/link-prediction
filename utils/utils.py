import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import random

# Calculates the scores for every edge in 'removed_edges' for every algorithm in 'algos'
def compare_normal_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges):
    # Build dataframe by columns
    df_n = pd.DataFrame(
        columns=["edge", "is_removed_edge"] + list(algos.keys()))

    # Calculate the scores of every non-existent edge in the reduced_graph for the first algorithm 
    sources, targets, first_scores = list(zip(*algos[list(algos.keys())[0]](reduced_graph)))
    edges = list(zip(sources, targets))
    removed = []
    scores = {list(algos.keys())[0]: first_scores}

    for edge in edges:
        # Check if edge is in removed_edges => relevant for comparing the algorithms
        if edge in removed_edges or edge[::-1] in removed_edges:
            removed.append(True)
        else:
            removed.append(False)

    # Calculate the scores of every non-existent edge in the reduced_graph for the other algorithms
    for key in list(algos.keys())[1:]:
        _, _, tmp_scores = list(zip(*algos[key](reduced_graph)))
        scores[key] = tmp_scores

    # Fill dataframe with data
    df_n["edge"] = edges
    df_n["is_removed_edge"] = removed
    for key in algos.keys():
        df_n[key] = scores[key]

    return df_n



# Calculates the scores for every edge in 'removed_edges' for every algorithm in 'algos'
def compare_community_algorithms_for_reduced_graph(algos, reduced_graph, removed_edges, communities):
    for i, community in enumerate(communities):
        for v in community:
            reduced_graph.nodes[v]['community'] = i + 1

    # Build dataframe by columns
    df_n = pd.DataFrame(
        columns=["edge", "is_removed_edge"] + list(algos.keys()))

    # Calculate the scores of every non-existent edge in the reduced_graph for the first algorithm 
    sources, targets, first_scores = list(
        zip(*algos[list(algos.keys())[0]](reduced_graph)))
    edges = list(zip(sources, targets))
    removed = []
    scores = {list(algos.keys())[0]: first_scores}

    for edge in edges:
        # Check if edge is in removed_edges => relevant for comparing the algorithms
        if edge in removed_edges or edge[::-1] in removed_edges:
            removed.append(True)
        else:
            removed.append(False)

    # Calculate the scores of every non-existent edge in the reduced_graph for the other algorithms
    for key in list(algos.keys())[1:]:
        _, _, tmp_scores = list(zip(*algos[key](reduced_graph)))
        scores[key] = tmp_scores

    # Fill dataframe with data
    df_n["edge"] = edges
    df_n["is_removed_edge"] = removed
    for key in algos.keys():
        df_n[key] = scores[key]

    return df_n


def compare_combined(algos, reduced_graph, removed_edges, communities):
    # Calculate data for all "normal" algorithms (algorithms that are not based on communities)
    df1 = compare_normal_algorithms_for_reduced_graph(
        algos["normal_algos"], reduced_graph, removed_edges)
    # Calculate data for all "community" algorithms (algorithms that are based on communities)
    df2 = compare_community_algorithms_for_reduced_graph(
        algos["community_algos"], reduced_graph, removed_edges, communities)

    # concat the two dataframes
    return pd.concat([df1, df2.loc[:, list(algos["community_algos"].keys())]], axis=1)

# Randomly removes edges from the graph and returns ("graph" is left untouched)
def remove_edges(graph, percentages):
    res = []

    for p in percentages:
        # Calculate number of edges to remove based on the current percentage
        num_of_edges_to_remove = int(graph.number_of_edges() * p)

        # Randomly select edges to remove
        edges_to_remove = random.sample(list(graph.edges()), k=num_of_edges_to_remove)
        
        tmp_graph = graph.copy()

        # Remove edges from temporary graph
        tmp_graph.remove_edges_from(edges_to_remove)
        
        res.append((tmp_graph, edges_to_remove))

    return res


def plot_results(graph_num, data, scope=None, num_of_intervals=10):
    if scope:
        # If scope is set, check if scope is set right
        assert (scope[0] < scope[1]+num_of_intervals)

    # Dictionary for full names of algorithms in resulting image
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
    
    # Sort for every algorithm and calculate the indexes of the previously removed edges
    for algo in data.columns[2:]:
        # Sort by current algorithm
        data = data.sort_values(by=algo, ascending=False)
        # Reset indexes
        data = data.reset_index(drop=True)

        # Append a list of indexes of previously removed edges to list_of_indexlists
        list_of_indexlists.append(
            list(data[data['is_removed_edge'] == True].index))

    # Calculate highest index in list_of_indexlists
    max_val = max(list(zip(*list_of_indexlists))[-1])

    # Set width of interval (and scope if not set)
    if scope:
        width_of_interval = int((scope[1] - scope[0]) / num_of_intervals)
    else:
        width_of_interval = int(max_val / num_of_intervals)
        scope = (0, max_val)

    # Calculate actual intervals
    for j in range(num_of_intervals):
        left, right = j*width_of_interval+1, (j+1)*width_of_interval

        # For display purposes
        disp_ranges.append(f"{left}-{right}")

        # Actual intervals
        ranges.append((left, right))

    # Set last interval correctly, so that the last interval shows correct ending
    if scope[1] < max_val:
        disp_ranges[-1] = (f"{ranges[-1][1]}-{max_val}")
        ranges[-1] = (ranges[-1][1], max_val)
    elif scope[1] > max_val:
        disp_ranges[-1] = (f"{ranges[-1][0]}-{max_val}")
        ranges[-1] = (ranges[-1][0], max_val)

    # Calculate number of indexes in each interval for every algorithm
    for j, algo in enumerate(data.columns[2:]):
        y = []
        for left, right in ranges:
            # Filter for every index that falls in the range(left, right)
            number_of_indexes_in_interval = len(
                list(filter(lambda x: left <= x < right, list_of_indexlists[j])))
            y.append(number_of_indexes_in_interval)

        x = [x + bar_width*j for x in range(len(y))]
        plt.bar(x, y, width=bar_width, edgecolor='grey', label=algo_dict[algo])

    plt.title(f"Graph n{graph_num}")
    plt.xlabel(xlabel=f"Rank calculated by algorithm",
               fontweight='bold',
               fontsize=15)
    plt.ylabel(ylabel="Number of previously removed edges",
               fontweight='bold',
               fontsize=15)
    
    # Set placing of the display range to be in the middle of the bars
    num_of_algos = len(data.columns[2:])
    if num_of_algos % 2 == 0:
        plt.xticks([r + bar_width*(num_of_algos/2-0.5) for r in range(num_of_intervals)], disp_ranges)
    elif num_of_algos % 2 != 0:
        plt.xticks([r + bar_width*(num_of_algos/2-1) for r in range(num_of_intervals)], disp_ranges)

    plt.legend()
    plt.show()
