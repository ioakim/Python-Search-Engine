import json

class Document:
    doc_id = 0
    heading = ""
    title = ""
    summary = ""
    description = ""
    vocab = []

    def __init__(self, id, title, heading, summary, description, vocab):
        self.doc_id = id
        self.heading = heading
        self.title = title
        self.summary = summary
        self.description = description
        self.vocab = vocab

    def cache_document(self):
        doc_out = open('index_files/doc_parts/' + str(self.doc_id) + '.txt', 'w')
        data = [self.doc_id, self.title, self.heading, self.summary, self.description]
        json.dump(data, doc_out)
        doc_out.close()
        return

    def set_id(self, id):
        self.doc_id = id