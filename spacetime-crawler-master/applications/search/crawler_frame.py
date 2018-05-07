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
        self.outgoing=0
        self.best_url=""
        self.subs={}


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneDelehoybMshoshanUfperezUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = DelehoybMshoshanUfperezLink("wics.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneDelehoybMshoshanUfperezUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        f = open('analytics.txt', 'w')
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            if len(links) >self.outgoing:
                self.outgoing=len(links)
                self.best_url= downloaded.url
            mainUrl=urlparse(downloaded.url)
            
            if mainUrl.netloc not in self.subs.keys()and mainUrl.path not in self.subs.keys():
                
                print mainUrl
                if mainUrl.scheme=="" and mainUrl.netloc=="":
                    self.subs[mainUrl.path]=set()
                else:
                    self.subs["://"+mainUrl.netloc]=set()
                    

            for l in links:
                if is_valid(l):
                    linkUrl=urlparse(l)
                    if (mainUrl.netloc) == (linkUrl.netloc):
                        if mainUrl.netloc!="":
                            self.subs["://"+mainUrl.netloc].add(linkUrl.path)
                        else:
                            self.subs[mainUrl.path].add(linkUrl.path)
                    self.frame.add(DelehoybMshoshanUfperezLink(l))
            analytics=""
            analytics+="1. subdomains : processed urls : \n"
            for i in self.subs:
                analytics+=i +" : "+str(len(self.subs[i])) +"\n"
            analytics+="\n2. url with most outgoing links: \n"+self.best_url+" : "+str(self.outgoing)
            f.write(analytics)
            f.close()

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
    print "\t***********URL:           ", rawDataObj.url             # self explanatory i hope
    #print "\t***********CONTENT:       ", rawDataObj.content         # ALL the html source of the page.  parse this for links.
    print "\t***********ERROR MSG:     ", rawDataObj.error_message   # "not found", etc.
    print "\t***********HEADERS:       ", rawDataObj.headers         # part of the handshake
    print "\t***********HTTP CODE:     ", rawDataObj.http_code       # the 3 digit http code (like 404, etc.)
    print "\t***********IS REDIRECTED: ", rawDataObj.is_redirected   # how to tell is this is a trap!
    print "\t***********FINAL URL:     ", rawDataObj.final_url       # i think this only gets a value if this URL redirects you somewhere

    if not rawDataObj.http_code >=400 and rawDataObj.http_code <=599 and rawDataObj.error_message == None:
        doc = html.fromstring(rawDataObj.content)
        doc.make_links_absolute(rawDataObj.url)
        links = html.iterlinks(doc)  # returns a list of ALL links, even to things like stylesheets and image assets

        for link in links:
            url = link[2]
            # if the URL is 1 character long or less...
            # if the first character of the URL is a "#"...
            # or if the first 6 characters start with "mailto:"
            # then skip this URL, don't add it to the frontier
            if len(url) <= 1 or \
               url[0] == "#" or \
               (len(url)>=6 and url[0:6] == "mailto"):
                continue
            outputLinks.append(url)
    #        print "\t*****WOW***** (added to outputLinks) ", url

    #print "\n\n\t*****WOW*****", outputLinks
    #print "\n\n"

    return outputLinks

def not_a_trap(parsed, url):
    complete_queries = parse_qs(parsed.query)    # queries is a dictionary of {query:value}
    # if there are no queries, then let it pass
    if len(complete_queries) == 0:
        return True

    query_strings = [q for q in complete_queries.keys()]
    # append "=" to the end of every query
    for i in range(len(query_strings)):
        query_strings[i] += "="

    # check if queries are "date" or end in a specific token (if they do, then this url is a trap)
    for q in query_strings:
        q = q.lower()
        if q == "date=" \
        or "_id=" in q or "-id=" in q \
        or "_token=" in q or "-token=" in q \
        or "_key=" in q or "-key=" in q:
            # all queries are guaranteed to end in "="
            print "\t\tThrew a URL away due to date, id, key, or token in queries:", url
            return False

    directories = parsed.path.split('/')
    # quick n dirty way to remove empty strings from urls like: "/dir1/dir2/dir3/"
    # (that start and end with a "/", then there will be 2 empty strings in directory, which we don't want)
    for i in range(directories.count("")):
        directories.remove("")

    # check for long paths in the url of an arbitrarily long path
    arbitrary_long_path_length = 13
    if len(directories) >= arbitrary_long_path_length:
        print "\t\tThrew a URL away due to too many directories:", url
        return False

    # check for repeating directories:
    directories_set = set(directories)
    if len(directories) != len(directories_set):
        print "\t\tThrew a URL away due to duplicate directories:", url
        return False
    return True

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''
    parsed = urlparse(url)
    #print "\t\tParsed: ", parsed
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        # if the url is absolute...
        # and it isn't a crawler trap....
        # and ".ics.uci.edu" is in the hostname....
        # and it doesn't match that regular expression....
        # then this is a valid URL.
        return bool(urlparse(url).netloc) \
            and not_a_trap(parsed, url) \
            and ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False
