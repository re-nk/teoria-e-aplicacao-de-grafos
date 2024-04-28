# following https://ona-book.org/community.html
#pip install onadata igraph leidenalg python-louvain
from onadata import wikivote,email_edgelist, email_vertices
import pandas as pd
import networkx as nx
from cdlib import algorithms, evaluation, NodeClustering, viz
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt 
import seaborn as sns
import community as community_louvain
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# https://python-louvain.readthedocs.io/en/latest/api.html
# pip install community python-louvain as networkx.community didnt work

def question1():
    print('Question 1: Determine how many weakly connected components there are in this graph. How large is the largest component?')
    print(str(nx.number_weakly_connected_components(dir_graph_wikivote)) + ' weakly connected components')
    components = nx.weakly_connected_components(dir_graph_wikivote)
    subgraphs = [dir_graph_wikivote.subgraph(component).copy() 
    for component in components]
    # size of subgraphs
    weakly_components_lengths = [len(subgraph.nodes) for subgraph in subgraphs]
    print('Largest weakly component length: ' + str(max(weakly_components_lengths)))
    print()


def question2():
    print('Question 2: Determine how many strongly connected components there are in this graph. How large is the largest component?')
    #todo mb explain this
    print(str(nx.number_strongly_connected_components(dir_graph_wikivote)) + ' strongly connected components')
#todo mb comment more around here, after doing a report
    components = nx.strongly_connected_components(dir_graph_wikivote)
    subgraphs = [dir_graph_wikivote.subgraph(component).copy() 
    for component in components]
    # size of subgraphs
    strongly_components_lengths = [len(subgraph.nodes) for subgraph in subgraphs]
    print('Largest strongly component length: ' + str(max(strongly_components_lengths)))
    print()

def question3(): # todo 
    print('')
    

def question4(und_graph_email): # hmm.... mb all the connected vertexes r in the same component & there are 1004-986 isolated vertexes
    print('Question 4: Determine the connected components of this network and reduce the network to its largest connected component.')
 #und_graph_email_vertices = nx.from_pandas_edgelist(df_email_vertices, source='from', target='to', create_using=nx.Graph)
# todo reduce und_graph_email_vertices as well
    # get all connected components
    components = list(nx.connected_components(und_graph_email))
    subgraphs = [und_graph_email.subgraph(component).copy() 
    for component in components]
    print('Number of connected components: ' + str(len(components)))
    # size of subgraphs
    components_lengths = [len(subgraph.nodes) for subgraph in subgraphs] 
# ref https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.components.connected_components.html
    # reduce network to largest component
    largest_cc = max(nx.connected_components(und_graph_email), key=len)
    largest_cc_graph = und_graph_email.subgraph(largest_cc)
    print("Size of largest connected component: " + str(len(largest_cc_graph.nodes()))) # TODO !FIX should reduce network to largest connected component
    print()
    global und_graph_email_largest_connected
    global df_email_vertices_largest_connected
    und_graph_email_largest_connected = largest_cc_graph
    # todo do same for edges
    df_email_vertices_largest_connected = df_email_vertices[df_email_vertices['id'].isin([und_graph_email_largest_connected.nodes()])]

    return largest_cc_graph

def question5(graph): # todo
    print('Use the Louvain algorithm to determine a vertex partition/community structure with optimal modularity in this network.')    
    # create undirected network
    email = nx.from_pandas_edgelist(df_email_edgelist, source = "from", target = "to")
    # get louvain partition which optimizes modularity
    louvain_comms_email = algorithms.louvain(email)
    print(pd.DataFrame(louvain_comms_email.communities).transpose())
    #print('Modularity ' + str(louvain_comms_email.newman_girvan_modularity().score))
# todo ? arent there many louvains? why isnt a list returned? dont i have to pick ? assuming no for now
    return louvain_comms_email


#for the ground truth department structure
def graph_to_NodeClustering_obj(graph):
    # reference https://cdlib.readthedocs.io/en/latest/reference/classes.html  
    return NodeClustering([list(graph.nodes)], graph=graph)   


def question6(louvain_email): # 
    print('Question 6: Compare the modularity of the Louvain community structure with that of the ground truth department structure.')
    # todo fix should make community from sharing a dept?
    print('Modularity of louvain in emails edgelist' + str(louvain_email.newman_girvan_modularity().score))    
    ground_truth_communities  = graph_to_NodeClustering_obj(und_graph_email_largest_connected)  # df_column_to_NodeClustering_obj(und_graph_email, largest_email_vertices, 'dept')
    # reference https://cdlib.readthedocs.io/en/latest/reference/eval/cdlib.evaluation.newman_girvan_modularity.html
    ground_truth_modularity = evaluation.newman_girvan_modularity(und_graph_email_largest_connected , ground_truth_communities).score
    print('Modularity of ground truth department structure in email vertices:', ground_truth_modularity)
    return ground_truth_communities

