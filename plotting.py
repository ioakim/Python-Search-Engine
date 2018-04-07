import numpy as np
import matplotlib.pyplot as plt
import copy

files = ["doc_status/basic.csv", "doc_status/stem.csv", "doc_status/weight.csv", "doc_status/relevance.csv"]

systems = {} # Holds the mean points for each system
rel_docs = []

rel_file = open('doc_status/IR_queries_2017_recall.txt', 'r')

for line in rel_file:
    rel_docs.append(int(line))

index = 0
for filename in files:
    f = open(filename, 'r')
    
    retrieved_doc_status = {}
    nDocs = 0
    for line in f:
        thisLine = line.strip() # Get rid of line-feed
        lineItems = thisLine.split()          # Split the line into items by space
        retrieved_doc_status[nDocs] = [int(i) for i in lineItems[0:len(lineItems)]] # Convert a list of strings into a list of integers
        nDocs += 1
    print("Read %d retrieved document status lines from file" % nDocs)
    nQueries = len(retrieved_doc_status[0])
    query_one_status = [0]*nDocs
    for doc in retrieved_doc_status.keys():
        query_one_status[doc] = retrieved_doc_status[doc][0]
    
    total_rel = rel_docs[index]#total relevant are numbers Dan gave 
    index += 1
    
    rel_after_i_seen = np.cumsum(query_one_status)

    thisQuery = [0]*nDocs # Holds current query
    allPrecisionValues = [] # Holds ALL precision values over all queries
    allRecallValues = []
    precision_points = {}
    recall_points = {}
    for q in range(0, nQueries):
        for doc in retrieved_doc_status.keys():
            thisQuery[doc] = retrieved_doc_status[doc][q]  # Get the q'th column of retrieved_doc_status = response to q'th query
        thisCumSum = np.cumsum(thisQuery) # and its cumulative sum

        precision_value = []
        recall_value = []
        # total_rel_docs = 0
        for i in range (0,nDocs):
            if precision_points.get(q):
                precision_points.get(q).append(thisCumSum[i]/(i+1))
            else:
                precision_points[q] = [thisCumSum[i]/(i+1)]
            if recall_points.get(q):
                recall_points.get(q).append(rel_after_i_seen[i] / total_rel)
            else:
                recall_points[q] = [rel_after_i_seen[i] / total_rel]
            
            if thisQuery[i] == 1:
                precision_value.append( thisCumSum[i]/(i+1) )
                allPrecisionValues.append( thisCumSum[i]/(i+1) )
                allRecallValues.append(rel_after_i_seen[i] / total_rel)
                recall_value.append(rel_after_i_seen[i] / total_rel)
        # for i in range (0, nDocs):
            # if thisQuery[i] == 1:
        thisAverageValue = np.mean( precision_value )
        thisRecallValue = np.mean( recall_value )
        print('Average precision value for query no %d = %.4f' % (q+1, thisAverageValue) )
        print('Average recall value for query no %d = %.4f' % (q+1, thisRecallValue) )

    recall = []
    precision = []
    avg_fscore = []
    for i in range(0, 10):
        prec_total = 0
        rec_total = 0
        for prec_points in precision_points.values():
            prec_total += prec_points[i]
        precision.append(prec_total/10)
        for rec_points in recall_points.values():
            rec_total += rec_points[i]
        recall.append(rec_total/10)


    systems[filename] = [recall, precision] # mean precision, recall


print(systems)
plt.figure()
plt.rcParams.update({'font.size': 14}) # Sets all font-sizes to 14

basic = systems.get(files[0])
recall_basic = basic[1]
precision_basic = basic[0]

stem = systems.get(files[1])
recall_stem = stem[1]
precision_stem = stem[0]

weight = systems.get(files[2])
recall_weight = weight[1]
precision_weight = weight[0]

relfbk = systems.get(files[3])
recall_relfbk = relfbk[1]
precision_relfbk = relfbk[0]

# print(precision_basic)
plt.plot(precision_basic, recall_basic, '-b+', label='Precision-recall Basic')
plt.plot(precision_stem, recall_stem, '-g+', label='Precision-recall Stem')
plt.plot(precision_weight, recall_weight, '-r+', label='Precision-recall Weight')
plt.plot(precision_relfbk, recall_relfbk, '-c+', label='Precision-recall Relfbk')


plt.xlabel('Recall', weight='bold')
plt.ylabel('Precision', weight='bold')
plt.title('Average precision versus recall over the set of queries')
plt.grid()
plt.legend(loc='upper right')
plt.show()
