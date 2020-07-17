
Documentation of structDataset
==============================

.. image:: https://travis-ci.org/structDataset/documentation.svg?branch=master
    :target: https://travis-ci.org/structDataset/documentation
    :alt: Travis-Ci Status

.. image:: https://readthedocs.org/projects/structdataset/badge/?version=latest
    :target: http://structdataset.readthedocs.io
    :alt: Documentation Status

.. image:: https://beta.mybinder.org/badge.svg
    :target: https://beta.mybinder.org/v2/gh/structDataset/documentation/master?filepath=notebooks
    :alt: My Binder - Notebooks

This repository contains the source files for the documentation of
`structDataset`_ which can be found under this link:
http://structdataset.readthedocs.io/.

.. _structDataset: https://github.com/structDataset/data

The repository contains an ``notebooks`` folder at the top which includes the
notebooks used for sections in the documentation. They should be well prepared
and enable us to make the documentation more illustrative whenever it is
needed.

The ``docs`` folder contains all the files needed for a documentation with
sphinx. The main new feature is that you can add notebooks to the specific
folder which uses data from ``data/..`` and additional PDFs from
``documents/..``. In addition to that, you have to include the notebook name in
``docs/conf.py`` relative to the ``_temp`` folder. This temporary folder is
created while running ``make html`` in the documentation folder.

The folder containing datasets is located in ``data/..``. I am not sure
whether the current specialization is necessary, but we will see it in the
future.

The ``documents`` folder contains PDFs and the like of it.
