"""
pyLDAvis GraphLab
===============
Helper functions to visualize GraphLab Create's TopicModel (an implementation of LDA)
"""

import funcy as fp
import numpy as np
import pandas as pd
from . import prepare as vis_prepare

def _topics_as_df(topic_model):
    tdf = topic_model['topics'].to_dataframe()
    return pd.DataFrame(np.vstack(tdf['topic_probabilities'].values), index=tdf['vocabulary'])

def _extract_data(topic_model, docs):
   doc_lengths = [np.array(d.values()).sum() for d in docs]

   term_freqs_dict = fp.merge_with(sum, *docs)
   vocab = term_freqs_dict.keys()
   term_freqs = term_freqs_dict.values()

   doc_topic_dists = np.vstack(topic_model.predict(docs, output_type='probabilities'))

   topics = _topics_as_df(topic_model)
   topic_term_dists = topics.T[vocab].values

   return {'topic_term_dists': topic_term_dists, 'doc_topic_dists': doc_topic_dists,
           'doc_lengths': doc_lengths, 'vocab': vocab, 'term_frequency': term_freqs}

def prepare(topic_model, docs):
    """Transforms the GraphLab TopicModel and related corpus data into
    the data structures needed for the visualization.

    Parameters
    ----------
    topic_model : graphlab.toolkits.topic_model.topic_model.TopicModel
        An already trained GraphLab topic model.
    docs : SArray of dicts
        The corpus in bag of word form, the same docs used to train the model.

    Returns
    -------
    prepared_data : PreparedData
        the data structures used in the visualization

    Example
    --------
    For example usage please see this notebook:
    http://nbviewer.ipython.org/github/bmabey/pyLDAvis/blob/master/notebooks/GraphLab.ipynb
    """
    return vis_prepare(**_extract_data(topic_model, docs))
