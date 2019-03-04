"""
pyLDAvis GraphLab
===============
Helper functions to visualize GraphLab Create's TopicModel (an implementation of LDA)
"""

from __future__ import absolute_import

import funcy as fp
import numpy as np
import pandas as pd
import graphlab as gl
import pyLDAvis


def _topics_as_df(topic_model):
    tdf = topic_model['topics'].to_dataframe()
    return pd.DataFrame(np.vstack(tdf['topic_probabilities'].values), index=tdf['vocabulary'])


def _sum_sarray_dicts(sarray):
    counts_sf = gl.SFrame({
        'count_dicts': sarray}).stack('count_dicts').groupby(
        key_columns='X1',
        operations={'count': gl.aggregate.SUM('X2')})
    return counts_sf.unstack(column=['X1', 'count'])[0].values()[0]


def _extract_doc_data(docs):
    doc_lengths = list(docs.apply(lambda d: np.array(d.values()).sum()))
    term_freqs_dict = _sum_sarray_dicts(docs)

    vocab = term_freqs_dict.keys()
    term_freqs = term_freqs_dict.values()

    return {'doc_lengths': doc_lengths, 'vocab': vocab, 'term_frequency': term_freqs}


def _extract_model_data(topic_model, docs, vocab):
    doc_topic_dists = np.vstack(topic_model.predict(docs, output_type='probabilities'))

    topics = _topics_as_df(topic_model)
    topic_term_dists = topics.T[vocab].values

    return {'topic_term_dists': topic_term_dists, 'doc_topic_dists': doc_topic_dists}


def _extract_data(topic_model, docs):
    doc_data = _extract_doc_data(docs)
    model_data = _extract_model_data(topic_model, docs, doc_data['vocab'])
    return fp.merge(doc_data, model_data)


def prepare(topic_model, docs, **kargs):
    """Transforms the GraphLab TopicModel and related corpus data into
    the data structures needed for the visualization.

    Parameters
    ----------
    topic_model : graphlab.toolkits.topic_model.topic_model.TopicModel
        An already trained GraphLab topic model.
    docs : SArray of dicts
        The corpus in bag of word form, the same docs used to train the model.
    **kwargs :
        additional keyword arguments are passed through to :func:`pyldavis.prepare`.

    Returns
    -------
    prepared_data : PreparedData
        the data structures used in the visualization

    Example
    --------
    For example usage please see this notebook:
    http://nbviewer.ipython.org/github/bmabey/pyLDAvis/blob/master/notebooks/GraphLab.ipynb
    """
    opts = fp.merge(_extract_data(topic_model, docs), kargs)
    return pyLDAvis.prepare(**opts)
