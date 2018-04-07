import sys
import csv
import os
import json
import subprocess
from data import Data
import PCcrawler as crawler
from retriever import retrieve

#write the evaluation results to file
def write_to_file(queryNo, scores, filename, amount=10):
    open_mode = 'a' if os.path.exists(filename) else 'w'
    
    with open(filename, open_mode) as csvfile:
        wr = csv.writer(csvfile, delimiter=',')
        docids = []
        if (open_mode == 'w'):
            wr.writerow(["StudentNo", 100134028])
            wr.writerow(["System", "relfbk"])
            wr.writerow(["QueryNo", "Rank", "URL"])

        with open('index_files/docids.txt','r') as file:
            docids = eval(file.read())
            i = 0
            for k in sorted(scores, key=scores.get, reverse=True)[:amount]:
                i += 1
                wr.writerow([queryNo, i, docids[k]])

def open_files(): #add files to cache
    cache = Data()
    try:
        with open('index_files/docids.txt','r') as file:
            docids = eval(file.read())
            cache.doc_ids = docids
        with open('index_files/doclengths.txt', 'r') as file:
            doclengths = eval(file.read())
            doclengths = {int(k):v for k, v in doclengths.items()}
            cache.doc_lengths = doclengths
        with open('index_files/postings.txt', 'r') as file:
            postings = json.load(file)
            postings = {int(k):v for k, v in postings.items()}
            cache.postings = postings
        with open('index_files/vocab.txt', 'r') as file:
            vocab = eval(file.read())
            cache.vocab = vocab
        with open('index_files/doc_parts/titles.txt', 'r') as file:
            titles = eval(file.read())
            cache.titles = titles
        with open('index_files/doc_parts/headings.txt', 'r') as file:
            headings = eval(file.read())
            cache.headings = headings
        with open('index_files/doc_parts/descriptions.txt', 'r') as file:
            descriptions = eval(file.read())
            cache.descriptions = descriptions
        with open('index_files/doc_parts/summaries.txt', 'r') as file:
            summaries = eval(file.read())
            cache.summaries = summaries
        return cache
    except Exception as e:
        print("Try indexing again.")
        print("ERROR", e)

def main():
    
    command = sys.argv.pop(1)
    if (command == "-index"):
        crawler.start(sys.argv)
    elif (command == "-initialise"):
        subprocess.check_call(["python", "cache.py"])
        os.system("./cache.py")
    else:
        print("type engine.py -index to crawl or engine.py -initialise to start the engine")

if __name__=="__main__":
    main()