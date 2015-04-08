from collections import namedtuple
import json

import numpy as np
import pandas as pd
from skbio.stats.ordination import PCoA
from skbio.stats.distance import DistanceMatrix

import scipy.spatial.distance as dist
from scipy.stats import entropy

def __num_dist_rows__(array, ndigits=2):
   return int(pd.DataFrame(array).sum(axis=1).map(lambda x: round(x, ndigits)).sum())

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

def jensen_shannon(_P, _Q):
    _M = 0.5 * (_P + _Q)
    return 0.5 * (entropy(_P, _M) + entropy(_Q, _M))

def js_PCoA(distributions):
   dist_matrix = DistanceMatrix(dist.squareform(dist.pdist(distributions.values, jensen_shannon)))
   pcoa = PCoA(dist_matrix).scores()
   return pcoa.site[:,0:2]

def _df_with_names(data, index_name, columns_name):
   df = pd.DataFrame(data)
   df.index.name = index_name
   df.columns.name = columns_name
   return df

def _mds_df(mds, topic_term_dists, topic_proportion):
   K = topic_term_dists.shape[0]
   mds_res = mds(topic_term_dists)
   assert mds_res.shape == (K, 2)
   mds_df = pd.DataFrame({'x': mds_res[:,0], 'y': mds_res[:,1], 'topics': range(1, K + 1), \
                          'cluster': 1, 'Freq': topic_proportion * 100})
   # note: cluster (should?) be deprecated soon. See: https://github.com/cpsievert/LDAvis/issues/26
   return mds_df

# phi  - topic_merm_dists
# theta - doc_topic_dists
def prepare(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency, R=30, lambda_step = 0.01, mds=js_PCoA, plot_opts={'xlabel': 'PC1', 'ylabel': 'PC2'}):
   topic_term_dists = _df_with_names(topic_term_dists, 'topic', 'term')
   doc_topic_dists  = _df_with_names(doc_topic_dists, 'doc', 'topic')
   term_frequency   = pd.Series(term_frequency, name='term_frequency')
   doc_lengths      = pd.Series(doc_lengths, name='doc_length')
   vocab            = pd.Series(vocab, name='vocab')
   K = num_topics   = topic_term_dists.shape[0]

   _input_validate(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency)

   topic_freq = (doc_topic_dists.T * doc_lengths).T.sum()
   topic_proportion = (topic_freq / topic_freq.sum()).order(ascending=False)
   topic_order = topic_proportion.index
   topic_freq = topic_freq[topic_order]

   topic_term_dists = topic_term_dists.ix[topic_order]
   doc_topic_dists = doc_topic_dists[topic_order]

   mds_df = _mds_df(mds, topic_term_dists, topic_proportion)

   # marginal distribution over terms (width of blue bars)
   term_proportion = term_frequency / term_frequency.sum()
   # token counts for each term-topic combination (widths of red bars)
   term_topic_freq = (topic_term_dists.T  * topic_freq).T
   # adjust to match term frequencies exactly (get rid of rounding error)
   err = term_frequency / term_topic_freq.sum()
   term_topic_freq = term_topic_freq * err

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
      sort('saliency', ascending=False). \
      head(R).drop('saliency', 1)
   ranks = np.arange(R, 0, -1)
   default_term_info['logprob'] = default_term_info['loglift'] = ranks

   ## compute relevance and top terms for each topic
   log_lift = np.log(topic_term_dists / term_proportion)
   log_ttd = np.log(topic_term_dists)
   lambda_seq = np.arange(0, 1 + lambda_step, lambda_step)

   def find_relevance(lambda_):
      relevance = lambda_ * log_ttd + (1 - lambda_) * log_lift
      return relevance.T.apply(lambda s: s.order(ascending=False).index).head(R)

   topic_order = list(topic_order)
   def topic_top_term_df((original_topic_id, topic_terms)):
      new_topic_id = topic_order.index(original_topic_id) + 1
      term_ix = topic_terms.unique()
      return pd.DataFrame({'Term': vocab[term_ix], \
                           'Freq': term_topic_freq.loc[original_topic_id, term_ix], \
                           'Total': term_frequency[term_ix], \
                           'logprob': log_ttd.loc[original_topic_id, term_ix].round(4), \
                           'loglift': log_lift.loc[original_topic_id, term_ix].round(4), \
                           'Category': 'Topic%d' % new_topic_id})

   top_terms = pd.concat(map(find_relevance, lambda_seq))
   topic_dfs = map(topic_top_term_df, top_terms.T.iterrows())
   topic_info = pd.concat([default_term_info] + topic_dfs)

   # last, to compute the areas of the circles when a term is highlighted
   # we must gather all unique terms that could show up (for every combination
   # of topic and value of lambda) and compute its distribution over topics.

   # term-topic frequency table of unique terms across all topics and all values of lambda
   term_ix = topic_info.index.unique()
   term_ix.sort()
   top_topic_terms_freq = term_topic_freq[term_ix]
   # use the new ordering for the topics
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
   token_table.sort(['Term', 'Topic'], inplace=True)

   client_topic_order = [x + 1 for x in topic_order]
   return PreparedData(mds_df, topic_info, token_table, R, lambda_step, plot_opts, client_topic_order)

class PreparedData(namedtuple('PreparedData', ['mds_df', 'topic_info', 'token_table',\
                                               'R', 'lambda_step', 'plot_opts', 'topic_order'])):
    def to_dict(self):
       return {'mdsDat': self.mds_df.to_dict(orient='list'),
               'tinfo': self.topic_info.to_dict(orient='list'),
               'token.table': self.token_table.to_dict(orient='list'),
               'R': self.R,
               'lambda.step': self.lambda_step,
               'plot.opts': self.plot_opts,
               'topic.order': self.topic_order}

def create_json(*args, **kargs):
   return json.dumps(prepare(*args, **kargs).to_dict())
