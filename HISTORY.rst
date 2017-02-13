.. :changelog:

History
-------

2.1.1 (2017-02-13)
---------------------

* Fix `gensim` module to work with a sparse corpus #82.

2.1.0 (2016-06-30)
---------------------

* Added missing dependency on `scipy`.
* Fixed term sorting that was incompatible with pandas 0.19.x.

2.0.0 (2016-06-30)
---------------------

* Removed dependency on `scikit-bio` by adding an internal PCoA implementation.
* Added helper functions for scikit-learn LDA model! See the new notebook for details.
* Extended gensim helper functions to work with HDP models.
* Added scikit-learn's Multi-dimensional scaling as another MDS option when scikit-learn is installed.

1.5.1 (2016-04-15)
---------------------

* Add sort_topics option to prepare function to allow disabling of topic re-ordering.


1.5.0 (2016-02-20)
---------------------

* Red Bar Width bug fix

 In some cases, the widths of the red topic-term bars did not decrease (as they should have) from term \#1 to
 term \#R under the relevance ranking with $\lambda = 1$. In other words, when $\lambda = 1$, there were topics
 in which a narrow red bar was displayed above a wider red bar, which should never happen. The issue had to do
 with the way topic-term bar widths are computed, and is discussed in detail in #32.


In the end, we implemented a quick fix in which we compute term frequencies implicitly, rather than using those
supplied in the createJSON() function. The upside is that the red bar widths are now explicitly controlled to
produce the correct visualization. The downside is that the blue bar widths do not necessarily match the
user-supplied term frequencies exactly -- in fact, the new version of LDAvis ignores the user-supplied term
frequencies entirely. In a few experiments, the differences are small, and decrease (as a proportion of the true
term frequencies) as the true term frequencies increase.



1.4.1 (2016-01-31)
---------------------

* Included requirements.txt in MANIFEST to (hopefully) fix bad release.

1.4.0 (2016-01-31)
---------------------

* Updated to newest version of skibio for PCoA mds.
* requirements.txt cleanup
* New 'tsne' option for prepare, see docs and notebook for more info.


 1.3.5 (2015-12-18)
---------------------

* Add explicit version info for scikit-bio since the API has changed.


1.3.4 (2015-11-16)
---------------------

* Gensim Python typo fix in imports. :/

1.3.3 (2015-11-13)
---------------------

* Gensim Python 2.x fix for absolute imports.

1.3.2 (2015-11-09)
---------------------

* Gensim prepare 25% speed increase, thanks @mattilyra!
* Pandas deprecation warnings are now gone.
* Pandas v0.17 is now being used.

1.3.1 (2015-11-02)
---------------------

* Updates gensim and other logic to be python 3 compatible.

1.3.0 (2015-08-20)
---------------------

* Fixes gensim logic and makes it more robust.
* Faster graphlab processing.
* kargs for gensim and graphlab are passed down to underlying prepare function.
* Requires recent version of pandas to avoid problems with our use of the newer `DataFrame.to_dict` API.

1.2.0 (2015-06-13)
---------------------

* Updates gensim logic to be clearer and work with Python 3.x.

1.1.0 (2015-06-02)
---------------------

* Fixes bug with GraphLab function that was producing bogus visualizations.

1.0.0 (2015-05-29)
---------------------

* First release on PyPI. Faithful port of R version with IPython support and helper functions for GraphLab & gensim.
