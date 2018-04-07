import math
import collections
import re
import json
import string
from random import randint
from terminaltables import AsciiTable
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet

query_vector = []
docids = []
doclengths = {}
postings = {}
vocab = []
positions = {}
titles = []
headings = []
descriptions = []
summaries = []

rocchio_non_rel_docs = set()




def get_weight(docid, term):
    
    weight = 1

    title = titles[docid]
    description = descriptions[docid]
    heading = headings[docid]


    #searching for the term and if present adding weight to it
    if re.search(term, title, re.M|re.I):
        weight *= 1.5
    if re.search(term, description, re.M|re.I):
        weight *= 1.2
    if re.search(term, heading, re.M|re.I):
        weight *= 1.1

    return weight


# Retrieves answers with tf*idf weighting
def tf_idf(query_set, rocchio=False):
    global docids
    global doclengths
    global postings
    global vocab
    global positions
    global query_vector
    global rocchio_non_rel_docs

    print(rocchio_non_rel_docs)
    stemm = PorterStemmer(mode='NLTK_EXTENSIONS')
    docs = []


    idf = {}
    scores = {}
    terms_to_weight = {}
    for term in query_set:
        term = term.rstrip('?!.;:,').lower()#remove basic punctuation
        stemmed_term = stemm.stem(term)#Stem the term
        try:
            termid = vocab.index(stemmed_term)#find the term
            terms_to_weight[termid] = term
        except:
            print(term, " not found.")
            continue
        idf[termid] = (1 + math.log(len(postings.get(termid)))/len(doclengths))

    i = -1
    for termid in sorted(idf, key=idf.get, reverse=True):
        i += 1
        
        if not rocchio:
            query_vector.append(idf[termid]/len(query_set))

        for post in postings.get(termid):
            if post[0] in positions:
                positions[post[0]].append(post[2])
            else:
                positions[post[0]] = [post[2]]
             
            diff_weight = get_weight(post[0], terms_to_weight[termid])#calculate the weight to be added
            

            if post[0] not in rocchio_non_rel_docs: #add the weight into tf*idf calc
                if post[0] in scores:
                    scores[post[0]] += ((idf.get(termid) * post[1]) / doclengths.get(post[0]) * query_vector[i]) * diff_weight
                else:
                    scores[post[0]] = ((idf.get(termid) * post[1]) / doclengths.get(post[0]) * query_vector[i]) * diff_weight

    return scores

#function to find snippets
def get_snippet(query_terms, docid):
    snippet = ''
    
    summary = summaries[docid]
    description = descriptions[docid]
    title = titles[docid]

    
    if description != "" and not summary.isspace():
        snippet =sent_tokenize(descriptions[docid])[0]#get a snippet on description
    else:
        snippet = sent_tokenize(summary)[0] if not snippet else snippet[0] #or on summary if no description is available
    
    return snippet

def flatten(list):
    for el in list:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el

#creating the results
def results_table(index, query_terms, docid):
    table_data = [[],[]]

    title = titles[docid]
    url = docids[docid]
    table_data[0] = [str(index) + ' ' + title + url] #results table is index, title and url
    snippet = get_snippet(query_terms, docid)
    table_data[1].append((snippet))#and snippet
    return table_data

def do_rocchio(query_terms, scores):
    global query_vector
    global rocchio_non_rel_docs

    rel_docs_user = input("Enter the indexes of the relevant documents without space:\n")
    rel_scores = [0]
    rel_docids = []

    if rel_docs_user != "" and not rel_docs_user.isspace():
        rel_docs_user = list(rel_docs_user) #creating list from user's input
        for i in rel_docs_user:
            k = list(scores.keys())[int(i)]
            rel_scores.append(scores.get(k))#appending the scores of the relevant documents
            rel_docids.append(k)#appending the relevant ids

    for docid in rel_docids:#remaining non relevant documents
        del scores[docid]


    #finding the total of documents that have to be removed
    rocchio_non_rel_docs |= set(scores.keys())

    
    #calculating the mean of the relevant documents,
    rel_mean = sum(rel_scores) / len(rel_scores)

    #calculating the mean of the non-relevant documents
    non_rel_mean = sum(scores.values()) / len(scores)
    
    new_query_vector = []
    for vector in query_vector:
        new_vector = vector + (0.5 * rel_mean) - (0.25 * non_rel_mean)#rocchio equation
        if new_vector > 0:
            new_query_vector.append(new_vector)
        else:
            new_query_vector.append(0)#if any negative set to 0

    query_vector = new_query_vector
    retrieve(query_terms, rocchio=True)#retrieve again

# This is a basic vector model retrieval with tf*idf weighting
def retrieve(query_terms, rocchio=False, data=None, should_print=True):
    global docids
    global postings
    global vocab
    global doclengths
    global titles
    global headings
    global descriptions
    global summaries
    global rocchio_non_rel_docs
    global query_vector

    
    if not rocchio:
        rocchio_non_rel_docs = set()
        query_vector = []

    
    if (data): #getting from cache
        docids = data.doc_ids
        doclengths = data.doc_lengths
        postings = data.postings
        vocab = data.vocab
        titles = data.titles
        headings = data.headings
        descriptions = data.descriptions
        summaries = data.summaries

    query_terms = set(query_terms)

    scores = tf_idf(query_terms, rocchio) #calculating tf*idf

    if should_print:
        amount_to_print = 10
        i = 0
        scores_for_feedback = collections.OrderedDict()
        for docid in sorted(scores, key=scores.get, reverse=True):
            i += 1
            scores_for_feedback[docid] = scores.get(docid)
            if (i == amount_to_print):
                letter = ''
                while (letter != "c"):
                    letter = input("Type 'feedback' to give feedback or 'stop' to exit...\n")
                    if (letter == "stop"):
                        return
                    elif (letter == "feedback"):
                        do_rocchio(query_terms, scores_for_feedback)
                        return
                    i = 0
            table = results_table(i, query_terms, docid)#constract the table
            print(str(table[0]) + '\n' + str(table[1]) + '\n')
    else:
        return scores
        