"""
pyLDAvis Prepare
===============
Main transformation functions for preparing LDAdata to the visualization's data structures
"""

from __future__ import absolute_import
from past.builtins import basestring
from collections import namedtuple
import json
import logging
from joblib import Parallel, delayed, cpu_count
import numpy as np
import pandas as pd
from scipy.stats import entropy
from scipy.spatial.distance import pdist, squareform
from .utils import NumPyEncoder
try:
    from sklearn.manifold import MDS, TSNE
    sklearn_present = True
except ImportError:
    sklearn_present = False


def __num_dist_rows__(array, ndigits=2):
   return array.shape[0] - int((pd.DataFrame(array).sum(axis=1) < 0.999).sum())


class ValidationError(ValueError):
   pass


def _input_check(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency):
   ttds = topic_term_dists.shape
   dtds = doc_topic_dists.shape
   errors = []
   def err(msg):
      errors.append(msg)

   if dtds[1] != ttds[0]:
      err('Number of rows of topic_term_dists does not match number of columns of doc_topic_dists; both should be equal to the number of topics in the model.')

   if len(doc_lengths) != dtds[0]:
      err('Length of doc_lengths not equal to the number of rows in doc_topic_dists; both should be equal to the number of documents in the data.')

   W = len(vocab)
   if ttds[1] != W:
      err('Number of terms in vocabulary does not match the number of columns of topic_term_dists (where each row of topic_term_dists is a probability distribution of terms for a given topic).')
   if len(term_frequency) != W:
      err('Length of term_frequency not equal to the number of terms in the vocabulary (len of vocab).')

   if __num_dist_rows__(topic_term_dists) != ttds[0]:
      err('Not all rows (distributions) in topic_term_dists sum to 1.')

   if __num_dist_rows__(doc_topic_dists) != dtds[0]:
      err('Not all rows (distributions) in doc_topic_dists sum to 1.')

   if len(errors) > 0:
      return errors


def _input_validate(*args):
   res = _input_check(*args)
   if res:
      raise ValidationError('\n' + '\n'.join([' * ' + s for s in res]))


def _jensen_shannon(_P, _Q):
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))


def _pcoa(pair_dists, n_components=2):
    """Principal Coordinate Analysis,
    aka Classical Multidimensional Scaling
    """
    # code referenced from skbio.stats.ordination.pcoa
    # https://github.com/biocore/scikit-bio/blob/0.5.0/skbio/stats/ordination/_principal_coordinate_analysis.py

    # pairwise distance matrix is assumed symmetric
    pair_dists = np.asarray(pair_dists, np.float64)

    # perform SVD on double centred distance matrix
    n = pair_dists.shape[0]
    H = np.eye(n) - np.ones((n, n)) / n
    B = - H.dot(pair_dists ** 2).dot(H) / 2
    eigvals, eigvecs = np.linalg.eig(B)

    # Take first n_components of eigenvalues and eigenvectors
    # sorted in decreasing order
    ix = eigvals.argsort()[::-1][:n_components]
    eigvals = eigvals[ix]
    eigvecs = eigvecs[:, ix]

    # replace any remaining negative eigenvalues and associated eigenvectors with zeroes
    # at least 1 eigenvalue must be zero
    eigvals[np.isclose(eigvals, 0)] = 0
    if np.any(eigvals < 0):
        ix_neg = eigvals < 0
        eigvals[ix_neg] = np.zeros(eigvals[ix_neg].shape)
        eigvecs[:, ix_neg] = np.zeros(eigvecs[:, ix_neg].shape)

    return np.sqrt(eigvals) * eigvecs


def js_PCoA(distributions):
    """Dimension reduction via Jensen-Shannon Divergence & Principal Coordinate Analysis
    (aka Classical Multidimensional Scaling)

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    Returns
    -------
    pcoa : array, shape (`n_dists`, 2)
    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    return _pcoa(dist_matrix)


def js_MMDS(distributions, **kwargs):
    """Dimension reduction via Jensen-Shannon Divergence & Metric Multidimensional Scaling

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    **kwargs : Keyword argument to be passed to `sklearn.manifold.MDS()`

    Returns
    -------
    mmds : array, shape (`n_dists`, 2)
    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    model = MDS(n_components=2, random_state=0, dissimilarity='precomputed', **kwargs)
    return model.fit_transform(dist_matrix)


