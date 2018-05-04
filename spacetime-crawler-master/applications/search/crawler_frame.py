import logging
from datamodel.search.DelehoybMshoshanUfperez_datamodel import DelehoybMshoshanUfperezLink, OneDelehoybMshoshanUfperezUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"

@Producer(DelehoybMshoshanUfperezLink)
@GetterSetter(OneDelehoybMshoshanUfperezUnProcessedLink)
class CrawlerFrame(IApplication):
    app_id = "DelehoybMshoshanUfperez"

    def __init__(self, frame):
        self.app_id = "DelehoybMshoshanUfperez"
        self.frame = frame


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneDelehoybMshoshanUfperezUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = DelehoybMshoshanUfperezLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneDelehoybMshoshanUfperezUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(DelehoybMshoshanUfperezLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
    
def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''
    print("***********URL:           ", rawDataObj.url)             # self explanatory i hope
    #print("***********CONTENT:       ", rawDataObj.content)         # ALL the html source of the page.  parse this for links.
    print("***********ERROR MSG:     ", rawDataObj.error_message)   # "not found", etc.
    print("***********HEADERS:       ", rawDataObj.headers)         # part of the handshake
    print("***********HTTP CODE:     ", rawDataObj.http_code)       # the 3 digit http code (like 404, etc.)
    print("***********IS REDIRECTED: ", rawDataObj.is_redirected)   # how to tell is this is a trap!
    print("***********FINAL URL:     ", rawDataObj.final_url)       # i think this only gets a value if this URL redirects you somewhere
    
    # add all the URL -STRINGS- to outputLinks 
    links = html.iterlinks(rawDataObj.content)  # returns a list of ALL links, even to things like stylesheets and image assets 
    #links = html.find_rel_links(rawDataObj.content, 'href')
     
    for link in links:
        url = link[2]
        if len(url) == 1 or url[0] == "#" or url[0:6] == "mailto":
            continue
        if url[0:4] != "http" and url[0:4] != "www.":
            # the first 4 characters aren't "http" or "www.", so url is a relative path (starts with "/" or "." or "..")
            # construct the full path:
            print "Relative path found: ", url
            pass
        outputLinks.append(url)
        print "*****WOW***** (added to outputLinks) ", url
 
    #print "\n\n*****WOW*****", outputLinks 
    #print "\n\n" 
    
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        # might want to use link.download() to check for crawler traps? ( i don't think so actually ) 
        # ganglia example: https://ganglia.ics.uci.edu/?r=4hr&cs=&ce=&m=load_one&tab=m&vn=&hide-hf=false 
        #                                              ^ we don't care about anything past this question mark, i don't think    

    except TypeError:
        print ("TypeError for ", parsed)
        return False
