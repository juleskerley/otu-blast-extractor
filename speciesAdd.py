# Goal is to get the mussels that are in blastn_Pfa1.tsv
#  appended onto the Pfa-otu_table.tsv.
# If the species (column 1) exists in Pfa-out_table (column 1),
#  then it needs every muscle (column 18 & 22) appended onto
#  the row of the particular species .
# It is okay to append 18 and 22 each time. The redundancy is acceptable.
# blastn_Pfa1.tsv is the "longer" file that verbosely has every
#  species (some of which are not in Pfa-otu_table.tsv),
#  so an exhaustive search on it should get everything.

# NOTE: This script assumes that the blast and otu file are in the same
#       directory as it. If it is not, then you can either move the script or
#       change the names of blastFile and otuFile to fit the file location

import pandas as pd

def main():
    # File to extract from without file extension
    blastFile = "blastn_Pfa1"
    # File to extract into without file extension
    otuFile = "Pfa-otu_table"
    
    # Opening the blast file
    blastn_pfa1 =  pd.read_table(blastFile+".tsv",delimiter='\t',
                                 header=None)
    # Merging column 0 and 1; surely there is a better way?
    # Stack Overflow gave me this and I'm certain there is a pandas way...
    blastn_pfa1[0] = blastn_pfa1[0] + '-' + blastn_pfa1[1]
    # Removing the Redundant column 1 (might not be needed)
    blastn_pfa1.drop(labels=1,axis=1,inplace=True)

    # Renaming several columns for future table referencing
    # Chnage column number if these are placed differently
    blastn_pfa1.rename(columns={0 : 'genome-publicdb'},inplace=True)
    blastn_pfa1.rename(columns={17 : 'taxonomic-name'},inplace=True)
    blastn_pfa1.rename(columns={18 : 'common-name'},inplace=True)
    blastn_pfa1.rename(columns={19 : 'description'},inplace=True)
    blastn_pfa1.set_index('genome-publicdb',inplace=True)
    
    # Taking the header out first to do some work to make it better
    with open(otuFile+".tsv") as f:
        # Create a string with all the modifications needed to properly become
        # the labels for the dataframe
        fields = f.readline().strip().split('\t')
    # Adding the index label to the front
    fields =  ['genome'] + fields
    # Pulling the whole file, skipping the header line in the file
    pfa_otu_table = pd.read_table(otuFile+".tsv",
                                  delimiter='\t',header=None,
                                  skiprows=1,names=fields)
    # Setting the genome to be the index of the table
    pfa_otu_table.set_index('genome',inplace=True)

    # List for appending
    newColumnData = []

    # For each item in genome column of Pfa, get all instances of genome in
    # blastn and insert "taxonomic-name" and "description" onto the particular
    # item. 
    for candidate in pfa_otu_table.index:
        # Filtering the blast file for the candidate genome
        # This is possibly empty but that is okay
        filtered_result = blastn_pfa1.filter(regex="^{0}".format(candidate),
                                             axis=0)
        # Removing the duplicate entries 
        filtered_result = filtered_result[[
            'taxonomic-name','description'
            ]].drop_duplicates(subset='taxonomic-name')
        # Creating the list from a filtered search of a particular genome
        extractedList = filtered_result[[
            'taxonomic-name','description']].values.flatten().tolist()
        
        # Debug output
        print(candidate, extractedList)
        
        # Joining the list with commas for the convenience of using Excel
        # Also, this converts it into a string
        extractedString = ','.join(extractedList)
        #Adding the string to a list
        newColumnData.append(extractedString)
    
    # Adding extracted data to otu table
    pfa_otu_table['extracted'] = newColumnData
    
    # Creating the .tsv to make use of the results.
    pfa_otu_table.to_csv(path_or_buf="{0}-extracted.tsv".format(otuFile),
                         sep='\t')
    
    return

if __name__ == "__main__":
    main()