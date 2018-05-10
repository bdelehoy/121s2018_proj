# game plan:
# tokenize just the first 20-50 for testing purposes
# use MongoDB to insert the inverted indices (tokens and docIDs) into a database

# we're gonna have to have someone run this overnight so we can get all the tokens in the database
# i (brandon) can do that on my desktop at home (ryzen 5 1600) at some point

MAX_ENTRIES = 30

def main():
    print "Starting to build indices:"
    for i in range(MAX_ENTRIES):
        print "whee", i

if __name__ == "__main__":
    main()