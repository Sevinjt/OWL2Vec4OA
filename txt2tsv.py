reader = open(r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\alignment2022\logmap_outputlogmap_overestimation.txt', "r+")
tsv = open(r'C:\Users\sev_s\Documents\OWL2Vec-Star\case_studies\Data\alignment2022\omim2ordo_overestimation.tsv', 'w')
lines = reader.readlines()
for line in lines:
    dat=line.split("|")
    
    subject = (str(dat[0]))
    object = (str(dat[1]))
    confidence_value =float(dat[3])

    tsv.write(f"{subject}\t{object}\t{confidence_value}\n")