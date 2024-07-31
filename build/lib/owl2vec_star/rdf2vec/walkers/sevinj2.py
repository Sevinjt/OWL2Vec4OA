from owl2vec_star.rdf2vec.walkers.random import Walker
from owl2vec_star.rdf2vec.graph import KnowledgeGraph, Vertex
import numpy as np
from hashlib import md5
import rdflib
import networkx as nx
import random as rnd
from array import *
from rdflib import URIRef, Literal, BNode

edges = []

class SevinjWalker(Walker):
    def __init__(self, depth, walks_per_graph):
        print("Depth:", depth)
        print("walks_per_graph:", walks_per_graph)
        super(SevinjWalker, self).__init__(depth, walks_per_graph)
        
    def printVertex(self, vertex):
        print(".")
        print("From Subject:", vertex.id)
        print("From Predicate:", vertex.predicate)
        print("From Object:", vertex.name)
        print("From From:", vertex._from)
        print("From To:", vertex._to)

    def get_edge_confidence(self, node, neighbor):
        # Define a method to get the confidence value of an edge
        # This example assumes edges have a 'confidence' attribute
        self.printVertex(node)
        self.printVertex(neighbor)
        print("Edges:", len(node.edges))
        print("get edge conf", edges)

        if (len(edges)>0):
           print("Edges length:",len(edges))
           foundEdge = next(iter([v for v in edges if v[0] == neighbor.id]), None)
           print("foundEdge:",foundEdge)
           if foundEdge is None:
              confidence = 1.0
           else:
              confidence = foundEdge[3]
        else:
           confidence=1.0
        return confidence
    
    @classmethod
    def referencedVertices(self,vertex):
        edges = []

        if isinstance(vertex._from, Vertex):
             self.referencedVertices(vertex._from)
                         
        if isinstance(vertex._to, Vertex):
             self.referencedVertices(vertex._to)

        # mapping
        object = vertex.name.partition('#')[0]
        subject = vertex.name.partition('#')[2]
        predicate = vertex.predicate
        if "subClassOf" in vertex.name:
              print("adding to subClassOf edges:", vertex.name, object, predicate, subject)               
              edges.append((object, 'subClassOf', subject, rnd.random()))
        elif "superClassOf" in vertex.name:
              print("adding to superClassOf edges:", vertex.name, object, predicate, subject)
              edges.append((object, 'superClassOf', subject, rnd.random()))
        elif "EquivalentOf" in vertex.name:
              print("adding to superClassOf edges:", vertex.name, object, predicate, subject)
              edges.append((object, 'EquivalentOf', subject, rnd.random()))
        else: 
              #Edge
              object = vertex.name.partition('#')[0]
              subject = vertex.name.partition('#')[2]
              predicate = vertex.predicate
              print("adding to Edge edges:", vertex.name, object, predicate, subject)
              edges.append((object, predicate, subject, 1.0))
              
        return edges
    
    @classmethod
    def get_edges(self,knowledgegraph, node):

            graph = rdflib.Graph();
            edges = []
            
            vertices = knowledgegraph._vertices
            

            for vertex in vertices:
                if vertex == node:
                   print("matched node so extracting edges...", vertex)
                   return self.referencedVertices(vertex)
                   break
        

    def extract_random_walks(self, graph, root):
    	
    	
        """Extract random walks of depth - 1 hops rooted in root."""
        # Initialize one walk of length 1 (the root)
        walks = {(root,)}

        for i in range(self.depth):
            walks_copy = walks.copy()
            #print("walks length:", len(walks))
            for walk in walks_copy:
                node = walk[-1]
                #print("Node:", node)
                
                # get the edges which already have the confidences
                node.edges = self.get_edges(graph, node)
                #print(node.edges)
                # now get the nodes neighbors
                neighbors = graph.get_neighbors(node)
                #print("Neighbours length:", len(neighbors))

                if len(neighbors) > 0:
                    #print("Node:", node)
                    #print("Neighbours length:", len(neighbors))
                    walks.remove(walk)

                    # Calculate the probability distribution for neighbor selection
                    confidences = [self.get_edge_confidence(node, neighbor) for neighbor in neighbors]
                    total_confidence = sum(confidences)
                    print("total_confidence", total_confidence)
                    probabilities = [confidence / total_confidence for confidence in confidences]

                    # Choose a neighbor based on the probability distribution
                    chosen_neighbor = np.random.choice(list(neighbors), p=probabilities, size=1)[0]
                    print("adding to walks walk: ", walk, chosen_neighbor)
                    walks.add((walk, chosen_neighbor))
                    #print("walks length:", len(walks))
                    print(walks)

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
        for instance in instances:
            walks = self.extract_random_walks(graph, Vertex(str(instance)))
            for walk in walks:
                canonical_walk = []
                print("walk:", walk)
                for i, hop in enumerate(walk):
                    print("type hop:", hop)
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

                canonical_walks.add(tuple(canonical_walk))

        return canonical_walks
        
    # g = rdflib.Graph

    # kg = KnowledgeGraph()

    # graphN = rdflib.Graph

    # ontology_files = [ontology_file1, ontology_file2, mapping]

    # construct_kg_walker(ontology_files, "Random", g)
    
 # g = rdflib.Graph
 #graphN = rdflib.Graph()
 #graph.parse(onto_file1, format='xml')

 #g = rdflib.Graph()
 #g.parse(data=graph.serialize(format='nt'), format='nt')
 # ontology_files = ['ontology1.owl', 'ontology2.owl', 'ontology3.rdf']
 # construct_kg_walker(ontology_files, "Random", g)