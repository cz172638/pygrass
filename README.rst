+++++++
pygrass
+++++++

Since in the 2006 GRASS developers start to adopt python for the new GUI, python becoming more and more important and developers plan to convert all the bash script in to python for the next major release GRASS 7.

``pygrass`` want to improve integration between GRASS and python, make the use of python under GRASS more consistent with the language itself and make the GRASS scripting and programming activity easier and more natural to the final users.

This project has been funded with support from the google Summer of Code 2012.


Download
========

It is possible to download ``pygrass`` from the `dowload <>` page of the `website <>`, or download directly cloning the repository: ::

    $ git clone https://code.google.com/p/pygrass/


Installing
==========

Use ``setup.py`` possibly inside a `virtualenv <http://pypi.python.org/pypi/virtualenv/>`::

    $ python setup.py install


Reading the docs
================

To read the docs locally, it is necessary to change directory and run the make command to produce the output (html, pdf, epub). ::

    $ cd docs
    $ make html

Then, direct your browser to ``_build/html/index.html``.

Or read them online at <http://www.ing.unitn.it/~zambelli/projects/pygrass//>.


Testing
=======

To run the tests with the interpreter available as ``python``, use::

    make test

If you want to use a different interpreter, e.g. ``python3``, use::

    PYTHON=python3 make test


Contributing
============

Send wishes, comments, patches, etc. to <grass-dev@lists.osgeo.org>.


Support and Documentation
=========================


I you find any issue please open a new `issue <http://code.google.com/p/pygrass/issues>`_
and/or write to the `grass-dev mailing list <http://lists.osgeo.org/listinfo/grass-dev>`_.



License
=======

`GNU GPL v2 <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>`_


Authors
=======

``pygrass`` is made available by `Pietro Zambelli`_ during the
`Google Summer of Code 2012`_.

Mentor of the project is Sören Gebbert.
Co-Mentors are:
    * Martin Landa;
    * Markus Metz;
    * Markus Netler;
    * Luca Delucchi.

.. _Pietro Zambelli: http://www.ing.unitn.it/~zambelli
.. _Google Summer of Code 2012: http://google-melange.appspot.com/gsoc/proposal/review/google/gsoc2012/zarch/1


Credits
=======

- `GRASS`_
- `Numpy`_
- `PostgreSQL`_
- `psycopg2`_
- `Distribute`_
- `Buildout`_
- `modern-package-template`_

.. _GRASS: http://grass.osgeo.org/
.. _Numpy: http://numpy.scipy.org/
.. _PostgreSQL: http://www.postgresql.org/
.. _Buildout: http://www.buildout.org/
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _`modern-package-template`: http://pypi.python.org/pypi/modern-package-template
