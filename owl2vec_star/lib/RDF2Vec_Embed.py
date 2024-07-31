import configparser
import rdflib
import sys
import numpy as np
import rdflib
from rdflib import URIRef, Literal, BNode
import time
import os

from owl2vec_star.rdf2vec.embed import RDF2VecTransformer
from owl2vec_star.rdf2vec.graph import KnowledgeGraph, Vertex
from owl2vec_star.rdf2vec.walkers.random import RandomWalker
from owl2vec_star.rdf2vec.walkers.weisfeiler_lehman import WeisfeilerLehmanWalker
from owl2vec_star.rdf2vec.walkers.mapping4vec import Mapping4Vec
from owl2vec_star.lib.Onto_Projection import Reasoner, OntologyProjection
from rdflib import OWL, Graph
import configparser
from rdflib.namespace import RDF, RDFS
from rdflib import Graph, RDF, RDFS


def construct_kg_walker(ontology_file, mapping_file, walker_type, walk_depth, config):
    global classes 
    global class_onto1
    global class_onto2

    mapping_file = config['BASIC']['mapping']
    confidence_threshold = config['BASIC']['confidence_threshold']
    
    class_onto1 = set()
    class_onto2 = set()
    g = rdflib.Graph()
    if ontology_file.endswith('ttl') or ontology_file.endswith('TTL'):
        g.parse(ontology_file, format='turtle')
    else:
        g.parse(ontology_file)
    
    kg = KnowledgeGraph()
    for (s, p, o) in g:
        s_v, o_v = Vertex(str(s)), Vertex(str(o))
        p_v = Vertex(str(p), predicate=True, _from=s_v, _to=o_v)
        kg.add_vertex(s_v)
        kg.add_vertex(p_v)
        kg.add_vertex(o_v)
        kg.add_edge(s_v, p_v, 1.0)
        kg.add_edge(p_v, o_v, 1.0)

    with open(os.path.join(config['DOCUMENT']['cache_dir'], 'entities_onto1.txt'), 'r+', encoding="utf-8") as f:
        for i in f.readlines():
          class_onto1.add(str(i.strip('\n').strip()))

    with open(os.path.join(config['DOCUMENT']['cache_dir'], 'entities_onto2.txt'), 'r+', encoding="utf-8") as f:
        for i in f.readlines():
          class_onto2.add(str(i.strip('\n').strip()))
        
    

    seed_entities=set()
    if mapping_file.split('.')[-1]=='txt':
        reader = open(mapping_file, "r+")
        lines = reader.readlines()
        for line in lines:
            dat=line.split("|")
            
            subject = rdflib.URIRef(str(dat[0]))
            predicate = rdflib.URIRef(str(dat[2]))
            object = rdflib.Literal(str(dat[1]))
            confidence_value =float(dat[3])
                
            s_v, o_v = Vertex(str(subject)), Vertex(str(object))
            p_v = Vertex(str(predicate), predicate=True, _from=s_v, _to=o_v)
            kg.add_vertex(s_v)
            kg.add_vertex(p_v)
            kg.add_vertex(o_v)
            kg.add_edge(s_v, p_v, confidence_value)
            kg.add_edge(p_v, o_v, confidence_value)
            seed_entities.add(str(subject))
            seed_entities.add(str(object))
        
    elif mapping_file.split('.')[-1]=='owl':
        reader = open(mapping_file, "r+")
        lines = reader.readlines()
        for line in lines:
            if line.startswith('        <entity1'):
                quotInd1 = line.index(">")
                quotInd2 = line.index("<",quotInd1+1)
                subject=str(line[quotInd1+1: quotInd2])
                continue
            if line.startswith('        <entity2'):
                quotInd1 = line.index(">")
                quotInd2 = line.index("<",quotInd1+1)
                object=str(line[quotInd1+1: quotInd2])
                continue
            if line.startswith('        <measure'):
                quotInd1 = line.index(">")
                quotInd2 = line.index("<",quotInd1+1)
                confidence_value=float(line[quotInd1+1: quotInd2])
                predicate = str('=')
		
                s_v, o_v = Vertex(str(subject)), Vertex(str(object))
                p_v = Vertex(str(predicate), predicate=True, _from=s_v, _to=o_v)
                kg.add_vertex(s_v)
                kg.add_vertex(p_v)
                kg.add_vertex(o_v)
                kg.add_edge(s_v, p_v, confidence_value)
                kg.add_edge(p_v, o_v, confidence_value)
                seed_entities.add(str(subject))
                seed_entities.add(str(object))
                continue
        
    elif mapping_file.split('.')[-1]=='rdf':
        reader = open(mapping_file, "r+")
        lines = reader.readlines()
        for line in lines:
            if line.startswith('		<entity1 '):
                quotInd1 = line.index("=")
                quotInd2 = line.index(">",quotInd1+1)
                subject=str(line[quotInd1+1: quotInd2-1])
                continue
            if line.startswith('		<entity2 '):
                quotInd1 = line.index("=")
                quotInd2 = line.index(">",quotInd1+1)
                object=str(line[quotInd1+1: quotInd2-1])
                continue
            if line.startswith('		<measure '):
                quotInd1 = line.index(">")
                quotInd2 = line.index("<",quotInd1+1)
                confidence_value=float(line[quotInd1+1: quotInd2])
                predicate = str('=')
		
                s_v, o_v = Vertex(str(subject)), Vertex(str(object))
                p_v = Vertex(str(predicate), predicate=True, _from=s_v, _to=o_v)
                kg.add_vertex(s_v)
                kg.add_vertex(p_v)
                kg.add_vertex(o_v)
                kg.add_edge(s_v, p_v, confidence_value)
                kg.add_edge(p_v, o_v, confidence_value)
                seed_entities.add(str(subject))
                seed_entities.add(str(object))
                continue

    elif mapping_file.split('.')[-1]=='tsv':
        reader = open(mapping_file, "r+")
        lines = reader.readlines()
        for line in lines:
            dat=line.split("\t")
            
            subject = rdflib.URIRef(str(dat[0]))
            object = rdflib.Literal(str(dat[1]))
            confidence_value =float(dat[2])
            predicate = str('=')
		
            s_v, o_v = Vertex(str(subject)), Vertex(str(object))
            p_v = Vertex(str(predicate), predicate=True, _from=s_v, _to=o_v)
            kg.add_vertex(s_v)
            kg.add_vertex(p_v)
            kg.add_vertex(o_v)
            kg.add_edge(s_v, p_v, confidence_value)
            kg.add_edge(p_v, o_v, confidence_value)
            seed_entities.add(str(subject))
            seed_entities.add(str(object))

    if config['BASIC']['seed_entities_on_mapping'] == 'yes':
        classes = seed_entities    
    else:
        classes = class_onto1.union(class_onto2)

    if walker_type.lower() == 'random':
        walker = RandomWalker(depth=walk_depth, walks_per_graph=float('inf'))
    elif walker_type.lower() == 'wl':
        walker = WeisfeilerLehmanWalker(depth=walk_depth, walks_per_graph=float('inf'))
    elif walker_type.lower() == 'mapping4vec':
        walker = Mapping4Vec(depth=walk_depth, walks_per_graph=float('inf'),class_onto1=class_onto1, class_onto2=class_onto2, confidence_threshold=confidence_threshold)
    else:
        print('walker %s not implemented' % walker_type)
        sys.exit()
    #print(classes)
    return kg, walker, classes

