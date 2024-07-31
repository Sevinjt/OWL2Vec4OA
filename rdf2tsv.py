reader = open(r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\AML_alignment_sn2fbody.rdf', "r+")
tsv = open(r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\AML_alignment_sn2fbody.tsv', 'w')
lines = reader.readlines()
for line in lines:
    if line.strip().startswith('<entity1 '):
        quotInd1 = line.index("=")
        quotInd2 = line.index(">",quotInd1+1)
        subject=str(line[quotInd1+2: quotInd2-2])
        tsv.write(f"{subject}\t")
        continue
    if line.strip().startswith('<entity2 '):
        quotInd1 = line.index("=")
        quotInd2 = line.index(">",quotInd1+1)
        object=str(line[quotInd1+2: quotInd2-2])
        tsv.write(f"{object}\t")
        continue
    if line.strip().startswith('<measure '):
        quotInd1 = line.index(">")
        quotInd2 = line.index("<",quotInd1+1)
        confidence_value=float(line[quotInd1+1: quotInd2])
        tsv.write(f"{confidence_value}\n")