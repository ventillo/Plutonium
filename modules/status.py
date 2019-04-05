#!/usr/bin/python3
import cherrypy
import influxdb
import time
import datetime
import psutil
import config

# Icons
fs_sol_icon = 'https://bastart.spoton.cz/static/img/iss_solar_icon.png'
fs_cap_icon = 'https://bastart.spoton.cz/static/img/iss_capacitor_icon.png'


class StatusInfo(object):
    @cherrypy.expose
    def index(self):
        header = config.read_html('header', config._templates)
        menu_raw = config.read_html('top_menu', config._templates)
        menu = menu_raw.format(energy = '', weather = '',
                               status = 'active', temphumi = '')
        body = self.body()
        footer = config.read_html('footer', config._templates)
        result = header\
               + menu\
               + body\
               + footer
        return result

    def LastKnownState(self):
        '''
        Function to get energy readings from InfluxDB.

        returns:
            dict(): {"time": str(time_stamp),
                     "solar": solar,
                     "cap": cap}
        '''

        influx_status_client = config.Conf.influx_status_client
        #Not from DB, actual numbers
        uptime_since = datetime.datetime.strftime(
            datetime.datetime.fromtimestamp(int(psutil.boot_time())),
            "%Y-%m-%d %H:%M:%S"
        )

        # General query
        query1 = "SELECT time, voltage FROM iss WHERE type = "
        query2 = "ORDER BY time DESC LIMIT 1"

        # now parse the tag in the middle of the two q from above
        solar_q = "{} '{}' {}".format(query1, "solar", query2)
        cap_q = "{} '{}' {}".format(query1, "capcaitor", query2)

        # the actual query to DB
        solar = influx_status_client.query(solar_q)
        cap = influx_status_client.query(cap_q)

        # returned is a list, in this case, we just need one value [0]
        result_solar = [sol for sol in solar][0][0]
        result_cap = [cap_ for cap_ in cap][0][0]

        # Put the time to a uhman readable format, strip nanosecs
        time_stamp = time.strptime(result_solar['time'].split('.')[0],
                                       "%Y-%m-%dT%H:%M:%S")
        result = {}

        # Construct the result to return
        result.update({"time": time_stamp})
        result.update({"solar": round(result_solar['voltage'], 1)})
        result.update({"cap": round(result_cap['voltage'], 1)})
        result.update({"uptime": uptime_since})
        return result


    def body(self):
        admin_preformat = config.read_html('status_admin', config._templates)
        current_status = self.LastKnownState()
        admin_html = admin_preformat.format(
                timestamp = time.strftime("%d.%m.%Y %H:%M:%S",
                                        current_status['time']),
                sol_icon = fs_sol_icon,
                cap_icon = fs_cap_icon,
                sol_value = round(current_status['solar'] / 100, 2),
                cap_value = current_status['cap'],
                uptime = current_status['uptime']
                )
        return admin_html
