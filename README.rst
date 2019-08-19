======================================
Desire2Learn Client Library for Python
======================================

Our Python client library SDK is currently in experimental form. Currently, we
use this libary as a quick way to rapidly, and interactively, prototype or
hand-test back-end LMS services for trouble shooting purposes: it's not intended
for rigorous production use.

**Feedback and contributions welcome**. If you have any feedback or additions
you'd like to make to the Python client library, please feel free to
contact Valence@Desire2Learn.com to coordinate with our development team.

.. note::

   You can find the latest version of this documentation, and related
   topics in our 
   `Valence API documentation <http://docs.valence.desire2learn.com/clients/python/index.html>`_.

Installation
============
You can find the 
`latest build <http://code.google.com/p/desire2learn-valence/downloads/list?q=label:pythonlatestclient>`_
of the client library SDK on our repository download page.

**Dependencies**. In order to use the Python client library SDK, you'll need to
first ensure you have a working Python development environment:

* Python 3 (the reference environment uses Python 3.2).

* The `Requests Python package <http://docs.python-requests.org/en/latest/index.html>`_
  gets used in our :py:mod:`service <d2lvalence.service>` module to make the
  calls through to the back-end service, and in our :py:mod:`auth <d2lvalence.auth>`
  module so that you can use a calling user context object as an authentication
  helper for Requests.

* The `Bottle Python package <http://bottlepy.org/docs/dev/>`_ if you want to
  use the samples available in conjunction with this client library (not a
  dependency for the client library itself).


Modules
=======
The Python library divides functionality into a number of modules:

**Authentication**. The :py:mod:`d2lvalence.auth` module provides assistance for
the authentication needed to invoke Valence APIs. You use the module's functions
(and perhaps also classes) to create a 
:py:class:`calling user context <d2lvalence.auth.D2LUserContext>` object that
you can then employ in conjunction with the Reqeusts package as an
authentication helper.

**Data**. The :py:mod:`d2lvalence.data` module provides classes to encapsulate
the JSON data structures passed back and forth through the Valence APIs. All the
classes inherit from a :py:class:`D2LStructure generic base class
<d2lvalence.data.D2LStructure>`.

Note that currently we drive additions to the `data` module by the needs of our
samples and ongoing testing: it does not cover all the structures present in the
Valence API.

**Service**. The :py:mod:`d2lvalence.service` module contains a suite of helper
functions you can use to make Valence API calls and partially digest the data
results passed back. In general, the data passed back by a service function is
either a pre-defined class inheriting from :py:class:`D2LStructure
<d2lvalence.data.D2LStructure>`, or one or more dictionaries formed from the
retrieved JSON data.