def js_TSNE(distributions, **kwargs):
    """Dimension reduction via Jensen-Shannon Divergence & t-distributed Stochastic Neighbor Embedding

    Parameters
    ----------
    distributions : array-like, shape (`n_dists`, `k`)
        Matrix of distributions probabilities.

    **kwargs : Keyword argument to be passed to `sklearn.manifold.TSNE()`

    Returns
    -------
    tsne : array, shape (`n_dists`, 2)
    """
    dist_matrix = squareform(pdist(distributions, metric=_jensen_shannon))
    model = TSNE(n_components=2, random_state=0, metric='precomputed', **kwargs)
    return model.fit_transform(dist_matrix)


def _df_with_names(data, index_name, columns_name):
   if type(data) == pd.DataFrame:
      # we want our index to be numbered
      df = pd.DataFrame(data.values)
   else:
      df = pd.DataFrame(data)
   df.index.name = index_name
   df.columns.name = columns_name
   return df


def _series_with_name(data, name):
   if type(data) == pd.Series:
      data.name = name
      # ensures a numeric index
      return data.reset_index()[name]
   else:
      return pd.Series(data, name=name)


def _topic_coordinates(mds, topic_term_dists, topic_proportion):
   K = topic_term_dists.shape[0]
   mds_res = mds(topic_term_dists)
   assert mds_res.shape == (K, 2)
   mds_df = pd.DataFrame({'x': mds_res[:,0], 'y': mds_res[:,1], 'topics': range(1, K + 1), \
                          'cluster': 1, 'Freq': topic_proportion * 100})
   # note: cluster (should?) be deprecated soon. See: https://github.com/cpsievert/LDAvis/issues/26
   return mds_df


def _chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i+n]


def _job_chunks(l, n_jobs):
   n_chunks = n_jobs
   if n_jobs < 0:
      # so, have n chunks if we are using all n cores/cpus
      n_chunks = cpu_count() + 1 - n_jobs

   return _chunks(l, n_chunks)


def _find_relevance(log_ttd, log_lift, R, lambda_):
   relevance = lambda_ * log_ttd + (1 - lambda_) * log_lift
   return relevance.T.apply(lambda s: s.sort_values(ascending=False).index).head(R)


def _find_relevance_chunks(log_ttd, log_lift, R, lambda_seq):
   return pd.concat([_find_relevance(log_ttd, log_lift, R, l) for l in lambda_seq])


def _topic_info(topic_term_dists, topic_proportion, term_frequency, term_topic_freq, vocab, lambda_step, R, n_jobs):
   # marginal distribution over terms (width of blue bars)
   term_proportion = term_frequency / term_frequency.sum()

   # compute the distinctiveness and saliency of the terms:
   # this determines the R terms that are displayed when no topic is selected
   topic_given_term = topic_term_dists / topic_term_dists.sum()
   kernel = (topic_given_term * np.log((topic_given_term.T / topic_proportion).T))
   distinctiveness = kernel.sum()
   saliency = term_proportion * distinctiveness

   # Order the terms for the "default" view by decreasing saliency:
   default_term_info  = pd.DataFrame({'saliency': saliency, 'Term': vocab, \
                                      'Freq': term_frequency, 'Total': term_frequency, \
                                      'Category': 'Default'}). \
      sort_values(by='saliency', ascending=False). \
      head(R).drop('saliency', 1)
   # Rounding Freq and Total to integer values to match LDAvis code:
   default_term_info['Freq'] = np.floor(default_term_info['Freq'])
   default_term_info['Total'] = np.floor(default_term_info['Total'])
   ranks = np.arange(R, 0, -1)
   default_term_info['logprob'] = default_term_info['loglift'] = ranks

   ## compute relevance and top terms for each topic
   log_lift = np.log(topic_term_dists / term_proportion)
   log_ttd = np.log(topic_term_dists)
   lambda_seq = np.arange(0, 1 + lambda_step, lambda_step)

   def topic_top_term_df(tup):
      new_topic_id, (original_topic_id, topic_terms) = tup
      term_ix = topic_terms.unique()
      return pd.DataFrame({'Term': vocab[term_ix], \
                           'Freq': term_topic_freq.loc[original_topic_id, term_ix], \
                           'Total': term_frequency[term_ix], \
                           'logprob': log_ttd.loc[original_topic_id, term_ix].round(4), \
                           'loglift': log_lift.loc[original_topic_id, term_ix].round(4), \
                           'Category': 'Topic%d' % new_topic_id})

   top_terms = pd.concat(Parallel(n_jobs=n_jobs)(delayed(_find_relevance_chunks)(log_ttd, log_lift, R, ls) \
                                                 for ls in _job_chunks(lambda_seq, n_jobs)))
   topic_dfs = map(topic_top_term_df, enumerate(top_terms.T.iterrows(), 1))
   return pd.concat([default_term_info] + list(topic_dfs))