def visualize_louvain(graph, louvain_comms):
    # Create dict with labels only for Mr Hi and John A
    node_labels = {node: node if node == "Mr Hi" or node == "John A" else "" for node in graph.nodes}
    # Create and order community mappings
    communities = louvain_comms.to_node_community_map()
  # get wont cause error if communities[node] is none 
    communities = [communities[node].get(node) for node in graph.nodes]
    # Create color map
    pastel2 = cm.get_cmap('Pastel2', max(communities) + 1)
    # Visualize Louvain community structure
    plt.figure(figsize=(10, 6))
    np.random.seed(123)
    nx.draw_spring(graph, labels=node_labels, cmap=pastel2, node_color=communities, edge_color="grey")
    plt.title("Graph color-coded by Louvain community")
    plt.show()



def visualize(graph, communities):
    # create dict with labels 
    node = list(graph.nodes)
    labels = [i \
    for i in graph.nodes]
    nodelabels = dict(zip(node, labels))
# todo add legend per dept
    # create and order community mappings
    communities = communities.to_node_community_map()
    # communities = [communities[k].pop() for k in node]
    # due to previous error: network reduced to a single node or not reduced, attempted pop from empty list
    ordered_communities = []
    for k in node:
        if communities[k]:
            ordered_communities.append(communities[k].pop())
        else:
            # If communities[k] is empty, keep it as it is
            pass
            # ordered_communities.append(None) # Filter out None values
    # create color map
    pastel2 = cm.get_cmap('Pastel2', max(ordered_communities) + 1)
    # visualize
    np.random.seed(123)
    # todo add nodelabels as legend
    nx.draw_spring(graph, labels = nodelabels, cmap = pastel2, node_color = ordered_communities, edge_color = "grey")
    # nx.draw_spring(graph, cmap = pastel2, node_color = ordered_communities, edge_color = "grey")

    plt.show()

def question7(ground_truth_community):
    print('Question 7: Visualize the graph color-coded by the Louvain community, and then visualize the graph separately color-coded by the ground truth department. Compare the visualizations. Can you describe any of the Louvain communities in terms of departments?') 
    print('Louvain community structure')
    # Visualize Louvain community structure
    print('Ground truth department structure')
    print(ground_truth_community)
    visualize(und_graph_email, louvain_email)
    # todo this makes no sense it has a single dept
    visualize(und_graph_email, ground_truth_community)


def get_dfs_vertex_by_comm_dept(graph, louvain, df_vertices):
    df_louvain = pd.DataFrame(louvain.communities).transpose()
    # Melt the DataFrame df_louvain to have 'community' and 'vertex' columns
    df_louvain_melted = df_louvain.melt(var_name='community', value_name='vertex')
    df_louvain_melted.dropna(subset=['vertex'], inplace=True)
    # Create a new DataFrame by merging email_vertices with df_louvain_melted
    df_comm_dept_per_vertex = pd.merge(df_louvain_melted, df_vertices, left_on='vertex', right_on='id', how='left')
    # drop repeated column
    df_comm_dept_per_vertex.drop(columns=['id'], inplace=True)
    # Drop rows with NaN values
    print(df_comm_dept_per_vertex) #  986 nodes ok
    # get the total number of rows
    total_rows = df_comm_dept_per_vertex.shape[0]
    # Count the occurrences of each community value
    community_counts = df_comm_dept_per_vertex['community'].value_counts()
    # Calculate the percentage of each community
    percentage_per_community = community_counts / total_rows * 100
    return df_comm_dept_per_vertex, percentage_per_community

def question8(graph, louvain, df_vertices):
    print('Question 8: Create a dataframe containing the community and department for each vertex. Manipulate this dataframe to show the percentage of individuals from each department in each community. Try to visualize this using a heatmap or other style of visualization and try to use this to describe the communities in terms of departments.')    
    df_comm_dept_per_vertex, percentage_per_community = get_dfs_vertex_by_comm_dept(graph, louvain, df_vertices)   
    print('vertex percentage by community:')
    print('community  |  vertex id')
    print(percentage_per_community)
    print('community  |  vertex id  |  dept')
    print(df_comm_dept_per_vertex)
    # plotting heatmap
    # Convert percentage_per_community Series to a DataFrame with 'community' as index
    df_heatmap = percentage_per_community.reset_index(name='percentage').rename(columns={'index': 'community'})
    plt.figure(figsize=(10, 6))
    plt.title('Percentage of individuals in each community')
    sns.heatmap(df_heatmap[['percentage']], cmap='YlGnBu', annot=True, fmt='.2f', cbar=True)
    plt.xlabel('Vertex Percentage')
    plt.ylabel('Community ID')
    plt.show()

