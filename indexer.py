import sys
import re
import string
import json
from document import Document
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
import unidecode

# global declarations for doclist, postings, vocabulary
# docids could be doc metadata, which consists of:
# docID(key) = [the URL, the length of the document, description of document]

docids = []
postings = {}
vocab = []
doclengths = {}
titles = []
headings = []
descriptions = []
summaries = []


def main():
    return


def read_index_files(): #checking the index files
    try:
        with open('index_files/docids.txt','r') as file:
            docids = eval(file.read())
        with open('index_files/doclengths.txt', 'r') as file:
            doclengths = eval(file.read())
            doclengths = {int(k):v for k, v in doclengths.items()}
        with open('index_files/postings.txt', 'r') as file:
            postings = eval(file.read())
            postings = {int(k):v for k, v in postings.items()}
        with open('index_files/vocab.txt', 'r') as file:
            vocab = eval(file.read())
    except:
        print("There is something wrong with the index. Try indexing again.")

def write_index():
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclengths
    global titles
    global headings
    global descriptions
    global summaries

    # writes to index files: docids, vocab, postings
    outlist1 = open('index_files/docids.txt', 'w')
    outlist2 = open('index_files/vocab.txt', 'w')
    outlist3 = open('index_files/postings.txt', 'w')
    outlist4 = open('index_files/doclengths.txt', 'w')
    outlist5 = open('index_files/doc_structure/titles.txt', 'w')
    outlist6 = open('index_files/doc_structure/headings.txt', 'w')
    outlist7 = open('index_files/doc_structure/descriptions.txt', 'w')
    outlist8 = open('index_files/doc_structure/summaries.txt', 'w')


    json.dump(docids, outlist1)
    json.dump(vocab, outlist2)
    json.dump(postings, outlist3)
    json.dump(doclengths, outlist4)
    json.dump(titles, outlist5)
    json.dump(headings, outlist6)
    json.dump(descriptions, outlist7)
    json.dump(summaries, outlist8)

    outlist1.close()
    outlist2.close()
    outlist3.close()
    outlist4.close()
    outlist5.close()
    outlist6.close()
    outlist7.close()
    outlist8.close()

    return

def make_index(url, page_contents):
    # declare refs to global variables
    global docids
    global postings
    global vocab
    global doclengths
    global titles
    global headings
    global descriptions
    global summaries

    print('===============================================')
    print('make_index: url = ', url)
    print('===============================================')
    
    

    document = clean_document(page_contents)#get the cleaned content from html
    tokens = document.vocab
    

    docID = len(docids) # Get the docID and add the URL to docs


    #remove http or https to avoid duplicate urls
    re_http = r'https|http|www[.]|www\d[.]|:\/\/'
    url = re.sub(re_http, '', url)
    if url in docids:
        return

    docids.append(url) #add the url to docids
    doclengths[docID] = len(tokens)
    
    #add the titles, headings, description and summaries to separate files to use later
    titles.append(document.title)
    headings.append(document.heading)
    descriptions.append(document.description)
    summaries.append(document.summary)

    
    token_pos = []
    for token in tokens:
        # Get the termID and add the token in vocab if not there
        if token in vocab:
            termID = vocab.index(token)
        else:
            termID = len(vocab)
            vocab.append(token)
        token_pos = re.finditer(re.escape(token), document.summary, re.IGNORECASE)

        # Find instances of this token in the summary of the document.
        term_pos = [m.start(0) for m in token_pos]

        
        docIDs_freqs = postings.get(termID) #check if the termid is in the postings table
        if docIDs_freqs is not None:
            
            docs = [item[0] for item in docIDs_freqs] #list of docIDs

            if docID in docs: #if the docid is in the list
                docIndex = docs.index(docID)
                docIDs_freqs[docIndex][1] += 1 #increase the frequency
            else:
                postings[termID].append([docID, 1, term_pos]) #or else iniatilise it to 1
        else:
            postings[termID] = [[docID, 1, term_pos]] #if noi in postings add it
    return

def stem_vocab(vocab): #function to stem the vocab
    porter_s = PorterStemmer(mode='NLTK_EXTENSIONS')
    words = word_tokenize(vocab)
    vocab = [porter_s.stem(word) for word in words]
    return vocab


#cleaning the document from HTML tags and unnesecary stuff
def clean_document(page_contents):
    # first convert bytes to string if necessary
    if isinstance(page_contents, bytes):
        page_contents = page_contents.decode('utf-8', 'ignore')

    re_punctuation = r'(?<!\d)[^a-zA-Z0-9%+\']+|[^a-zA-Z0-9%+\']+(?!\d)'
    re_alt_tags = r'<img alt="(.*?)".*?>'
    re_description = r'name="description"[^>]*content="([^"]+)"|content="([^"]+)"[^>]*name="description"'
    re_heading = r'<h1>([\w].*)<\/h1>'
    re_title = r'<title>(.+)<\/title>'
    re_spans = r'<span.*?>.*?<\/span>'
    re_all_tags = r'<script.*?>.*?<\/script>|<style.*?>.*?<\/style>|<.+?>|&nbsp|&amp'
    re_lists = r'<li.*?>.*?<\/li>|<ul.*?>.*?<\/ul>'
    
    
    #all UEA have their content in portlet-body
    re_page_content = r'(<div class="portlet-body">.*?<footer.*?>)'
    re_links = r'(?<!href=")(\b[\w]+:\/\/[\w?\-._\/=]+[\w\/])'

    # remove line breaks
    page_contents = page_contents.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    page_contents = unidecode.unidecode(page_contents)

    #find the title, heading and description
    title = re.search(re_title, page_contents)
    heading = re.search(re_heading, page_contents)
    description = re.findall(re_description, page_contents)

    #remove spans and lists
    summary = re.sub(re_spans, ' ', page_contents)
    summary = re.sub(re_lists, ' ', summary)
    summary = re.sub(re_heading, ' ', summary)
    #extract the summary
    summary = re.search(re_page_content, summary)

    # remove code between content in alt tags and meta tags
    # r"\1" keeps the group between parenthesis of the pattern
    page_contents = re.sub(re_alt_tags, r"\1", page_contents)
    page_contents = re.sub(re_description, r"\1", page_contents)
    
    # remove all tags
    page_contents = re.sub(re_all_tags, ' ', page_contents)
    
    # remove punctuation, lowercase and split
    vocab = re.sub(re_punctuation, ' ', page_contents).lower()

    # remove stopwords a, the
    vocab = re.sub(r'\sa\s|\sthe\s', ' ', vocab)
    vocab = stem_vocab(vocab)

    description = ' '.join(str(group) for group in description[0]) if description else ''
   

    heading = '' if not heading else heading.group(1)
        
    document = Document(0, title.group(1), heading, summary, description, vocab)#constract the document
    return document

# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
