.. Plutonium reporter documentation master file, created by
   sphinx-quickstart on Wed Apr  3 15:53:15 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==============================================
DOC: Plutonium reporter
==============================================

.. toctree::
    :maxdepth: 3
    :caption: Contents:
    
    introduction


Scope
=====
This document covers the **software part** of the reporter, although it consists
of a multitude of hw technologies, please keep that in mind.

Purpose
========

Delivering aggregated and comprehensive representation of data-value pairs
in such a way, that even a complete idiot can read them. *This project is
created by AND for me.*

In short, this application spins up a web server and on its address plots and
displays values gathered from various sources.

An example granted: https://bastart.spoton.cz

Sources
--------

The sources for feeding the **Plutonium** include:

- Davis Vantage vue weather station (with a couple HW mods)
- Victron MPPT solar converter (Utilizing the Victron Direct RS232 protocol)
- CPU, MEM, DISK, (W)LAN statistics, plotted
- Custom ESP8266 data loggers
    - Temp / Humidity + battery logging
    - Current monitoring for LED lighting

Discrepancies and hardware dependencies
---------------------------------------
Obviously, all the monitoring cannot be done without proper HW equipment.
Although this server is primarily aimed at use on a Raspberry PI, it can be
installed on an old notebook, or similar, as the platform is Python3 and thus
independent of the OS.

Solar / MPPT
++++++++++++
- Victron MPPT solar charge controller (Bluesolar)
- RS232 -> USB or similar, to get the data to RasPi

Davis Vantage Vue
+++++++++++++++++
- Obviously the Davis Vantage Vue weather station
- The CC1101 / wireless version
- arduino mini / Uno @ 3.3V
- CC1101 receiver with a couple other components

RasPI statistics
++++++++++++++++
- Just the RasPI

ESP8266 stuff
+++++++++++++
- basically anything that can feed into the influxDB.

Indices and tables
===================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
