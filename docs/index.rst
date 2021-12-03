.. Goodboy 

Goodboy documentation
=====================

**Goodboy** is a Python library for data validation.

.. note::
   This project is under active development.

.. code-block:: python

   >>> from goodboy import DateTime, Dict, Key, Str, validate
   >>> 
   >>> result = validate(
   ...     Dict(keys=[
   ...         Key("name", Str(), required=True),
   ...         Key("birthday", DateTime(), required=True),
   ...     ]), {
   ...         "name": "Neil Young",
   ...         "birthday": "1945-11-12T00:00:00"
   ...     }, typecast=True
   ... )
   >>> 
   >>> result.is_valid 
   True
   >>> result.value
   {'name': 'Neil Young', 'birthday': datetime.datetime(1945, 11, 12, 0, 0)}

Contents:
---------

.. toctree::
   :maxdepth: 2

   getting-started
   reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
