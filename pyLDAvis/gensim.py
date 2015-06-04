"""
pyLDAvis Gensim
===============
Helper functions to visualize LDA models trained by Gensim
"""

import funcy as fp
import numpy as np
import pandas as pd
from past.builtins import xrange
from . import prepare as vis_prepare

def _normalize(array):
   return pd.DataFrame(array).\
      apply(lambda row: row / row.sum(), axis=1).values

def _extract_data(topic_model, corpus, dictionary):
   doc_lengths = [sum([t[1] for t in doc]) for doc in corpus]

   term_freqs_dict = fp.merge_with(sum, *corpus)
   N = len(term_freqs_dict)

   vocab = [dictionary[id] for id in xrange(N)]
   term_freqs = [term_freqs_dict[id] for id in xrange(N)]

   gamma, _ = topic_model.inference(corpus)
   doc_topic_dists = _normalize(gamma)

   topic_term_dists = _normalize(topic_model.state.get_lambda())

   return {'topic_term_dists': topic_term_dists, 'doc_topic_dists': doc_topic_dists,
           'doc_lengths': doc_lengths, 'vocab': vocab, 'term_frequency': term_freqs}

def prepare(topic_model, corpus, dictionary):
    """Transforms the Gensim TopicModel and related corpus and dictionary into
    the data structures needed for the visualization.

    Parameters
    ----------
    topic_model : gensim.models.ldamodel.LdaModel
        An already trained Gensim LdaModel. The other gensim model types are
    not supported (PRs welcome).
    corpus : array-like list of bag of word docs in tuple form
        The corpus in bag of word form, the same docs used to train the model.
    For example: [(50, 3), (63, 5), ....]
    dictionary: gensim.corpora.Dictionary
        The dictionary object used to create the corpus. Needed to extract the
    actual terms (not ids).

    Returns
    -------
    prepared_data : PreparedData
        the data structures used in the visualization

    Example
    --------
    For example usage please see this notebook:
    http://nbviewer.ipython.org/github/bmabey/pyLDAvis/blob/master/notebooks/Gensim%20Newsgroup.ipynb
    """

    return vis_prepare(**_extract_data(topic_model, corpus, dictionary))
