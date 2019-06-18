from __future__ import absolute_import
import numpy as np
from past.builtins import basestring
from pyLDAvis._prepare import (
    _input_validate, _series_with_name, _df_with_names,
    js_PCoA , _token_table, _topic_info, _token_table,
    _topic_coordinates,PreparedData)


def generate_topic_freq(doc_topic_dists, doc_lengths):
    """
    doc_topic_dists: Spark partitioned DataFrame object

        column name should be: "doc_id", "topic_dist"

    doc_lengths: Length of each document in spark DataFrame
        By counting number vocabs each document got after pre-processing stage.
        columns: "doc_id", "doc_length"

	Ensure `doc_length` size is same as number of documents in
	`doc_topic_dists`

    #spark: `pyspark.sql.SparkSession` object

    return: topic_freq, for each topic. In np.array format.
    """
    topic_freq = doc_topic_dists\
	.join(doc_lengths, "doc_id")\
	.select("doc_length", "topic_dist")\
	.rdd\
	.map(lambda x: [i*x["doc_length"] for i in x["topic_dist"]])\
	.reduce(lambda dist1, dist2: [a+b for a,b in zip(dist1, dist2)])
    return np.array(topic_freq)


def prepare(topic_freq, topic_term_dists, vocab,
            term_frequency, spark_context=None,
            R=30, lambda_step=0.01, mds=js_PCoA, n_jobs=-1,
            plot_opts={'xlab': 'PC1', 'ylab': 'PC2'}, sort_topics=True):
    """
    The ported the prepare to support the large document size and 100s of topics,
    with the help of apache spark.

    If the documents size is in millions and #topics in hundreds, then getting the
    `doc_topic_dists` itself won't fit in memory.

    Main bottleneck with the python implementation is finding the topic proption
    across entire corpus, ie; (doc_topic_dists.T * document_lenths)
    this operation going to consume lot of memory if we have millions of documents
    and hundereds of topics.

    As `doc_topic_dists` and `doc_lengths` are only used to find the topic 
    distribution on entire corpuse we can make use of spark to do this metix-vector
    multiplication and avoid loading the doc_topic_dists completely into memory at
    once..

    Transforms the topic model distributions and related corpus data into
    the data structures needed for the visualization.

    Parameters
    ----------
    topic_freq : Topic Frequency on entire corpus.
        In default pyLDAVis this quantity was calculated from `doc_topic_dists`
        and `doc_lengths`, in order to support the scale of millions of document
        and hundereds of topics, this operation is kept outside with the help of
        spark. Use the method `pyLDAVis.spark.generate_topic_freq` to generate it.
    topic_term_dists : array-like, shape (`n_topics`, `n_terms`)
        Matrix of topic-term probabilities. Where `n_terms` is `len(vocab)`.
    vocab : array-like, shape `n_terms`
        List of all the words in the corpus used to train the model.
    term_frequency : array-like, shape `n_terms`
        The count of each particular term over the entire corpus. The ordering
        of these counts should correspond with `vocab` and `topic_term_dists`.
    spark_context :  A `pyspark.sql.SparkSession` object
        Initilized with the spark cluster. If provided the complex operations will
        be done using spark_context.
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
        This named tuple can be represented as json or a python dictionary.
        There is a helper function 'sorted_terms' that can be used to get
        the terms of a topic using lambda to rank their relevance.


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
    #doc_topic_dists = _df_with_names(doc_topic_dists, 'doc', 'topic')
    topic_freq = _series_with_name(topic_freq, "topic_frequency")
    term_frequency = _series_with_name(term_frequency, 'term_frequency')
    #doc_lengths = _series_with_name(doc_lengths, 'doc_length')
    vocab = _series_with_name(vocab, 'vocab')
    #_input_validate(topic_term_dists, doc_topic_dists, doc_lengths, vocab, term_frequency)
    R = min(R, len(vocab))

    #topic_freq = (doc_topic_dists.T * doc_lengths).T.sum()
    # topic_freq       = np.dot(doc_topic_dists.T, doc_lengths)
    if (sort_topics):
        topic_proportion = (topic_freq / topic_freq.sum()).sort_values(ascending=False)
    else:
        topic_proportion = (topic_freq / topic_freq.sum())
        
    topic_order = topic_proportion.index
    # reorder all data based on new ordering of topics
    topic_freq = topic_freq[topic_order]
    topic_term_dists = topic_term_dists.iloc[topic_order]
    #doc_topic_dists = doc_topic_dists[topic_order]

    # token counts for each term-topic combination (widths of red bars)
    term_topic_freq = (topic_term_dists.T * topic_freq).T
    # Quick fix for red bar width bug.  We calculate the
    # term frequencies internally, using the topic term distributions and the
    # topic frequencies, rather than using the user-supplied term frequencies.
    # For a detailed discussion, see: https://github.com/cpsievert/LDAvis/pull/41
    term_frequency = np.sum(term_topic_freq, axis=0)

    topic_info = _topic_info(topic_term_dists, topic_proportion,
                             term_frequency, term_topic_freq, vocab, lambda_step, R, n_jobs)
    token_table = _token_table(topic_info, term_topic_freq, vocab, term_frequency)
    topic_coordinates = _topic_coordinates(mds, topic_term_dists, topic_proportion)
    client_topic_order = [x + 1 for x in topic_order]

    return PreparedData(topic_coordinates, topic_info,
                        token_table, R, lambda_step, plot_opts, client_topic_order)
