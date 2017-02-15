import itertools
from itertools import *
import pandas as pd
import urllib
import csv
import re

ASSEMBLY_DIR="assembly"

# Download both files and save as refseq_bacteria.txt and genbank_bacteria.txt
#refseq_bacteria = urllib.urlopen("ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/bacteria/assembly_summary.txt")
#genbank_bacteria = "ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/assembly_summary.txt"
refseq_bacteria = "refseq_bacteria.txt"
genbank_bacteria = "genbank_bacteria.txt"
REORDERED_GENOMES = "reordered_assembly.txt"
METAPHLAN2_OUTPUT = "merged_species.txt"


def get_reference_genomes():
	
	print "[INFO] Reading the files into pandas dataframe" 
	#read the entire file as pandas dataframe
	df = pd.read_table(ASSEMBLY_DIR + "/" + refseq_bacteria,header=1,dtype=str)
	df2 = pd.read_table(ASSEMBLY_DIR + "/" + genbank_bacteria,header=1,dtype=str)
        print "[INFO] Merged the data frames into one pandas file"
	df= df.append(df2)
	
	#test the data frame
	#print df.head()
	#print df.columns

	#sort dataframe using dedefined order list 
	print "[INFO] Sorting the dataframe (refseq category) to get reference genome at top"
	order_list=[ 'reference genome','representative genome', 'na']
	df["refseq_category"] = df["refseq_category"].astype("category")
	df["refseq_category"] = df["refseq_category"].cat.set_categories(order_list)
	df = df.sort_values(by="refseq_category")

	print "[INFO] Saving reordered dataframe as \"reordered_assembly.txt\""
	df.to_csv(ASSEMBLY_DIR + "/" + REORDERED_GENOMES ,sep='\t')
	return df

# main
print "\n\n\n[INFO]---------------Starting program----------------------"
print "\n[INFO] Searching species names in reference genome databases"
genome_link = []
with open(METAPHLAN2_OUTPUT, 'r') as f:
	print "[INFO] Builind reference databases for searching"
	df = get_reference_genomes()
	species_status = {}
	print "[INFO] Searching species one at a time"
	for line in itertools.islice(f, 2, None):
		species_name = line.split()[0]
		# fix species name to match assembly entry
		name_tmp = species_name.replace("s__", "").replace("_"," ").replace("sp ","sp. ").replace(" unclassified","").replace(" noname","").split()
		species_name_fixed = " ".join(name_tmp[0:2]) + " " + "_".join(name_tmp[2:])
		species_name_fixed = species_name_fixed.rstrip()	
			
		print "[INFO] Searching ...", species_name, " :",
		species_status[species_name] = "Not Found"
		for index, row in islice(df.iterrows(), 1, None):
		    	if re.search(species_name_fixed,row['organism_name']):
				species_status[species_name] = row['organism_name'] + "\t" + row['ftp_path']
				print "FOUND" ," -> ", row['organism_name']," -> ", row['# assembly_accession'],
				break
		print ""

	print "\n[INFO] Removing any duplicate entries and missing entries ... "
	species_status2 = {}
	for key in species_status:
		FOUND = 'No'
		for key2 in species_status2:
			if species_status[key] == species_status2[key2]:
				FOUND = 'Yes'
		if FOUND == 'No' and species_status[key] != "Not Found":
			species_status2[key] = species_status[key]	
		

	print "[INFO] Searching finished. Now saving output in text files\n\n"

	with open('genome_for_mapping_found.list', 'w') as f:
		for key in species_status2:
				f.write(key + "\n")
				#print "[INFO]", key, species_status2[key]
		print "[INFO] The list of species found is saved as \"genome_for_mapping_found.list\"\n"
		

        with open('genome_for_mapping_nofound.list', 'w') as f:
                for key in species_status:
                        if species_status[key] == "Not Found":
                                f.write(key + "\t" + species_status[key] + "\n")
                                #print "[INFO]", species_status[key]
                print "[INFO] The list of species not found is saved as \"genome_for_mapping_nofound.list\"\n\n"
		
