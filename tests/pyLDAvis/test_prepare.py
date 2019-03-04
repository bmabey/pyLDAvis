from __future__ import division

import json
import os.path as path

import funcy as fp


from numpy.testing import assert_array_equal
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal

from pyLDAvis import prepare

roundtrip = fp.compose(json.loads, lambda d: d.to_json(), prepare)

DATA_DIR = path.join(path.dirname(path.realpath(__file__)), "../data/")


def load_dataset(name):
    with open(path.join(DATA_DIR, '%s_input.json' % name), 'r') as j:
        data_input = json.load(j)

    with open(path.join(DATA_DIR, '%s_output.json' % name), 'r') as j:
        expected = json.load(j)

    return data_input, expected


def remove_col_suffixes(df):
    df.columns = [w.split('_')[0] for w in df.columns]
    return df


def test_end_to_end_with_R_examples():
    data_input, expected = load_dataset('movie_reviews')
    output = roundtrip(topic_term_dists=data_input['phi'],
                       doc_topic_dists=data_input['theta'],
                       doc_lengths=data_input['doc.length'],
                       vocab=data_input['vocab'],
                       term_frequency=data_input['term.frequency'], R=30, lambda_step=0.01)

    assert_array_equal(np.array(expected['topic.order']), np.array(output['topic.order']))

    def both(f):
        return f(expected), f(output)

    assert set(expected['tinfo']['Category']) == set(output['tinfo']['Category'])
    etinfo, otinfo = both(lambda d: pd.DataFrame(d['tinfo']))

    eddf = etinfo.query('Category == "Default"')
    eddf = eddf.reindex(sorted(eddf.columns), axis=1)

    oddf = otinfo.query('Category == "Default"')
    oddf = oddf.reindex(sorted(oddf.columns), axis=1)
    assert_frame_equal(eddf, oddf)

    joined = pd.merge(otinfo, etinfo, how='inner', on=['Term', 'Category'], suffixes=['_o', '_e'])
    ejoined = remove_col_suffixes(joined[['Term', 'Category', 'Freq_e',
                                          'Total_e', 'loglift_e', 'logprob_e']])
    ojoined = remove_col_suffixes(joined[['Term', 'Category', 'Freq_o', 'Total_o',
                                          'loglift_o', 'logprob_o']])

    join_percent = float(len(joined)) / len(etinfo)
    print('Topic Info join was %.0f%%' % (100 * join_percent))
    assert_frame_equal(ejoined, ojoined, check_less_precise=True)
    assert join_percent > 0.95

    def abs_basis(df):
        df.x = df.x.abs()
        df.y = df.y.abs()
        return df

    emds, omds = both(lambda r: abs_basis(pd.DataFrame(r['mdsDat'])))
    assert_frame_equal(emds.reindex(sorted(oddf.columns), axis=1),
                       omds.reindex(sorted(oddf.columns), axis=1), check_less_precise=True)

    def rounded_token_table(r):
        tt = pd.DataFrame(r['token.table'])
        tt.Freq = tt.Freq.round(5)
        return tt
    ett, ott = both(rounded_token_table)
    joined = pd.DataFrame(pd.merge(ott, ett, on=['Freq', 'Term'],
                          suffixes=['_o', '_e'], how='inner')
                          .groupby('Topic_o')['Topic_e'].value_counts())
    joined.columns = ['count']
    most_likely_map = joined.query('count > 100')
    most_likely_map.index.names = ['Topic_o', 'Topic_e']
    df = pd.DataFrame(most_likely_map).reset_index()
    assert_array_equal(df['Topic_o'].values, df['Topic_e'].values)
