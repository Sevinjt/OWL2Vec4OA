from owl2vec_star.rdf2vec.walkers.random import Walker
from owl2vec_star.rdf2vec.graph import KnowledgeGraph, Vertex
import numpy as np
from hashlib import md5
import rdflib
import networkx as nx
import random as rnd
from array import *
from rdflib import URIRef, Literal, BNode
import configparser
import logging
import os

#from tqdm import tqdm

edges = []

class Mapping4Vec(Walker):
    def __init__(self, depth, walks_per_graph,class_onto1, class_onto2, confidence_threshold):
        # print("Depth:", depth)
        # print("walks_per_graph:", walks_per_graph)
        super(Mapping4Vec, self).__init__(depth, walks_per_graph)
        self.class_onto1=class_onto1
        self.class_onto2=class_onto2
        self.pct_wl_sz1_lst=list()
        self.pct_wl_sz2_lst=list()
        self.confidence_threshold = confidence_threshold
        
    def printVertex(self, vertex):
        print(".")
        print("From Subject:", vertex.id)
        print("From Predicate:", vertex.predicate)
        print("From Object:", vertex.name)
        print("From From:", vertex._from)
        print("From To:", vertex._to)

    def get_edge_confidence(self, graph, node, neighbor):
        # Define a method to get the confidence value of an edge
        # This example assumes edges have a 'confidence' attribute
        # self.printVertex(node)
        # self.printVertex(neighbor)
        
        node_edges = graph.get_neighbors(node)
        # print("Edges:", len(node_edges))
        # print(node_edges)
        if (len(node_edges)>0):
           # print("Edges length:",len(node_edges))
           foundEdge = self.referencedVertices(node, neighbor, graph)
           # foundEdge = next(iter([v for v in node_edges if v[0] == neighbor.id]), None)
           
           # print("foundEdge:",foundEdge)
           if foundEdge is None:
              confidence = 1.0
           else:
              confidence = foundEdge[0][2]
        else:
           confidence=1.0
        return confidence
    
    @classmethod
    def referencedVertices(self,vertex, neighbor, kg):
        edge = []

        # info in the edges between nodes are added to the transition matrix. 
        # they have confidence value info 
        confidence_value=kg._confidence_values_matrix[vertex][neighbor]

        # mapping
        # object = vertex.name.partition('#')[0]
        # subject = vertex.name.partition('#')[2]
        predicate = vertex.predicate
        if "subClassOf" in vertex.name:
              # print("adding to subClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)               
              edge.append((vertex.name, neighbor.name, confidence_value,predicate))
        elif "superClassOf" in vertex.name:
              # print("adding to superClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
        elif "EquivalentOf" in vertex.name:
              # print("adding to superClassOf edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
        else: 
              # Edge
              predicate = vertex.predicate
              # print("adding to Edge edges:", vertex.name, neighbor.name, confidence_value, predicate)
              edge.append((vertex.name, neighbor.name, confidence_value, predicate))
              
        return edge
    

    # extracts random walks from knowlwedge graph 
    def extract_random_walks(self, graph, root, nodes_times):
        #wl_sz is walk size of onto1 and onto2
    
        """Extract random walks of depth - 1 hops rooted in root."""
        # Initialize one walk of length 1 (the root)
        walks = {(root,)}
        
        for i in range(self.depth):
            walks_copy = walks.copy()
            # print("walks length:", len(walks))
            for walk in walks_copy:
                node = walk[-1]
                #print("Node:", node)
                
                node_name=node.name
                nodes_times[node_name] = nodes_times.get(node_name, 0) + 1

                if node_name in self.class_onto1:
                    self.set_wl_node1.add(node_name)
                if node_name in self.class_onto2:
                    self.set_wl_node2.add(node_name)
                


                # get the edges which already have the confidences
                neighbors = graph.get_neighbors(node)

                if len(neighbors) > 0:
                    #print("Node:", node)
                    #print("Neighbours length:", len(neighbors))
                    walks.remove(walk)

                    for neighbor in neighbors:
                        foundEdge = self.referencedVertices(node, neighbor, graph)
                        if foundEdge[0][2] >= float(self.confidence_threshold) and foundEdge[0][2] != 0:
                            chosen_neighbor=neighbor
                            walks.add(walk + (chosen_neighbor, ))
                            
                            n_n=chosen_neighbor.name
                            #n_n1 = node.name
                            nodes_times[n_n] = nodes_times.get(n_n, 0) + 1
                            #nodes_times[n_n1] = nodes_times.get(n_n1, 0) + 1

                            if n_n in self.class_onto1:
                                self.set_wl_node1.add(n_n)
                            if n_n in self.class_onto2:
                                self.set_wl_node2.add(n_n)
                                                    
                    
            if self.walks_per_graph is not None:
                n_walks = min(len(walks),  self.walks_per_graph)
                walks_ix = np.random.choice(range(len(walks)), replace=False,
                                            size=n_walks)

                if len(walks_ix) > 0:
                    walks_list = list(walks)
                    walks = {walks_list[ix] for ix in walks_ix}  

        return list(walks)

        
    def extract(self, graph, instances):
        canonical_walks = set()
        import time
        import statistics
        means=[]
        times=[]
        self.nodes_times = dict()

        # for experimental purposes change k 
        # walker runs k times
        k=1
        for i in range(k):
            hops=[]
            walks_list=[]
            self.set_wl_node1=set()
            self.set_wl_node2=set()
            # Record the starting time
            start_time = time.time()
            for instance in instances:
                walks = self.extract_random_walks(graph, Vertex(str(instance)), nodes_times=self.nodes_times)
                for walk in walks:
                    canonical_walk = []
                    i=0
                    # print("walk:", walk)
                    for i, hop in enumerate(walk):
                        # print("type hop",i,':', hop.name)
                        if i == 0 or i % 2 == 1:
                            if isinstance(hop, tuple):
                                canonical_walk.append(hop[1].name)
                            else: 
                                canonical_walk.append(hop.name)
                        else:
                            if isinstance(hop, tuple):
                                canonical_walk.append(hop[1].name)
                            else: 
                                canonical_walk.append(hop.name)
                    hops.append(len(walk))
                    canonical_walks.add(tuple(canonical_walk))
            # Calculate the time taken by the process
            end_time = time.time()
            elapsed_time = end_time - start_time
            # Calculate the mean
            mean = statistics.mean(hops)

            # Calculate the standard deviation
            walks_list.append(len(walks))
            means.append(mean)
            times.append(elapsed_time)
        
            self.pct_wl_sz1=(len(self.set_wl_node1)/len(self.class_onto1))*100
            self.pct_wl_sz2=(len(self.set_wl_node2)/len(self.class_onto2))*100
            self.pct_wl_sz1_lst.append(self.pct_wl_sz1)
            self.pct_wl_sz2_lst.append(self.pct_wl_sz2)

        mean_means_hop = statistics.mean(means)

        mean_times_hop = statistics.mean(times)
        # we run the system k times this is why we find mean ve std deviation
        logging.info('Experiment results:\n')
        logging.info(f'Number of nodes {len(instances)}')
        #walk da ferqli hop sizelar olur her walkdan ortalama tapilmis meanlarin k rundaki meanini tapriq
        logging.info(f"Mean of mean hops: {mean_means_hop:.2f}")

        logging.info(f"Mean Time walks taken by the {k} process: {mean_times_hop:.7f} seconds")
        logging.info(f"Mean of percentage of visited nodes in ontology  1: {statistics.mean(self.pct_wl_sz1_lst):.2f}%" )
        logging.info(f"Mean of percentage of visited nodes in ontology  2: {statistics.mean(self.pct_wl_sz2_lst):.2f}%\n")
        sorted_nodes_times = sorted(self.nodes_times.items(), key=lambda x:x[1], reverse=True)
        self.nodes_times = dict(sorted_nodes_times)
        
        # shows how many time node accessed
        logging.info(f'Visited nodes with numbers {self.nodes_times}\n')
        
        allnodes = self.class_onto1.union(self.class_onto2)
        walked_nodes = self.set_wl_node1.union(self.set_wl_node2)
        logging.info(f"Coverage nodes {(len(walked_nodes)/len(allnodes))*100 :.2f}\n\n")
        
        return canonical_walks
