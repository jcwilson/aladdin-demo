##########
Components
##########

**The** ``lamp.json`` **file for this project:**

.. Pull this file in from outside of the docs/ directory
.. literalinclude:: ../../lamp.json
  :language: JSON

***
api
***

TODO include OpenAPI docs here

****
init
****

The image used for init containers.

********
commands
********

One can run several ``aladdin cmd`` commands with this project.

.. todo:: Document them here.

***
lab
***

This project makes a `Jupyter Lab`_ instance available in local and KDEV deployments. It has access to all of the other components' libraries and application code, so you can use it to experiment with any part of the project functionality in an exploratory fashion.

.. _Jupyter Lab: https://jupyterlab.readthedocs.io/en/stable/

******
shared
******

This is library code that is used by other components. In our case the *api*, *init* and *commands* components utilize the elasticsearch and redis utility code.

****************************
pipeline and pipeline-flake8
****************************

These components contain tools for performing CI tasks such as static code analysis, style checks, unit tests, load tests and so on.

We had to split these into two components due to a dependency version conflict between the ``prospector`` and ``flake8`` packages. We can see about merging these components in the future once those tools can be reconciled.
