import numpy as np
from collections import defaultdict
from rdflib import Graph, Namespace, RDF, RDFS, Literal
import rdflib

class Vertex(object):
    vertex_counter = 0
    
    def __init__(self, name, predicate=False, _from=None, _to=None):
        self.name = name
        self.predicate = predicate
        self._from = _from
        self._to = _to

        self.id = Vertex.vertex_counter
        Vertex.vertex_counter += 1
        
    def __eq__(self, other):
        if other is None: 
            return False
        return self.__hash__() == other.__hash__()
    
    def __hash__(self):
        if self.predicate:
            return hash((self.id, self._from, self._to, self.name))
        else:
            return hash(self.name)

    def __lt__(self, other):
        return self.name < other.name


class KnowledgeGraph(object):
    def __init__(self):
        self._vertices = set()
        self._transition_matrix = defaultdict(list)
        self._inv_transition_matrix = defaultdict(list)

        # initializing graph confidence matrix
        self._confidence_values_matrix=defaultdict(dict)
        #inverse graph conf matrix
        self._inv_confidence_values_matrix=defaultdict(dict)
        
    def add_vertex(self, vertex):
        """Add a vertex to the Knowledge Graph."""
        if vertex.predicate:
            self._vertices.add(vertex)
        else:
            self._vertices.add(vertex)

    def add_edge(self, v1, v2, conf):
        """Add a uni-directional edge."""
        self._transition_matrix[v1].append(v2)
        self._inv_transition_matrix[v2].append(v1)
        
        # adding confidence values to matrix
        self._confidence_values_matrix[v1][v2]=conf
        self._inv_confidence_values_matrix[v2][v1]=conf
        
    def remove_edge(self, v1, v2):
        """Remove the edge v1 -> v2 if present."""
        if v2 in self._transition_matrix[v1]:
            self._transition_matrix[v1].remove(v2)#
            self._confidence_values_matrix[v1][v2]=0

    def get_neighbors(self, vertex):
        """Get all the neighbors of vertex (vertex -> neighbor)."""
        return self._transition_matrix[vertex]#, self._confidence_values_matrix[vertex]
    
    def get_neighbors_conf_val(self, vertex):
        """Get all the neighbors of vertex (vertex -> neighbor)."""
        return self._confidence_values_matrix[vertex]
    
    def get_inv_neighbors(self, vertex):
        """Get all the neighbors of vertex (vertex -> neighbor)."""
        return self._inv_transition_matrix[vertex]#, self._inv_confidence_values_matrix[vertex]
    
    def get_inv_neighbors_conf_val(self, vertex):
        """Get all the neighbors of vertex (vertex -> neighbor)."""
        return self._inv_confidence_values_matrix[vertex]
    
    def visualise(self):
        """Visualise the graph using networkx & matplotlib."""
        import matplotlib.pyplot as plt
        import networkx as nx
        nx_graph = nx.DiGraph()
        
        for v in self._vertices:
            if not v.predicate:
                name = v.name.split('/')[-1]
                nx_graph.add_node(name, name=name, pred=v.predicate)
            
        for v in self._vertices:
            if not v.predicate:
                v_name = v.name.split('/')[-1]
                # Neighbors are predicates
                for pred in self.get_neighbors(v):
                    pred_name = pred.name.split('/')[-1]
                    for obj in self.get_neighbors(pred):
                        obj_name = obj.name.split('/')[-1]
                        conf = self._confidence_values_matrix[v][pred]
                        nx_graph.add_edge(v_name, obj_name, name=pred_name+' '+str(conf))
        
        plt.figure(figsize=(10,10))
        _pos = nx.circular_layout(nx_graph)
        nx.draw_networkx_nodes(nx_graph, pos=_pos, node_size=50)
        nx.draw_networkx_edges(nx_graph, pos=_pos, width=0.5)
        nx.draw_networkx_labels(nx_graph, pos=_pos, font_size=7.5)
        names = nx.get_edge_attributes(nx_graph, 'name')
        nx.draw_networkx_edge_labels(nx_graph, pos=_pos, edge_labels=names, font_size=6)

        plt.show()

    def kg_to_owl(self, kg2owl):
     

        # Create a new RDF graph
        graph = Graph()

        # Define namespaces for RDF and OWL
        rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        owl = Namespace("http://www.w3.org/2002/07/owl#")

        # Create OWL class and property URIs
        vertex_class_uri = owl.Vertex
        transition_property_uri = owl.transition
        inverse_transition_property_uri = owl.inverseTransition
        # Add OWL class definitions
        graph.add((vertex_class_uri, RDF.type, owl.Class))
        graph.add((vertex_class_uri, RDFS.label, Literal("Vertex")))

        # Add vertices as instances of the OWL class
        for vertex in self._vertices:
            graph.add((vertex, RDF.type, vertex_class_uri))

        # Add transition matrix relations as OWL property assertions
        for vertex, transitions in self._transition_matrix.items():
            for transition in transitions:
                graph.add((rdflib.URIRef(vertex), transition_property_uri, transition))
        # Add OWL class definitions
        graph.add((vertex_class_uri, RDF.type, owl.Class))
        graph.add((vertex_class_uri, RDFS.label, Literal("Vertex")))

        # Add vertices as instances of the OWL class
        for vertex in self._vertices:
            graph.add((rdflib.URIRef(vertex), RDF.type, vertex_class_uri))

        # Add transition matrix relations as OWL property assertions
        for vertex, transitions in self._inv_transition_matrix.items():
            for transition in transitions:
                graph.add((rdflib.URIRef(vertex), inverse_transition_property_uri, transition))

        # Serialize the RDF graph to an OWL/XML file
        graph.serialize(kg2owl, format="xml")

        