#this function is not used because this function is a transformer embedding model,
# since we are using word2vec what we need to do is to get data and send to gensim 
def get_rdf2vec_embed(ontology_file, mapping_file, walker_type, walk_depth, embed_size, classes, config):
    
    kg, walker, classes = construct_kg_walker(ontology_file = ontology_file,
                                            mapping_file=mapping_file,
                                            walker_type=walker_type,
                                            walk_depth=walk_depth, 
                                            config=config)
    
    if isinstance(walker, Mapping4Vec):
        transformer = RDF2VecTransformer(walkers=[walker], vector_size=embed_size)
    else:
        transformer = RDF2VecTransformer(walkers=walker, vector_size=embed_size)
    instances = [rdflib.URIRef(c) for c in classes]
    walk_embeddings = transformer.fit_transform(graph=kg, instances=instances)
    # print(instances)
    return np.array(walk_embeddings)



def get_rdf2vec_walks(ontology_file, mapping_file, walker_type, walk_depth, classes, config):
    kg, walker, classes = construct_kg_walker(ontology_file = ontology_file,
                                            mapping_file=mapping_file,
                                            walker_type=walker_type,
                                            walk_depth=walk_depth, 
                                            config=config)
    
    #kg.visualise()
    instances = [rdflib.URIRef(c) for c in classes]
    walks_ = list(walker.extract(graph=kg, instances=instances))

    return walks_,instances
