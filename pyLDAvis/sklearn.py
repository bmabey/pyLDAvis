import pandas as pd
import funcy as fp
from . import prepare as vis_prepare

def _extract_data(docs, vect, lda):
  
    #LDA scikit-learn implementation seems to have buggy code.
    #Topic_term_dists and doc_topic_dists isn't accummulated to 1.
    #Hence norm function implemented to normalize the distributions.
    norm = lambda data: pd.DataFrame(data).div(data.sum(1),axis=0).values
    vected = vect.fit_transform(docs)
    doc_topic_dists = norm(lda.fit_transform(vected))
  
    return lda,vect, dict(
                      doc_lengths = docs.str.len(),
                      vocab = vect.get_feature_names(),
                      term_frequency = vected.sum(axis=0).tolist()[0],
                      topic_term_dists = norm(lda.components_),
                      doc_topic_dists = doc_topic_dists)

def prepare(docs, vect, lda, **kwargs):
    """Create Prepared Data from sklearn's vectorizer and Latent Dirichlet
    Application.

    Parameters
    ----------
    docs : Pandas Series.
        Documents to be passed as an input.
    vect : Scikit-Learn Vectorizer (CountVectorizer,TfIdfVectorizer).
        vectorizer to convert documents into matrix sparser
    lda  : sklearn.decomposition.LatentDirichletAllocation.
        Latent Dirichlet Allocation

    **kwargs: Keyword argument to be passed to pyLDAvis.prepare()


    Returns
    -------
    prepared_data : PreparedData
          the data structures used in the visualization


    Example
    --------
    For example usage please see this notebook:
    http://nbviewer.ipython.org/github/bmabey/pyLDAvis/blob/master/notebooks/sklearn.ipynb

    See
    ------
    See `pyLDAvis.prepare` for **kwargs.
    """
  
    opts = fp.merge(_extract_data(docs, vect, lda)[2], kwargs)

    return vis_prepare(**opts)