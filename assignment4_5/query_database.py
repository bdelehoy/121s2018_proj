from __future__ import division
import json
import pymongo
from pymongo import MongoClient

BK_PATH = './WEBPAGES_RAW/bookkeeping.json'
with open(BK_PATH) as f:
    PAGES = json.load(f)


def print_out_urls(docid_list, query):
    # TODO: Make this nicer
    print "Found", len(docid_list), "result(s) for " + " ".join(query)+":"
    for docid in docid_list:
        print docid, " | ", PAGES[docid]
    return


def get_union_of_results(all_results):
    """all_results is [[(docid, freq), ... ], [(docid, freq), ... ], [(docid, freq), ... ]]
    This function returns a list of docids that each element in the list has.
    """
    common = set()  # DUMMY VALUE, make this initialize to empty list
    returnable=[]
    if(len(all_results)==1):
        for i in all_results[0]:
            returnable.append(i[0])
        return returnable
    else:
        for first in range(len(all_results)):
            for second in range(len(all_results)):
                if first!=second:
                    for i in all_results[first]:
                        for x in all_results[second]:
                            if x[0]==i[0]:
                                common.add(i[0])
        return common
                

            






    # TODO
    # if "computer" appeared in 715 pages and "science" appeared in 497 pages, this function should return
    # only the docids of pages that contain both "computer" and "science"

    # this should also work on single and 3+ word queries!!!!!!!!!!!!!!!!!
    # we will lose information regarding token frequency but that's ok for now
    return common_elements


def get_results(tokens, query_list):
    """Obtains the results for the given search query."""
    print "Searching for: " + " ".join(query_list)

    # query_list is (possibly) a multiword query: ["informatics"], ["computer", "science"]
    # we will iterate through each search term individually, add their results to a list, and only return the common elements
    # "common elements" meaning common docids.  information about count may be lost.
    all_results = []    # this a list of results
    for q in query_list:
        document =  tokens.find_one( {q : {"$exists" : True}} )
        # ^that returns a dictionary that represents the item in the database: {"q" : [(docid, freq), ... ], "_id" : #########}
        # so we have to index it one more time by "q" to get what we want
        results = document[q]       # this is a list of (docid, freq)
        all_results.append(results)
        print "\tFound", len(results), "results for", q   # DEBUG!  Comment me out when you're done

    # at this point, all_results is a list of lists of (docid, freq)
    # find union of docs here
    golden_docids = get_union_of_results(all_results)

    print_out_urls(golden_docids, query_list)
    


def user_prompt():
    print "\nWelcome to the ICS search system.  Connecting to the local database...."
    
    client = MongoClient()
    print "Successfully connected.  Fetching database \"CS121PROJ.tokens\"...."
    db = client.CS121PROJ
    collection = db.tokens
    print "Size of database on disk:", db.command("dbstats")["dataSize"] / 1000, "KB"       # 1000b to 1kb
    
    print "\nReady.  Please enter your search query below, with each word separated by a space.  Use CTRL-C to exit."
    # test this AT LEAST with:
    # uci
    # informatics
    # computer science
    # artificial intelligence
    # uci computer science
    while True:
        query_list = raw_input(">>> ").split()
        #print(query_list)
        get_results(collection, query_list)


def main():
    user_prompt()
    return

if __name__ == "__main__":
    main()
