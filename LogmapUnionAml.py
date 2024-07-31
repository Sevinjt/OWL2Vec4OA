def read_file(file_path):
    entities = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('\t')
                entity1, entity2, value = parts[0], parts[1], float(parts[2])
                entities[(entity1, entity2)] = value
    return entities

def write_union_file(output_path, union_entities):
    with open(output_path, 'w') as output_file:
        for (entity1, entity2), value in union_entities.items():
            output_file.write(f'{entity1}\t{entity2}\t{value:.4f}\n')

def main():
    file1_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\AML_alignment_sn2fbody.tsv'
    file2_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\logmap_sn2fbody.tsv'
    output_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\U_sn2fmb.tsv'

    entities1 = read_file(file1_path)
    entities2 = read_file(file2_path)

    union_entities = {**entities1, **entities2}

    write_union_file(output_path, union_entities)

main()
