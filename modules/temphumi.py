#!/usr/bin/python3
import cherrypy
import time
import config

# Icons
tea_temp_icon = 'https://bastart.spoton.cz/static/img/temperature_icon.png'
tea_hum_icon = 'https://bastart.spoton.cz/static/img/humidity_icon.png'
tea_bat_icon = 'https://bastart.spoton.cz/static/img/temperature_icon.png'


class PuerhInfo(object):
    @cherrypy.expose
    def index(self):
        header = config.read_html('header', config._templates)
        menu_raw = config.read_html('top_menu', config._templates)
        menu = menu_raw.format(energy = '', weather = '',
                               status = '', temphumi = 'active')
        body = self.body()
        footer = config.read_html('footer', config._templates)
        result = header\
               + menu\
               + body\
               + footer
        return result

    def currentState(self):
        self.influx_weather_client = config.Conf.influx_weather_client
        query1 = "SELECT time, humidity, temperature, battery, type from usense"
        tea_var = "WHERE type = 'Tea'"
        query2 = "AND time < NOW() - 10m ORDER BY time DESC LIMIT 1"
        tea_query = "{} {} {}".format(query1, tea_var, query2)

        results = self.influx_weather_client.query(tea_query)


        # returned is a list, in this case, we just need one value [0]
        result_tea_temp = [temperature for temperature in results][0][0]
        result_tea_hum = [humidity for humidity in results][0][0]
        result_tea_bat = [battery for battery in results][0][0]
        # Put the time to a human readable format, strip nanosecs
        time_stamp = time.strptime(result_tea_temp['time'].split('.')[0],
                                       "%Y-%m-%dT%H:%M:%S")
        result = {}
        
        result.update({"time": time_stamp})
        result.update({'temperature': result_tea_temp['temperature']})
        result.update({'humidity': result_tea_hum['humidity']})
        result.update({'battery': result_tea_bat['battery']})

        return result

    def body(self):
        admin_preformat = config.read_html('temphumi_admin', config._templates)
        current_temphumi = self.currentState()
        admin_html = admin_preformat.format(
            timestamp = time.strftime("%d.%m.%Y %H:%M:%S",
                                        current_temphumi['time']),
            temp_value = current_temphumi['temperature'],
            hum_value = current_temphumi['humidity'],
            bat_value = round(current_temphumi['battery'] / 1023, 2),
            tea_temp_icon = tea_temp_icon,
            tea_hum_icon = tea_hum_icon,
            tea_bat_icon = tea_bat_icon)
        return admin_html
