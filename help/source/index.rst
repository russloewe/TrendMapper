.. TrendMapper documentation master file, created by
   sphinx-quickstart on Sun Feb 12 17:11:03 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to TrendMapper's documentation!
============================================

Trend Mapper is a QGIS Python plugin that performs linear regression
analysis for a vector point layer for sets of features grouped by 
unique values along a chosen field.

Source code located at `github.com/russloewe/TrendMapper <https://github.com/russloewe/TrendMapper>`_ .

Trend Mapper
=============

.. autoclass:: trend_mapper.TrendMapper
    :members: run, process, stp
    
    
Trend Mapper Process
====================
    
.. autoclass:: trend_mapper.TrendMapperProcess
    :members:
    
    
Trend Mapper Tools
==================

A suite of tools for retrieving data from the QGIS interface and for making
new features and layers
 
.. automodule:: trend_mapper_tools
    :members:

Trend Mapper Dialog
===================

.. autoclass:: trend_mapper.TrendMapperDialog
    :members:
    
Analysis Functions
==================
   
.. automodule:: analysis
    :members:

    
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

