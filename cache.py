import sys
import engine
from retriever import retrieve
from data import Data
cache = None

def analyse_input(line):
    line = line.split(' ', 1)
    if (len(line) == 1):
        return 
    mode = line[0].strip("\n") #find the mode of process to be executed
    query = line[1].strip("\n") #and queries to be executed on
    query_terms = []
    queries = []

     
    if(query.find(".txt") != -1): #if it's a text file split each line to find the queries
        try:
            queries = [q.split() for q in open(query)]
        except Exception as e:
            print("File doesn't exist")
            print("Error", e)
    else:
        query_terms = query.split()#if not a text file just split the query


    if (mode == "search"): #if mode is search
        if queries:
            for query in queries:
                retrieve(query, data=cache)#call the retrieving mechanism
        else:
            retrieve(query_terms, data=cache)
    elif(mode == "evaluate"):#if the mode is for evaluation
        queryNo = 0
        for query in queries: #read the queries
            queryNo += 1
            # get ranked URLs
            scores = retrieve(query, data=cache, should_print=False)
            engine.write_to_file(queryNo, scores, "csv/relfbk1.csv", amount=10)

if __name__=="__main__":
    while True:
        if not cache: #checks if the files are not cached
            cache = engine.open_files()
        
        print("type search query_terms/query_file or evaluate query_file:")
        line = sys.stdin.readline() #read the input
        line.strip("\n")
            
        analyse_input(line)
        