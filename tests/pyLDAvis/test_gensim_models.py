#! /usr/bin/venv python3

import os

from gensim.models import LdaModel, HdpModel, AuthorTopicModel
from gensim.corpora.dictionary import Dictionary
from gensim.test.utils import common_dictionary, common_corpus

import pyLDAvis
import pyLDAvis.gensim_models as gensim_models


def get_author2doc():
    """Crafts a toy mapping between authors and documents (multiple authors per document)."""
    author2doc = {
        'john': [0, 1, 2, 3, 4, 5, 6],
        'jane': [2, 3, 4, 5, 6, 7, 8],
        'jack': [0, 2, 4, 6, 8],
        'jill': [1, 3, 5, 7]
    }
    return author2doc


def get_simple_author2doc():
    """Crafts a toy mapping between authors and documents (single author per document)."""
    author2doc = {
        'john': [0, 1, 2, 3, 4],
        'jane': [5, 6, 7, 8],
    }
    return author2doc


def test_lda():
    """Trains a LDA model and tests the html outputs."""
    lda = LdaModel(corpus=common_corpus, id2word=common_dictionary, num_topics=2)

    data = gensim_models.prepare(lda, common_corpus, common_dictionary)
    pyLDAvis.save_html(data, 'index_lda.html')
    os.remove('index_lda.html')


def test_hdp():
    """Trains a HDP model and tests the html outputs."""
    hdp = HdpModel(corpus=common_corpus, id2word=common_dictionary)

    data = gensim_models.prepare(hdp, common_corpus, common_dictionary)
    pyLDAvis.save_html(data, 'index_hdp.html')
    os.remove('index_hdp.html')


def test_atm():
    """Trains an Author-Topic model and tests the html outputs."""
    atm = AuthorTopicModel(corpus=common_corpus, id2word=common_dictionary,
                           author2doc=get_author2doc(), num_topics=2)

    data = gensim_models.prepare(atm, common_corpus, common_dictionary)
    pyLDAvis.save_html(data, 'index_atm.html')
    os.remove('index_atm.html')

def test_simple_atm():
    """Trains an Author-Topic model and tests the html outputs."""
    atm = AuthorTopicModel(corpus=common_corpus, id2word=common_dictionary,
                           author2doc=get_simple_author2doc(), num_topics=2)

    data = gensim_models.prepare(atm, common_corpus, common_dictionary)
    pyLDAvis.save_html(data, 'index_simple_atm.html')
    os.remove('index_simple_atm.html')


def test_sorted_terms():
    """This tests that we can get the terms of a given topic using lambda
    to calculate the relevance ranking. A common workflow is that once we
    visualize the topics we modify the lambda slide and we are interested
    in a particular lambda value, then with this function we can get the
    terms in that order.
    """
    lda = LdaModel(corpus=common_corpus, id2word=common_dictionary, num_topics=2)

    data = gensim_models.prepare(lda, common_corpus, common_dictionary)
    # https://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf
    # lambda = 0 should rank the terms by loglift
    # lambda = 1 should rank them by logprob.
    sorted_terms = data.sorted_terms(topic=1, _lambda=1).to_dict()
    assert (sorted_terms['logprob'] == sorted_terms['relevance'])
    sorted_terms = data.sorted_terms(topic=1, _lambda=0).to_dict()
    assert (sorted_terms['loglift'] == sorted_terms['relevance'])


if __name__ == "__main__":
    test_lda()
    test_hdp()
    test_atm()
    test_sorted_terms()
