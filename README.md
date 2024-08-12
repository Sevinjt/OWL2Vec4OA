# OWL2Vec4OA

OWL2Vec4OA by Sevinj Teymurova

## **OWL2Vec4OA: Tailoring Knowledge Graph Embeddings for Ontology Alignment**


### Features
--------

OWL2Vec4OA is an extension of the ontology embedding system [OWL2Vec*](https://github.com/KRR-Oxford/OWL2Vec-Star/) which exposes a CLI with two subcommands after installation, which allows you to perform two main programs.
You can also run the two original python programs without installation (see the requirements in `setup.py <https://github.com/KRR-Oxford/OWL2Vec-Star/blob/master/setup.py>`__).

Installation command::
```
    $ make install
```
### Standalone
------------
This command will embed two ontologies and their corresponding mappings. It can be configured by the configuration file default1.cfg.
See the examples and comments in default1.cfg for the usage.


### Running program::
------------

#### Option 1

1. Install Python 3: https://python.org/downloads
2. Install setuptools: https://pypi.org/project/setuptools
3. Run this command in the terminal: 
```
    $ python setup.py install
```

4. Run this command in the terminal:
```
    $ python OWL2Vec_Standalone1.py --config_file default1.cfg
```

#### Option 2

1. Install Python 3: https://python.org/downloads
2. Install pip: https://pip.pypa.io/en/stable/installation
3. Install library dependicies in requirements: pip install -r requirements_owl2vec.txt
4. Run jupyter notebook: 
``` 
    jupyter_notebook_owl2vec4oa.ipynb 
```
Note: Different from the experimental codes, the standalone command has implemented all OWL ontology
relevant procedures in python with Owlready, but it also allows the user to use pre-calculated
annotations/axioms/entities/projection to generate the corpus.

**Parameters to change when running the code with help of configuration file**
1. ontology_file1 
2. ontology_file2 
3. mapping
4. confidence_threshold
5. seed_entities_on_mapping
6. cache_dir
7. walk_depth

### Implementations 

-------
Code under: 
1. `OWL2Vec_Standalone1.py` and `owl2vec4mappings.py` implements merging two ontologies into one single projection RDF graph, axiom/annotations/seed entities documents generation and model training. Note, the code `owl2vec4mappings.py` is used to compile `jupyter_notebook_owl2vec4oa.ipynb`
2. `owl2vec_star/rdf2vec/graph.py` implements creating the Knowledge Graph
3. `owl2vec_star/lib/RDF2Vec_Embed.py` implements reading projection RDF graph, adding mapping entities and their confidence values into the Knowledge Graph(kg) to be able to extract walks for model training. 
4. `owl2vec_star/rdf2vec/walkers/mapping4vec.py`  implements bias sampling walking strategy over RDF graphs 
5. `LogmapIntersectionAml.py` - implements Intersection of mappings produced by LogMap and AML
6. `LogmapUnionAml.py` - implements Union of mappings produced by LogMap and AML
7. `rdf2tsv.py`- RDF to TSV
8. `txt2tsv.py` - TXT to TSV
9. `2023ns2nn_2.py` To run the code on HPC, using SNOMED2NCIT.NEOPLAS data with the configuration file `2023ns2nn_2.cfg. 
(version 0.0.1, last access: 07/2024) with revision.


### Publications
------------

- Sevinj Teymurova, Ernesto Jimenez-Ruiz, Tillman Weyde, Jiaoyan Chen. OWL2Vec4OA: Tailoring Knowledge Graph Embeddings for Ontology Alignment. Submitted to a conference: [PDF long version]() [PDF short version](). 

- Jiaoyan Chen, Pan Hu, Ernesto Jimenez-Ruiz, Ole Magnus Holter, Denvar Antonyrajah, and Ian Horrocks. **OWL2Vec*: Embedding of OWL ontologies**. Machine Learning, Springer, 2021. [PDF](https://arxiv.org/abs/2009.14654) [Springer](https://rdcu.be/cmIMh) [Collection](https://link.springer.com/journal/10994/topicalCollection/AC_f13088dda1f43d317c5acbfdf9439a31) [Codes in package](https://github.com/KRR-Oxford/OWL2Vec-Star/releases/tag/OWL2Vec-Star-ML-2021-Journal) or [folder](https://github.com/KRR-Oxford/OWL2Vec-Star/tree/master/case_studies)



### Case Studies
------------
Data and codes for class membership prediction on [NCIT](https://zenodo.org/records/8193375), [DOID](https://zenodo.org/records/8193375), [SNOMED](https://zenodo.org/records/8193375), [NEOPLAS](https://zenodo.org/records/8193375), [PHARMA](https://zenodo.org/records/8193375), [OMIM](https://zenodo.org/records/8193375), [ORDO](https://zenodo.org/records/8193375) ontologies and their corresponding mappings are under the folder `case_studies/Data`.


### Results 
------

You can find the computed embeddings in our [zenodo](https://doi.org/10.5281/zenodo.13217802) repository 
