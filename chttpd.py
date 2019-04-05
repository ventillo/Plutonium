#!/usr/bin/python3
import os
import cherrypy

import index
from modules import voltage
from modules import weather
from modules import dynamic
from modules import status
from modules import temphumi
import config


def main_server_loop():
    ''' Master http server - the main executable / daemon
    
    Contains basic server settings and how the sub-modules
    are called and mounted to their respective paths

    Args:
        *None*

    Sets:
        *server_config:*    dict(), updates cherrypy.config
        *conf:*             dict(), see Cherrypy docs for more
        *cherrypy.config:*  dict(), see Cherrypy docs for more
        
    Returns:
        *N/A*

    Raises:
        *Exception*         If server is unable to start
    
    '''
    server_config={
        'server.socket_host': config.Conf.val['_server_bind_ip'],
        'server.socket_port': config.Conf.val['_server_port']
    }
    cherrypy.config.update(server_config)
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(config.SCRIPT_PATH + '/')
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }

    cherrypy.tree.mount(voltage.EnergyInfo(), "/", conf)
    cherrypy.tree.mount(voltage.EnergyInfo(), "/energy", conf)
    cherrypy.tree.mount(weather.WeatherInfo(), "/weather", conf)
    cherrypy.tree.mount(status.StatusInfo(), "/status", conf)
    cherrypy.tree.mount(dynamic.Expose(), "/data", conf)
    cherrypy.tree.mount(temphumi.PuerhInfo(), "/temphumi", conf)
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == '__main__':
    try:
        main_server_loop()
    except Exception as e:
        raise e
