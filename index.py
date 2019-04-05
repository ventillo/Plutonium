#!/usr/bin/python3
import cherrypy
import config

static_dir = '/templates/' # Needs to have trailing and leading slash '/'

class landingPage(object):
    '''Base Index constructor and expose function'''
    @cherrypy.expose
    def index(self):
        header = config.read_html('header', static_dir)
        menu_raw = config.read_html('top_menu', static_dir)
        menu = menu_raw.format(energy = '', weather = '',
                               status = '', temphumi = '')
        body = self.body()
        footer = config.read_html('footer', static_dir)
        result = header\
               + menu\
               + body\
               + footer
        return result

    def body(self):
        admin_preformat = config.read_html('landing_page', static_dir)
        admin_html = admin_preformat
        return admin_html
