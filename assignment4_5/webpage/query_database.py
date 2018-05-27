from __future__ import division
import json
import pymongo
from pymongo import MongoClient
from numpy import log10
import sys

BK_PATH = './WEBPAGES_RAW/bookkeeping.json'
with open(BK_PATH) as f:
    PAGES = json.load(f)
NUM_DOCS = 2000
DEBUG_ENABLED = False

# test this AT LEAST with:
# uci
# informatics
# computer science
# artificial intelligence
# uci computer science

# TF(term, docid): 1 + log10( how many times (term) appears in (docid) )
# DF(term): how many documents (term) appears in
#
# IDF(DF): log10(N/DF), where N = the amount of unique documents in the database/corpus (2000 for now)
# TF-IDF(TF, IDF): TF*IDF

def oprint(str):
    """A print statement that only succeeds according to a global variable."""
    if DEBUG_ENABLED:
        print(str)

########################
### TF-IDF FUNCTIONS ###
########################
def tf(freq):
    """Returns the weighted term frequency of a given count.  freq is an int obtained from a separate posting list of (docid, freq)."""
    return 1 + log10(freq)

def idf(term):
    """Returns the inverse document frequency of term.  term is a posting list of (docid, freq)."""
    return log10(NUM_DOCS / len(term))

def tfidf(tf, idf):
    """Returns the final TF-IDF score of a pair of tf/idf scores for a nonspecific term/document pair."""
    return tf*idf


def print_out_urls(docid_list, query):
    # TODO: Make this nicer
    oprint("Found "+str(len(docid_list))+" result(s) for " + " ".join(query)+":")
    count = 0
    for docid in docid_list:
        print "{}\t{}\t{}".format(count, docid, PAGES[docid])   # print so it goes to stdout regardless of DEBUG_ENABLED
        count += 1
    return


def get_union_of_results(all_results):
    """all_results is [[(docid, freq), ... ], [(docid, freq), ... ], [(docid, freq), ... ]]
    This function returns a list of the docids that all elements appear in (but loses frequency information).
    """
    common = set()  # DUMMY VALUE, make this initialize to empty list
    if len(all_results) == 1:
        return [i[0] for i in all_results[0]]
    else:
        for first in range(len(all_results)):
            for second in range(len(all_results)):
                if first != second:
                    for i in all_results[first]:
                        for x in all_results[second]:
                            if x[0] == i[0]:
                                common.add(i[0])
        return common


def get_results(tokens, query_list):
    """Obtains the results for the given search query."""
    oprint("Searching for: " + " ".join(query_list))

    # query_list is (possibly) a multiword query: ["informatics"], ["computer", "science"]
    # we will iterate through each search term individually, add their results to a list, and only return the common elements
    # "common elements" meaning common docids.  information about count may be lost.
    all_results = []
    for q in query_list:
        document =  tokens.find_one( {q : {"$exists" : True}} )
        # ^that returns a dictionary that represents the item in the database: {"q" : [(docid, freq), ... ], "_id" : #########}
        # so we have to index it one more time by "q" to get what we want
        if document == None:
            oprint("\tNo results found for "+q+" (skipping)")
            continue
        all_results.append(document[q])     # document[q] is a list of (docid, freq)
        oprint("\t(DEBUG) Found "+str(len(document[q]))+" results for "+q)

    # at this point, all_results is a list of lists of (docid, freq)
    golden_docids = get_union_of_results(all_results)
    print_out_urls(golden_docids, query_list)
    

def user_prompt():
    args = sys.argv # args[0] is the name of the file, args[1:] is the search query
    oprint("\nWelcome to the ICS search system.")
    if len(args) <= 1:
        oprint("Please provide at least 1 search term as a command line argument.  Quitting....")
    else:
        oprint("Connecting to the local database \"CS121PROJ.tokens\"....")
        try:
            client = MongoClient()
            db = client.CS121PROJ
            collection = db.tokens
            dbsize = db.command("dbstats")["dataSize"] / 1000   # 1000 bytes to 1kb
        except:
            oprint("An error occured in creating a connection to the local database.  Please start the server.")
        else:
            oprint("Successfully connected.  Size of database on disk: "+str(dbsize)+" KB\n")
            query_list = args[1:]
            get_results(collection, query_list)
    sys.stdout.flush()


def main():
    user_prompt()
    return

if __name__ == "__main__":
    main()
