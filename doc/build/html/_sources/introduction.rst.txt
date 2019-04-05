.. Plutonium reporter documentation master file, created by
   sphinx-quickstart on Wed Apr  3 15:53:15 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Introduction to Plutonium
+++++++++++++++++++++++++

.. toctree::
    :maxdepth: 5
    :caption: Contents:

Directory structure
===================
Following structure is applied to this project. Some directories are
minified in this view on purpose.
::
    .
    ├── chttpd.py
    ├── config
    │   └── plutonium.ini
    ├── config.py
    ├── doc ... (documentation in sphinx)
    ├── index.py
    ├── localdeploy.sh
    ├── modules
    │   ├── dynamic.py
    │   ├── status.py
    │   ├── temphumi.py
    │   ├── voltage.py
    │   └── weather.py
    ├── static
    │   ├── css
    │   │   ├── bootstrap.css
    │   │   └── dygraph.css ...
    │   ├── img
    │   │   ├── battery_0.png ...
    │   └── js
    │       ├── solar_graph.js
    │       ├── status_graph.js
    │       ├── temphum_graph.js
    │       └── weather_graph.js ...
    ├── templates
    │   ├── footer.html
    │   ├── header.html
    │   ├── landing_page.html
    │   ├── status_admin.html
    │   ├── temphumi_admin.html
    │   ├── top_menu.html
    │   ├── voltage_admin.html
    │   └── weather_admin.html
    └── TODO.txt

CherryPy configuration (config.py)
==================================
Configuration is stored in a separate file statically, so each submodule can
load the same configuration. This should be variables, that are project-wide.

CherryPy configuration file (plutonium.ini)
-------------------------------------------
Configuration file, .ini style. Option = value. File resides in ./config
directory. It is read by confi.py and parsed into a dict(), available
throughout the project.
::
    _server_protocol = https
    _server_name = bastart.spoton.cz
    _server_port = 80
    _server_bind_ip = 0.0.0.0
    _influx_host = localhost
    _influx_port = 8086
    _influx_user = pi
    _influx_pwd = password
    _influx_weather_db = weather_v2
    _influx_status_db = status
    _influx_voltage_db = voltage
    _influx_IoT_db = weather_v2

Configuration classes and functions
------------------------------------
.. automodule:: config
    :members:

CherryPy server (chttpd.py)
===========================
The server uses CherryPy module. For more information, please consult the
Cherrypy documentation.

CHTTPD.py is also the executable, that can be launched as a standalone
application by simply typing ./chttpd.py, or python3 chttpd.py

.. automodule:: chttpd
    :members:

Modules and web paths
---------------------

Modules are located in the `modules` directory, hence the imports from a
subdirectory
::
    from modules import voltage
    from modules import weather
    from modules import dynamic
    from modules import status
    from modules import temphumi

As can be seen, each class / module is mounted under a specific web path. This
is the preferred way of future expansion modules.
::
    cherrypy.tree.mount(voltage.EnergyInfo(), "/", conf)
    cherrypy.tree.mount(voltage.EnergyInfo(), "/energy", conf)
    cherrypy.tree.mount(weather.WeatherInfo(), "/weather", conf)
    cherrypy.tree.mount(status.StatusInfo(), "/status", conf)
    cherrypy.tree.mount(dynamic.Expose(), "/data", conf)
    cherrypy.tree.mount(temphumi.PuerhInfo(), "/temphumi", conf)

Index (index.py)
================
Reserved for future use. Currently not displayed, as the EnergyInfo() class is
mounted under root(/) of the web, defined in chttpd.py
::
    cherrypy.tree.mount(voltage.EnergyInfo(), "/", conf)

.. automodule:: index
    :members:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
