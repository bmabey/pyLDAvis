pyLDAvis
========

Python package for interactive topic model visualization.
This is a port of the fabulous `R package <https://github.com/cpsievert/LDAvis>`__ by Carson Sievert and Kenny Shirley.

.. figure:: http://www2.research.att.com/~kshirley/figures/ldavis-pic.png
   :alt: LDAvis icon

**pyLDAvis** is designed to help users interpret the topics in a topic model that has been fit to a corpus of text data. The package extracts information from a fitted LDA topic model to inform an interactive web-based visualization.

The visualization is intended to be within an IPython notebook but can also be saved to a stand-alone HTML file for easy sharing.

|version status| |downloads| |build status| |docs|

Installation
~~~~~~~~~~~~~~~~~~~~~~

-  Stable version using pip:

::

    pip install pyldavis

-  Development version on GitHub

Clone the repository and run ``python setup.py``

Video demos
~~~~~~~~~~~

Carson Sievert created a video demoing the R package. The visualization is the same and so it applies equally to pyLDAvis:

-  `Visualizing & Exploring the Twenty Newsgroup Data <http://stat-graphics.org/movies/ldavis.html>`__

More documentation
~~~~~~~~~~~~~~~~~~

To read about the methodology behind pyLDAvis, see `the original
paper <http://nlp.stanford.edu/events/illvi2014/papers/sievert-illvi2014.pdf>`__,
which was presented at the `2014 ACL Workshop on Interactive Language
Learning, Visualization, and
Interfaces <http://nlp.stanford.edu/events/illvi2014/>`__ in Baltimore
on June 27, 2014.



.. |version status| image:: https://pypip.in/v/pyLDAvis/badge.png
   :target: https://pypi.python.org/pypi/pyLDAvis
.. |downloads| image:: https://pypip.in/d/pyLDAvis/badge.png
   :target: https://pypi.python.org/pypi/pyLDAvis
.. |build status| image:: https://travis-ci.org/bmabey/pyLDAvis.png?branch=master
   :target: https://travis-ci.org/bmabey/pyLDAvis
.. |docs| image:: https://readthedocs.org/projects/pyldavis/badge/?version=latest
   :target: https://pyLDAvis.readthedocs.org
