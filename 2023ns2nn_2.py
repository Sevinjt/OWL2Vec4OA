#!/usr/bin/env python
# coding: utf-8

# # Owl2vec_star_ext
# In this process, we get ontology files and to change it to embedding model

# In[ ]:


import owl2vec4mappings

# Parameters:
# ontology_file1
# ontology_file2
# mapping_file
# config_file
# uri_doc
# lit_doc
# mix_doc
# but there are some parameters you can change in config file
gensim_model = owl2vec4mappings.extract_owl2vec_model(ontology_file1 = "./case_studies/Data/snomed.neoplas.owl",
                                                ontology_file2 = './case_studies/Data/ncit.neoplas.owl',
                                                mapping_file = './case_studies/Data/trainUnion_S2NN.tsv',
                                                config_file = "./2023ns2nn_2.cfg",
                                                uri_doc = True, lit_doc = True, mix_doc = True)


# In[ ]:


# Run
import configparser
config = configparser.ConfigParser()
config.read("2023ns2nn_2.cfg")
output_folder=config['DOCUMENT']['cache_dir']


# In[ ]:


#Gensim format
#Run
gensim_model.save(output_folder+"ontology"+'_'+config['DOCUMENT']['walk_depth']+".embeddings")


# In[ ]:


#Txt format
#Run
gensim_model.wv.save_word2vec_format(output_folder+"ontology"+'_'+config['DOCUMENT']['walk_depth']+".embeddings.txt", binary=False)


# ## Loading embeddings and getting similarities

# In[ ]:


# Run
from gensim.models import Word2Vec
model = Word2Vec.load(output_folder+"ontology"+'_'+config['DOCUMENT']['walk_depth']+".embeddings")


# In[ ]:


# Run
ranking_results = []
# save the scored candidate mappings in the same format as the original test.cands.tsv
f = open(output_folder+"scored.test.cands"+'_'+config['DOCUMENT']['walk_depth']+".tsv", "w")
f.write("SrcEntity" +'\t'+ "TgtEntity" +'\t'+ "TgtCandidates\n")
file = open(r"/users/sbrt072/myfolder/OWL2Vec-Star/case_studies/Data/s2nn2023_test.cands.tsv")

for i in file.readlines()[1:]:
    src_ref_class = i.split('\t')[0]
    tgt_ref_class = i.split('\t')[1]
    tgt_cands = i.split('\t')[2]
    # print(src_ref_class, tgt_ref_class, tgt_cands)
    tgt_cands = eval(tgt_cands)  # transform string into list or sequence
    scored_cands = []
    for tgt_cand in tgt_cands:
        # assign a score to each candidate with an OM system
        try:
            matching_score = model.wv.similarity(src_ref_class, tgt_cand)
        except:
            matching_score = 0
        scored_cands.append([tgt_cand, matching_score])
    ranking_results.append([src_ref_class, tgt_ref_class, scored_cands])
    f.write(f'{src_ref_class}\t{tgt_ref_class}\t{scored_cands}\n')
print("done")


# In[ ]:


# Run
import numpy as np
distance_results = []
# save the scored candidate mappings in the same format as the original test.cands.tsv
f = open(output_folder+"distance.test.cands"+'_'+config['DOCUMENT']['walk_depth']+".tsv", "w")
f.write("SrcEntity" +'\t'+ "TgtEntity" +'\t'+ "TgtCandidates\n")
file = open(r"/users/sbrt072/myfolder/OWL2Vec-Star/case_studies/Data/s2nn2023_test.cands.tsv")


for i in file.readlines()[1:]:
    src_ref_class = i.split('\t')[0]
    tgt_ref_class = i.split('\t')[1]
    tgt_cands = i.split('\t')[2]
    # print(src_ref_class, tgt_ref_class, tgt_cands)
    tgt_cands = eval(tgt_cands)  # transform string into list or sequence
    scored_cands = []
    for tgt_cand in tgt_cands:
        # assign a score to each candidate with an OM system
        try:
            euc_dist = np.linalg.norm(model.wv[src_ref_class] - model.wv[tgt_cand])
        except:
            euc_dist = np.inf
        scored_cands.append([tgt_cand, euc_dist])
    distance_results.append([src_ref_class, tgt_ref_class, scored_cands])
    f.write(f'{src_ref_class}\t{tgt_ref_class}\t{scored_cands}\n')
print("done")


# In[ ]:





# In[ ]:




