import os
import numpy as np
import time
import argparse
import random
import multiprocessing
import gensim
import configparser

from owl2vec_star.lib.RDF2Vec_Embed import get_rdf2vec_walks, get_rdf2vec_embed
from owl2vec_star.lib.Label import pre_process_words, URI_parse
from owl2vec_star.lib.Onto_Projection import Reasoner, OntologyProjection
import nltk
nltk.download('punkt')


if __name__ == '__main__':
    from multiprocessing import freeze_support 
    freeze_support()
    parser = argparse.ArgumentParser()
    parser.add_argument("--ontology_file", type=str, default=None, help="The input ontology for embedding")
    parser.add_argument("--embedding_dir", type=str, default=None, help="The output embedding directory")
    parser.add_argument("--config_file", type=str, default='default1.cfg', help="Configuration file")
    parser.add_argument("--URI_Doc", help="Using URI document", action="store_true")
    parser.add_argument("--Lit_Doc", help="Using literal document", action="store_true")
    parser.add_argument("--Mix_Doc", help="Using mixture document", action="store_true")
    FLAGS, unparsed = parser.parse_known_args()

    # read and combine configurations
    # overwrite the parameters in the configuration file by the command parameters
    config = configparser.ConfigParser()
    config.read(FLAGS.config_file)
    # if FLAGS.ontology_file1 is not None:
    #     config['BASIC']['ontology_file1'] = FLAGS.ontology_file1
    # if FLAGS.ontology_file2 is not None:
    #     config['BASIC']['ontology_file2'] = FLAGS.ontology_file2
    # if FLAGS.mapping is not None:
    #     config['BASIC']['mapping'] = FLAGS.mapping
    if FLAGS.embedding_dir is not None:
        config['BASIC']['embedding_dir'] = FLAGS.embedding_dir
    if FLAGS.URI_Doc:
        config['DOCUMENT']['URI_Doc'] = 'yes'
    if FLAGS.Lit_Doc:
        config['DOCUMENT']['Lit_Doc'] = 'yes'
    if FLAGS.Mix_Doc:
        config['DOCUMENT']['Mix_Doc'] = 'yes'
    if 'cache_dir' not in config['DOCUMENT']:
        config['DOCUMENT']['cache_dir'] = './cache'
    if not os.path.exists(config['DOCUMENT']['cache_dir']):
        os.mkdir(config['DOCUMENT']['cache_dir'])
    if 'embedding_dir' not in config['BASIC']:
        config['BASIC']['embedding_dir'] = os.path.join(config['DOCUMENT']['cache_dir'], 'output'+'_'+config['DOCUMENT']['walk_depth'])
        config['BASIC']['embedding_vector_dir'] = os.path.join(config['DOCUMENT']['cache_dir'],"ontology"+'_'+config['DOCUMENT']['walk_depth']+".embeddings")

    print('1')
    ontology_file1 = config['BASIC']['ontology_file1']
    ontology_file2 = config['BASIC']['ontology_file2']
    mapping = config['BASIC']['mapping']
    start_time = time.time()
    if ('ontology_projection' in config['DOCUMENT'] and config['DOCUMENT']['ontology_projection'] == 'yes') or \
            'pre_entity_file' not in config['DOCUMENT'] or 'pre_axiom_file' not in config['DOCUMENT'] or \
            'pre_annotation_file' not in config['DOCUMENT']:
        print('\n Access the ontology ...')
        

        projection1 = OntologyProjection(config['BASIC']['ontology_file1'], reasoner=Reasoner.STRUCTURAL, only_taxonomy=False,
                                    bidirectional_taxonomy=True, include_literals=True, avoid_properties=set(),
                                    additional_preferred_labels_annotations=set(),
                                    additional_synonyms_annotations=set(),
                                    memory_reasoner='13351')

        projection2 = OntologyProjection(config['BASIC']['ontology_file2'], reasoner=Reasoner.STRUCTURAL, only_taxonomy=False,
                                            bidirectional_taxonomy=True, include_literals=True, avoid_properties=set(),
                                            additional_preferred_labels_annotations=set(),
                                            additional_synonyms_annotations=set(),
                                            memory_reasoner='13351')
        start_time = time.time()
        projection1.extractProjection()
        graph1 = projection1.getProjectionGraph()

        class_onto1 = set()
        for (a, b, c) in graph1:
            class_onto1.add(str(a))
            class_onto1.add(str(c))
        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'entities_onto1.txt'), 'w', encoding="utf-8") as f:
            for e in class_onto1:
                f.write('%s\n' % e)
    
        projection2.extractProjection()
        graph2 = projection2.getProjectionGraph()

        class_onto2 = set()
        for (a, b, c) in graph2:
            class_onto2.add(str(a))
            class_onto2.add(str(c))
        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'entities_onto2.txt'), 'w', encoding="utf-8") as f:
            for e in class_onto2:
                f.write('%s\n' % e)
          
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f'\n\n\nExtraction time for ontologies:{elapsed_time:.2f}')
        
        projection = graph1 + graph2      

        projection.serialize(config['BASIC']['ontology_file'], format="xml")      
        projection = OntologyProjection(config['BASIC']['ontology_file'], reasoner=Reasoner.STRUCTURAL, only_taxonomy=False,
                                    bidirectional_taxonomy=True, include_literals=True, avoid_properties=set(),
                                    additional_preferred_labels_annotations=set(),
                                    additional_synonyms_annotations=set(),
                                    memory_reasoner='13351')

    else:
        projection = None

    print('2')
    
    start_time = time.time()
    # Ontology projection
    if 'ontology_projection' in config['DOCUMENT'] and config['DOCUMENT']['ontology_projection'] == 'yes':
        print('\nCalculate the ontology projection ...')
        projection.extractProjection()
        onto_projection_file = os.path.join(config['DOCUMENT']['cache_dir'], 'projection.ttl')
        projection.saveProjectionGraph(onto_projection_file)
        ontology_file = onto_projection_file
    else:
        ontology_file = config['BASIC']['ontology_file']

    print('3')

    # Extract and save seed entities (classes and individuals)
    # Or read entities specified by the user
    if 'pre_entity_file' in config['DOCUMENT']:
        entities = [line.strip() for line in open(config['DOCUMENT']['pre_entity_file']).readlines()]
    else:
        print('\nExtract classes and individuals ...')
        projection.extractProjection()
        p_gr = projection.getProjectionGraph()
        entities = set()
        for (a, b, c) in p_gr:
            entities.add(str(a))
            entities.add(str(c))
        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'entities.txt'), 'w', encoding="utf-8") as f:
            for e in entities:
                f.write('%s\n' % e)

    print('4')

    # Extract axioms in Manchester Syntax if it is not pre_axiom_file is not set
    if 'pre_axiom_file' not in config['DOCUMENT']:
        print('\nExtract axioms ...')
        projection.createManchesterSyntaxAxioms()
        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'axioms.txt'), 'w', encoding="utf-8") as f:
            for ax in projection.axioms_manchester:
                f.write('%s\n' % ax)

    # If pre_annotation_file is set, directly read annotations
    # else, read annotations including rdfs:label and other literals from the ontology
    #   Extract annotations: 1) English label of each entity, by rdfs:label or skos:preferredLabel
    #                        2) None label annotations as sentences of the literal document
    uri_label, annotations = dict(), list()

    if 'pre_annotation_file' in config['DOCUMENT']:
        with open(config['DOCUMENT']['pre_annotation_file'],encoding="utf-8") as f:
            for line in f.readlines():
                tmp = line.strip().split()
                if tmp[1] == 'http://www.w3.org/2000/01/rdf-schema#label':
                    uri_label[tmp[0]] = pre_process_words(tmp[2:])
                else:
                    annotations.append([tmp[0]] + tmp[2:])

    else:
        print('\nExtract annotations ...')
        projection.indexAnnotations()
        for e in entities:
            if e in projection.entityToPreferredLabels and len(projection.entityToPreferredLabels[e]) > 0:
                label = list(projection.entityToPreferredLabels[e])[0]
                uri_label[e] = pre_process_words(words=label.split())
        for e in entities:
            if e in projection.entityToAllLexicalLabels:
                for v in projection.entityToAllLexicalLabels[e]:
                    if (v is not None) and \
                            (not (e in projection.entityToPreferredLabels and v in projection.entityToPreferredLabels[e])):
                        annotation = [e] + v.split()
                        annotations.append(annotation)

        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'annotations.txt'), 'w', encoding="utf-8") as f:
            for e in projection.entityToPreferredLabels:
                for v in projection.entityToPreferredLabels[e]:
                    f.write('%s preferred_label %s\n' % (e, v))
            for a in annotations:
                f.write('%s\n' % ' '.join(a))

    print('5')

    walk_sentences, axiom_sentences, URI_Doc = list(), list(), list()
    if 'URI_Doc' in config['DOCUMENT'] and config['DOCUMENT']['URI_Doc'] == 'yes':
        print('\nGenerate URI document ...')
        
        walks_,instances = get_rdf2vec_walks(ontology_file=ontology_file, mapping_file=mapping, walker_type=config['DOCUMENT']['walker'],
                                walk_depth=int(config['DOCUMENT']['walk_depth']), lasses=[], config = config)
        print('Extracted %d walks for %d seed entities' % (len(walks_), len(instances)))
        walk_sentences += [list(map(str, x)) for x in walks_]
        
        with open(os.path.join(config['DOCUMENT']['cache_dir'], 'new_axioms_'+ config['DOCUMENT']['walk_depth'] +'.txt'), 'w', encoding="utf-8") as f:
            for x in walks_:
                ax = "\t".join(x)
                f.write('%s\n' % ax)
        
                
        # print(walk_sentences)
        axiom_file = os.path.join(config['DOCUMENT']['cache_dir'], 'axioms.txt')
        if os.path.exists(axiom_file):
            for line in open(axiom_file).readlines():
                axiom_sentence = [item for item in line.strip().split()]
                axiom_sentences.append(axiom_sentence)
        print('Extracted %d axiom sentences' % (len(axiom_sentences)))
        URI_Doc = walk_sentences + axiom_sentences


    # Some entities have English labels
    # Keep the name of built-in properties (those starting with http://www.w3.org)
    # Some entities have no labels, then use the words in their URI name
    def label_item(item):
        if item in uri_label:
            return uri_label[item]
        elif item.startswith('http://www.w3.org'):
            return [item.split('#')[1].lower()]
        elif item.startswith('http://'):
            return URI_parse(uri=item)
        else:
            return [item.lower()]


    # read literal document
    # two parts: literals in the annotations (subject's label + literal words)
    #            replacing walk/axiom sentences by words in their labels
    Lit_Doc = list()
    if 'Lit_Doc' in config['DOCUMENT'] and config['DOCUMENT']['Lit_Doc'] == 'yes':
        print('\nGenerate literal document ...')
        for annotation in annotations:
            processed_words = pre_process_words(annotation[1:])
            if len(processed_words) > 0:
                Lit_Doc.append(label_item(item=annotation[0]) + processed_words)
        print('Extracted %d annotation sentences' % len(Lit_Doc))

        for sentence in walk_sentences:
            lit_sentence = list()
            for item in sentence:
                lit_sentence += label_item(item=item)
            Lit_Doc.append(lit_sentence)

        for sentence in axiom_sentences:
            lit_sentence = list()
            for item in sentence:
                lit_sentence += label_item(item=item)
            Lit_Doc.append(lit_sentence)

    # read mixture document
    # for each axiom/walk sentence, all): for each entity, keep its entity URI, replace the others by label words
    #                            random): randomly select one entity, keep its entity URI, replace the others by label words
    Mix_Doc = list()
    if 'Mix_Doc' in config['DOCUMENT'] and config['DOCUMENT']['Mix_Doc'] == 'yes':
        print('\nGenerate mixture document ...')
        for sentence in walk_sentences + axiom_sentences:
            if config['DOCUMENT']['Mix_Type'] == 'all':
                for index in range(len(sentence)):
                    mix_sentence = list()
                    for i, item in enumerate(sentence):
                        mix_sentence += [item] if i == index else label_item(item=item)
                    Mix_Doc.append(mix_sentence)
            elif config['DOCUMENT']['Mix_Type'] == 'random':
                random_index = random.randint(0, len(sentence) - 1)
                mix_sentence = list()
                for i, item in enumerate(sentence):
                    mix_sentence += [item] if i == random_index else label_item(item=item)
                Mix_Doc.append(mix_sentence)

    print('URI_Doc: %d, Lit_Doc: %d, Mix_Doc: %d' % (len(URI_Doc), len(Lit_Doc), len(Mix_Doc)))
    all_doc = URI_Doc + Lit_Doc + Mix_Doc

    print('Time for document construction: %s seconds' % (time.time() - start_time))
    random.shuffle(all_doc)

    # learn the embedding model (train a new model or fine tune the pre-trained model)
    start_time = time.time()
    if 'pre_train_model' not in config['MODEL'] or not os.path.exists(config['MODEL']['pre_train_model']):
        print('\nTrain the embedding model ...')
        model_ = gensim.models.Word2Vec(all_doc, size=int(config['MODEL']['embed_size']),
                                        window=int(config['MODEL']['window']),
                                        workers=multiprocessing.cpu_count(),
                                        sg=1, iter=int(config['MODEL']['iteration']),
                                        negative=int(config['MODEL']['negative']),
                                        min_count=int(config['MODEL']['min_count']), seed=int(config['MODEL']['seed']))
    else:
        print('\nFine-tune the pre-trained embedding model ...')
        model_ = gensim.models.Word2Vec.load(config['MODEL']['pre_train_model'])
        if len(all_doc) > 0:
            model_.min_count = int(config['MODEL']['min_count'])
            model_.build_vocab(all_doc, update=True)
            model_.train(all_doc, total_examples=model_.corpus_count, epochs=int(config['MODEL']['epoch']))
    
    # saved models loaded to generate embeddings 
    # we get words from model 
    # we find each vector mebedding for each word 
    # then we write it to the file for visualisation in the embedding space 
    model_.save(config['BASIC']['embedding_dir']+".bin")
    # Store just the words + their trained embeddings.
    model_.save(config['BASIC']['embedding_vector_dir'])

    # f = open(os.path.join(config['DOCUMENT']['cache_dir'], 'test.cands.tsv'), 'w', encoding="utf-8")

    # for n, canonical_walk in enumerate(walks_):
    #     predicates = list()
    #     trg = list()
    #     z = 0
    #     if len(canonical_walk) > 3:
    #         for j, walk in enumerate(canonical_walk):
    #             if 'owl2vec#' not in walk and \
    #                     'http://www.w3.org' not in walk and \
    #                       'http:' in walk and \
    #                           '=' not in walk and (z == 0 or z == 1 ):
    #                           trg.append(walk)
    #                           z += 1

    #             elif 'owl2vec#' not in walk and \
    #                     'http://www.w3.org' not in walk and \
    #                       'http:' in walk and \
    #                           '=' not in walk and (z == 2 ):
    #                           predicates.append(walk)

    #         if z == 2 and len(predicates) > 0 :
    #           predicates_tpl= tuple(predicates)
    #           ax = "\t".join(trg)
    #           f.write('%s' % ax)
    #           f.write(f"\t{predicates_tpl}\n")
    #     else:
    #         continue            
    # f.close()

    print('Time for learning the embedding model: %s seconds' % (time.time() - start_time))
    print('Model saved. Done!')