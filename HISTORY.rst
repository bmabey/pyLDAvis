.. :changelog:

History
-------

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