# returns lagrest clique size, list of largest cliques
def largest_cliques_info(graph):
    cliques = sorted(nx.find_cliques(graph), key=len, reverse=True)
    clique_sizes = [len(c) for c in cliques]
    max_clique_size = max(clique_sizes)
    largest_cliques = [c for c in cliques if len(c) == max_clique_size]
    return max_clique_size, largest_cliques

# ref https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.clique.find_cliques.html
def question9(graph):
    print('Question 9: Find the largest clique size in the graph. How many such largest cliques are there? What do you think a clique represents in this context?')
    max_clique_size, largest_cliques = largest_cliques_info(graph)
    amount_largest_cliques = largest_cliques.count(max_clique_size)
    print('Largest clique size ' + str(max_clique_size))
    print('Amount of largest cliques ' + str(amount_largest_cliques))
    


def question10(df_cliques, largest_cliques):
    print('Question 10: Try to visualize the members of these cliques in the context of the entire graph. What can you conclude?')
    df_cliques['vertex'] = df_cliques['vertex'].astype(int)
    # Iterate through cliques in largest_cliques
    for i, clique in enumerate(largest_cliques):
        # Create a new column name based on the clique index
        column_name = f"clique{i}"
        # Define a lambda function to check if vertex is in the clique
        df_cliques[column_name] = df_cliques['vertex'].isin(clique)
        # # print(len(cliques))
        # print((largest_cliques))
        print(df_cliques.head(7))
      
def question11(graph):
    print('Question 11: Use the Leiden community detection algorithm to find a vertex partition with optimal modularity. How many communities does the Leiden algorithm detect?')
    leiden_comms = algorithms.leiden(graph)
    print('Amount of communities detected by cdlib.algorithms.leiden(): ' + str(len(leiden_comms.communities)))

def question12(graph, leiden, louvain):
    print('Question 12: Compare the Leiden partition modularity to the Louvain partition modularity.')

    leiden_modularity = evaluation.newman_girvan_modularity(graph , leiden).score
    louvain_modularity = evaluation.newman_girvan_modularity(graph , louvain).score
    print('Leiden modularity: ' + str(leiden_modularity))
    print('Louvain modularity: ' + str(louvain_modularity))
    print('Leiden/Louvain percentage: ' + str((leiden_modularity / louvain_modularity) * 100))


def get_unique_vertices_in_list_of_cliques(cliques):
# Use set comprehension to collect unique elements from flattened sublists
  return list(set([vertex for sublist in cliques for vertex in sublist]))


def compare_community_algos(graph, communities_list):
    for community_algo_results in communities_list:
        viz.plot_network_clusters(graph, community_algo_results)
    plt.show()
    

def question13(graph, communities_algos_result_list):
    compare_community_algos(graph, communities_algos_result_list)



# load csv data 
df_wikivote = wikivote()
df_email_edgelist = email_edgelist()
df_email_vertices = email_vertices()
und_graph_email = nx.from_pandas_edgelist(df_email_edgelist, source='from', target='to', create_using=nx.Graph)

# create directed graph
dir_graph_wikivote = nx.from_pandas_edgelist(df_wikivote, source='from', target='to', create_using=nx.DiGraph())

# question1()
# question2()
# question3()

df_email_edgelist = email_edgelist()
graph = nx.from_pandas_edgelist(df_email_edgelist, source='from', target='to', create_using=nx.Graph)
#und_graph_email = question4(und_graph_email) # network reduced to largest
# question4(und_graph_email)

louvain_email = question5(und_graph_email) # todo independent questions
# ground_truth_dept_community = question6(louvain_email)

# question7(ground_truth_dept_community) # todo fix looks sketchy that theyre all the same color-- all same dept?
# question8(und_graph_email, louvain_email, df_email_vertices)
df_comm_dept_per_vertex, percentage_per_community = get_dfs_vertex_by_comm_dept(und_graph_email, louvain_email, df_email_vertices)
# question9(und_graph_email)
max_clique_size, largest_cliques = largest_cliques_info(und_graph_email)
vertices_in_largest_cliques = get_unique_vertices_in_list_of_cliques(largest_cliques)

df_cliques = df_comm_dept_per_vertex.copy()
# question10(df_cliques, largest_cliques)

# checking amount of nodes that should be in graph
# print(nx.from_pandas_edgelist(email_edgelist(), source='from', target='to', create_using=nx.Graph).number_of_nodes())


# question11(und_graph_email)
leiden_email = algorithms.leiden(und_graph_email)
question13(und_graph_email, [louvain_email, leiden_email])

# COMPARE REF https://cdlib.readthedocs.io/en/latest/reference/viz.html



# TODO IN COMPARE COMMUNITES USE MODILARITY SCORES
# TODO VISUAL REPRESENTATION FOR COMPARE QUESTIONS
