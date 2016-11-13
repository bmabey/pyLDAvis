pyLDAvis
========

Python library for interactive topic model visualization.
This is a port of the fabulous `R package <https://github.com/cpsievert/LDAvis>`__ by Carson Sievert and Kenny Shirley.

.. figure:: http://www.kennyshirley.com/figures/ldavis-pic.png
   :alt: LDAvis icon

**pyLDAvis** is designed to help users interpret the topics in a topic model that has been fit to a corpus of text data. The package extracts information from a fitted LDA topic model to inform an interactive web-based visualization.

The visualization is intended to be used within an IPython notebook but can also be saved to a stand-alone HTML file for easy sharing.

|version status| |build status| |docs|

Installation
~~~~~~~~~~~~~~~~~~~~~~

-  Stable version using pip:

::

    pip install pyldavis

-  Development version on GitHub

Clone the repository and run ``python setup.py``

Usage
~~~~~~~~~~~~~~~~~~~~~~

The best way to learn how to use **pyLDAvis** is to see it in action.
Check out this `notebook for an overview <http://nbviewer.ipython.org/github/bmabey/pyLDAvis/blob/master/notebooks/pyLDAvis_overview.ipynb>`__.
Refer to the `documentation <https://pyLDAvis.readthedocs.org>`__ for details.

For a concise explanation of the visualization see this
`vignette <http://cran.r-project.org/web/packages/LDAvis/vignettes/details.pdf>`__ from the LDAvis R package.

Video demos
~~~~~~~~~~~

Ben Mabey walked through the visualization in this short talk using a Hacker News corpus:

-  `Visualizing Topic Models <https://www.youtube.com/watch?v=tGxW2BzC_DU&index=4&list=PLykRMO7ZuHwP5cWnbEmP_mUIVgzd5DZgH>`__
-  `Notebook and visualization used in the demo <http://nbviewer.ipython.org/github/bmabey/hacker_news_topic_modelling/blob/master/HN%20Topic%20Model%20Talk.ipynb>`__
-  `Slide deck <https://speakerdeck.com/bmabey/visualizing-topic-models>`__


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




.. |version status| image:: https://img.shields.io/pypi/v/pyLDAvis.svg
   :target: https://pypi.python.org/pypi/pyLDAvis
.. |build status| image:: https://travis-ci.org/bmabey/pyLDAvis.png?branch=master
   :target: https://travis-ci.org/bmabey/pyLDAvis
.. |docs| image:: https://readthedocs.org/projects/pyldavis/badge/?version=latest
   :target: https://pyLDAvis.readthedocs.org
