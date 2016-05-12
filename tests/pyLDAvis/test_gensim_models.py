#! /usr/bin/venv python


from gensim.models import LdaModel, HdpModel
from gensim.corpora.dictionary import Dictionary
import pyLDAvis.gensim
import os


def get_corpus_dictionary():
    """Crafts a toy corpus and the dictionary associated."""
    # Toy corpus.
    corpus = [
        ['carrot', 'salad', 'tomato'],
        ['carrot', 'salad', 'dish'],
        ['tomato', 'dish'],
        ['tomato', 'salad'],

        ['car', 'break', 'highway'],
        ['highway', 'accident', 'car'],
        ['moto', 'break'],
        ['accident', 'moto', 'car']
    ]

    dictionary = Dictionary(corpus)

    # Transforming corpus with dictionary.
    corpus = [dictionary.doc2bow(doc) for doc in corpus]

    # Building reverse index.
    for (token, uid) in dictionary.token2id.items():
        dictionary.id2token[uid] = token

    return corpus, dictionary

def test_lda():
    """Trains a LDA model and tests the html outputs."""
    corpus, dictionary = get_corpus_dictionary()

    lda = LdaModel(corpus=corpus,
                   num_topics=2)

    data = pyLDAvis.gensim.prepare(lda, corpus, dictionary)
    pyLDAvis.save_html(data, 'index_lda.html')
    os.remove('index_lda.html')


def test_hdp():
    """Trains a HDP model and tests the html outputs."""
    corpus, dictionary = get_corpus_dictionary()

    hdp = HdpModel(corpus, dictionary.id2token)

    data = pyLDAvis.gensim.prepare(hdp, corpus, dictionary)
    pyLDAvis.save_html(data, 'index_hdp.html')
    os.remove('index_hdp.html')


if __name__ == "__main__":
    test_lda()
    test_hdp()
