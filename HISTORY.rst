.. :changelog:

History
-------

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
