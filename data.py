class Data: #mechanism for reading the files from cache
    doc_ids = []
    doc_lengths = {}
    postings = {}
    vocab = {}
    titles = []
    headings = []
    descriptions = []
    summaries = []

    def __init__(self, doc_ids=None, doc_lengths=None, postings=None, vocab=None):
        if (doc_ids is not None):
            self.doc_ids = doc_ids
            self.doc_lengths = doc_lengths
            self.postings = postings
            self.vocab = vocab