def _token_table(topic_info, term_topic_freq, vocab, term_frequency):
   # last, to compute the areas of the circles when a term is highlighted
   # we must gather all unique terms that could show up (for every combination
   # of topic and value of lambda) and compute its distribution over topics.

   # term-topic frequency table of unique terms across all topics and all values of lambda
   term_ix = topic_info.index.unique()
   term_ix = np.sort(term_ix)

   top_topic_terms_freq = term_topic_freq[term_ix]
   # use the new ordering for the topics
   K = len(term_topic_freq)
   top_topic_terms_freq.index = range(1, K + 1)
   top_topic_terms_freq.index.name = 'Topic'

   # we filter to Freq >= 0.5 to avoid sending too much data to the browser
   token_table = pd.DataFrame({'Freq': top_topic_terms_freq.unstack()}). \
                 reset_index().set_index('term'). \
                 query('Freq >= 0.5')

   token_table['Freq'] = token_table['Freq'].round()
   token_table['Term'] = vocab[token_table.index.values].values
   # Normalize token frequencies:
   token_table['Freq'] = token_table.Freq / term_frequency[token_table.index]
   return token_table.sort_values(by=['Term', 'Topic'])


def prepare(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency, \
            R=30, lambda_step=0.01, mds=js_PCoA, n_jobs=-1, \
            plot_opts={'xlab': 'PC1', 'ylab': 'PC2'}, sort_topics=True):
   """Transforms the topic model distributions and related corpus data into
   the data structures needed for the visualization.

    Parameters
    ----------
    topic_term_dists : array-like, shape (`n_topics`, `n_terms`)
        Matrix of topic-term probabilities. Where `n_terms` is `len(vocab)`.
    doc_topic_dists : array-like, shape (`n_docs`, `n_topics`)
        Matrix of document-topic probabilities.
    doc_lengths : array-like, shape `n_docs`
        The length of each document, i.e. the number of words in each document.
        The order of the numbers should be consistent with the ordering of the
        docs in `doc_topic_dists`.
    vocab : array-like, shape `n_terms`
        List of all the words in the corpus used to train the model.
    term_frequency : array-like, shape `n_terms`
        The count of each particular term over the entire corpus. The ordering
        of these counts should correspond with `vocab` and `topic_term_dists`.
    R : int
        The number of terms to display in the barcharts of the visualization.
        Default is 30. Recommended to be roughly between 10 and 50.
    lambda_step : float, between 0 and 1
        Determines the interstep distance in the grid of lambda values over
        which to iterate when computing relevance.
        Default is 0.01. Recommended to be between 0.01 and 0.1.
    mds : function or a string representation of function
        A function that takes `topic_term_dists` as an input and outputs a
        `n_topics` by `2`  distance matrix. The output approximates the distance
        between topics. See :func:`js_PCoA` for details on the default function.
        A string representation currently accepts `pcoa` (or upper case variant),
        `mmds` (or upper case variant) and `tsne` (or upper case variant),
        if `sklearn` package is installed for the latter two.
    n_jobs : int
        The number of cores to be used to do the computations. The regular
        joblib conventions are followed so `-1`, which is the default, will
        use all cores.
    plot_opts : dict, with keys 'xlab' and `ylab`
        Dictionary of plotting options, right now only used for the axis labels.
    sort_topics : sort topics by topic proportion (percentage of tokens covered). Set to false to
        to keep original topic order.

    Returns
    -------
    prepared_data : PreparedData
        A named tuple containing all the data structures required to create
        the visualization. To be passed on to functions like :func:`display`.

    Notes
    -----
    This implements the method of `Sievert, C. and Shirley, K. (2014):
    LDAvis: A Method for Visualizing and Interpreting Topics, ACL Workshop on
    Interactive Language Learning, Visualization, and Interfaces.`

    http://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf

    See Also
    --------
    :func:`save_json`: save json representation of a figure to file
    :func:`save_html` : save html representation of a figure to file
    :func:`show` : launch a local server and show a figure in a browser
    :func:`display` : embed figure within the IPython notebook
    :func:`enable_notebook` : automatically embed visualizations in IPython notebook
   """
   # parse mds
   if isinstance(mds, basestring):
      mds = mds.lower()
      if mds == 'pcoa':
         mds = js_PCoA
      elif mds in ('mmds', 'tsne'):
         if sklearn_present:
            mds_opts = {'mmds': js_MMDS, 'tsne': js_TSNE}
            mds = mds_opts[mds]
         else:
            logging.warning('sklearn not present, switch to PCoA')
            mds = js_PCoA
      else:
         logging.warning('Unknown mds `%s`, switch to PCoA' % mds)
         mds = js_PCoA

   topic_term_dists = _df_with_names(topic_term_dists, 'topic', 'term')
   doc_topic_dists  = _df_with_names(doc_topic_dists, 'doc', 'topic')
   term_frequency   = _series_with_name(term_frequency, 'term_frequency')
   doc_lengths      = _series_with_name(doc_lengths, 'doc_length')
   vocab            = _series_with_name(vocab, 'vocab')
   _input_validate(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency)
   R = min(R, len(vocab))

   topic_freq       = (doc_topic_dists.T * doc_lengths).T.sum()
   # topic_freq       = np.dot(doc_topic_dists.T, doc_lengths)
   if (sort_topics):
    topic_proportion = (topic_freq / topic_freq.sum()).sort_values(ascending=False)
   else:
    topic_proportion = (topic_freq / topic_freq.sum())

   topic_order      = topic_proportion.index
   # reorder all data based on new ordering of topics
   topic_freq       = topic_freq[topic_order]
   topic_term_dists = topic_term_dists.iloc[topic_order]
   doc_topic_dists  = doc_topic_dists[topic_order]

   # token counts for each term-topic combination (widths of red bars)
   term_topic_freq = (topic_term_dists.T * topic_freq).T
   ## Quick fix for red bar width bug.  We calculate the
   ## term frequencies internally, using the topic term distributions and the
   ## topic frequencies, rather than using the user-supplied term frequencies.
   ## For a detailed discussion, see: https://github.com/cpsievert/LDAvis/pull/41
   term_frequency = np.sum(term_topic_freq, axis=0)

   topic_info         = _topic_info(topic_term_dists, topic_proportion, term_frequency, term_topic_freq, vocab, lambda_step, R, n_jobs)
   token_table        = _token_table(topic_info, term_topic_freq, vocab, term_frequency)
   topic_coordinates = _topic_coordinates(mds, topic_term_dists, topic_proportion)
   client_topic_order = [x + 1 for x in topic_order]

   return PreparedData(topic_coordinates, topic_info, token_table, R, lambda_step, plot_opts, client_topic_order)

class PreparedData(namedtuple('PreparedData', ['topic_coordinates', 'topic_info', 'token_table',\
                                               'R', 'lambda_step', 'plot_opts', 'topic_order'])):
    def to_dict(self):
       return {'mdsDat': self.topic_coordinates.to_dict(orient='list'),
               'tinfo': self.topic_info.to_dict(orient='list'),
               'token.table': self.token_table.to_dict(orient='list'),
               'R': self.R,
               'lambda.step': self.lambda_step,
               'plot.opts': self.plot_opts,
               'topic.order': self.topic_order}

    def to_json(self):
       return json.dumps(self.to_dict(), cls=NumPyEncoder)
