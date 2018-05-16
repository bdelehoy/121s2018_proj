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
    return s.get_text(strip=True)


def get_url_from_docid(docid):
    return PAGES[docid]


def process_document(docid):
    print "***** Tokenizing document {}: {}".format(docid, PAGES[docid])            # DEBUG
    print "***** URL: " + get_url_from_docid(docid) + "\n"                          # DEBUG
    webpage_file = open("./WEBPAGES_RAW/" + docid)     # the HTML code of that document
    soup = BeautifulSoup(webpage_file, 'html.parser')

    print "***** START PAGE TEXT *****"                                             # DEBUG
    strings = get_doc_strings(soup)
    print strings                                                                   # DEBUG
    # add each token to a dict and write that to a json file here, i think
    print "***** END OF PAGE TEXT *****\n\n"                                        # DEBUG

    webpage_file.close()


def main():
    print "Starting to build indices:"
    all_ids = get_ids()
    for docid in all_ids:
        try:
            process_document(docid)

        except KeyError:
            print "File does not exist at", docid

if __name__ == "__main__":
    main()
