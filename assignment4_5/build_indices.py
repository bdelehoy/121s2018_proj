# game plan:
# tokenize just the first few for testing purposes
# use MongoDB to insert the inverted indices (tokens and docIDs) into a database

# we're gonna have to have someone run this overnight so we can get all the tokens in the database
# i (brandon) can do that on my desktop at home (ryzen 5 1600) at some point

import json
import pymongo
from bs4 import BeautifulSoup

MAX_ENTRIES = 10
FOLDERMAX = 74
FILEMAX = 499

BK_PATH = './WEBPAGES_RAW/bookkeeping.json'
with open(BK_PATH) as f:
    PAGES = json.load(f)

def get_ids():
    result = []
    counter = 0
    for folder in range(FOLDERMAX+1):
        for file in range(FILEMAX+1):
            counter += 1
            if counter <= MAX_ENTRIES:  # accounts for only collecting up to MAX_ENTRIES documents
                one_id = str(folder) + '/' + str(file)
                result.append(one_id)
    return result

def main():
    print "Starting to build indices:"
    all_ids = get_ids()
    for docid in all_ids:
        try:
            print "Tokenizing document {}: {}\n".format(docid, PAGES[docid])
            
        except KeyError:
            print "File does not exist at", docid

if __name__ == "__main__":
    main()
