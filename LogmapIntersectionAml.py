def read_file(file_path):
    entities = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('\t')
                entity1, entity2, value = str(parts[0]), str(parts[1]), float(parts[2])
                entities[(entity1, entity2)] = value
    return entities

def write_intersection_file(output_path, intersection_entities):
    with open(output_path, 'w') as output_file:
        for (entity1, entity2), value in intersection_entities.items():
            output_file.write(f'{entity1}\t{entity2}\t{value:.4f}\n')

def find_intersection(entities1, entities2):
    intersection_entities = {key: entities1[key] for key in entities1 if key in entities2}
    return intersection_entities

def main():
    file1_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\omim2ordo_aml.tsv'
    file2_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\omim2ordo_logmap.tsv'
    output_path = r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\omim2ordo_Int.tsv'

    entities1 = read_file(file1_path)
    entities2 = read_file(file2_path)

    intersection_entities = find_intersection(entities1, entities2)

    write_intersection_file(output_path, intersection_entities)


main()
