import json
import pymongo
from pymongo import MongoClient
import re
from bs4 import BeautifulSoup

###############
### GLOBALS ###
###############
MAX_ENTRIES = 100    # 36926 for ALL the documents
FOLDERMAX = 74
FILEMAX = 499

BK_PATH = './WEBPAGES_RAW/bookkeeping.json'
with open(BK_PATH) as f:
    PAGES = json.load(f)

CORPUS = dict()
### CORPUS format:
#
# Before pruning:
#   token : [docid, docid, ...]
#   Where docid is repeated however many times that token appeared in that document.
#
# After pruning:
#   token : [(docid, freq), (docid, freq), ...]
#   Where each tuple (docid, freq) has a unique docid associated with however many times that token appeared in that document.

########################
### HELPER FUNCTIONS ###
########################
def get_ids():
    """Generate docids as strings.  Does not actually open any files."""
    result = []
    counter = 0     # accounts for only collecting up to MAX_ENTRIES documents
    for folder in range(FOLDERMAX+1):
        for file in range(FILEMAX+1):
            counter += 1
            if counter <= MAX_ENTRIES:
                one_id = str(folder) + '/' + str(file)
                result.append(one_id)
    return result

def get_doc_strings(s):
    """Returns the text from a web page.  s is a BeautifulSoup object."""
    #return [repr(string) for string in s.stripped_strings]
    return s.get_text(strip=True).encode("utf-8")

def get_url_from_docid(docid):
    return PAGES[docid]

def prune_tokens(t):
    """Modifies t (a list of tokens) to include alphanumeric chars, '-', '.', and '/' """
    x = []    
    for i in t:
        # regex to only allow: alphanumeric chars, "-", ".", and "/"
        temp = re.sub('[^\da-zA-Z/-]+', ' ', i)
        x.extend(temp.split())
    #print x
    return x


#####################################
### CORPUS MODIFICATION FUNCTIONS ###
#####################################
def add_to_corpus(t_list, docid):
    """Adds the tokens in t_list to the global CORPUS."""
    for t in t_list:
        tl = t.lower()  # remove ambiguity in case
        if tl not in CORPUS.keys():
            CORPUS[tl] = [docid]
        else:
            CORPUS[tl].append(docid)

def compress_docids(doc_list):
    """Compresses a single docid list to include frequencies"""
    result = []
    temp = set(doc_list)
    for doc in temp:
        result.append((doc, doc_list.count(doc)))
    return result

def prune_corpus():
    """Modifies all tokens in the corpus to include token frequencies and (hopefully) reduce memory size"""
    for t in CORPUS:
        temp = CORPUS[t]
        CORPUS[t] = compress_docids(temp)

def send_to_mongo():
    """Goes through the CORPUS one-by-one and adds each token+docid+freq to a local MongoDB database."""
    print "About to connect to a local MongoDB database."
    raw_input("Press Enter once you have started the MongoDB server.... ")
    client = MongoClient()
    print "Successfully connected.  Fetching database \"CS121PROJ.tokens\"...."
    db = client.CS121PROJ
    collection = db.tokens
    print "Successfully connected to CS121PROJ.tokens.  Transferring corpus to the database...."

    num_inserted = 0
    one_doc = {"dummy": "dummy"}
    for token,docids in CORPUS.iteritems():
        one_doc = {token: docids}
        insert_result = collection.insert_one(one_doc)
        #print "Inserted " + token
        num_inserted += 1
    print "Done!  IDs inserted: ", num_inserted
    print "There are now " + str(collection.count()) + " tokens in the database."


##############################
### PROGRAM FLOW FUNCTIONS ###
##############################
def process_document(docid):
    """Iterate through the text of the document of docid and adds it to the global CORPUS."""
    print "***** Tokenizing document ID: {}".format(docid)                              # DEBUG
    print "***** URL: " + get_url_from_docid(docid) + "\n"                          # DEBUG
    webpage_file = open("./WEBPAGES_RAW/" + docid)     # the HTML code of that document
    soup = BeautifulSoup(webpage_file, 'html.parser')

    #print "***** START PAGE TEXT *****"                                             # DEBUG
    big_string = get_doc_strings(soup)
    tokens = big_string.split()
    tokens = prune_tokens(tokens)
    #print tokens                                                                    # DEBUG
    add_to_corpus(tokens, docid)
    #print "***** END OF PAGE TEXT *****\n\n"                                        # DEBUG

    webpage_file.close()

def main():
    print "Starting to build indices:"
    all_ids = get_ids()
    for docid in all_ids:
        try:
            process_document(docid)
        except KeyError:
            print "File does not exist: ID =", docid
    prune_corpus()
    # Sample corpus queries (these have nothing to do with MongoDB, use the console for that):
    #print CORPUS["informatics"]
    #print CORPUS["ics"]
    send_to_mongo()     # idea: send to Mongo after each document, not at the end.
                        # this would imply having a separate corpus to each document
                        # and we'd also have to not only insert documents into MongoDB, but UPDATE documents as well

    

if __name__ == "__main__":
    main()
