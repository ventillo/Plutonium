#!/usr/bin/python3
import cherrypy
import time
import config

# Icons
base_url = 'https://bastart.spoton.cz/static'
fs_wind_icon = base_url + '/img/wind_icon.png'
fs_pressure_icon = base_url + '/img/pressure_icon.png'
fs_in_temperature_icon = base_url + '/img/inside_temp_icon.png'
fs_out_temperature_icon = base_url + '/img/outside_temp_icon.png'
fs_windgust_icon = base_url + '/img/wind_gust_icon.png'
fs_winddirection_icon = base_url + '/img/wind_direction_icon.png'


class WeatherInfo(object):
    @cherrypy.expose
    def index(self):
        header = config.read_html('header', config._templates)
        menu_raw = config.read_html('top_menu', config._templates)
        menu = menu_raw.format(energy = '', weather = 'active',
                               status = '', temphumi = '')
        body = self.body()
        footer = config.read_html('footer', config._templates)
        result = header\
               + menu\
               + body\
               + footer
        return result

    def winddirName(self, direction):
        '''
        Function to get energy readings from InfluxDB.

        returns:
            dict(): {"last": str(last_entry),
                     "details": list(detailed_table),
                     "watthours": str(watthours)}
        '''
        if 10.5 <= direction < 34.5:
            result = "NNE"
        elif 34.5 <= direction < 58.5:
            result = "NE"
        elif 58.5 <= direction < 82.5:
            result = "ENE"
        elif 82.5 <= direction < 106.5:
            result = "E"
        elif 106.5 <= direction < 130.5:
            result = "ESE"
        elif 130.5 <= direction < 154.5:
            result = "SE"
        elif 154.5 <= direction < 178.5:
            result = "SSE"
        elif 178.5 <= direction < 202.5:
            result = "S"
        elif 202.5 <= direction < 226.5:
            result = "SSW"
        elif 226.5 <= direction < 250.5:
            result = "SW"
        elif 250.5 <= direction < 274.5:
            result = "W"
        elif 274.5 <= direction < 298.5:
            result = "WNW"
        elif 298.5 <= direction < 322.5:
            result = "NW"
        elif 322.5 <= direction < 346.5:
            result = "NNW"
        elif 346.5 <= direction <= 359.9 or 0 < direction < 10.5:
            result = "N"
        elif direction == 0:
            result = "ERROR, windvan broken"
        else:
            result = "NaN"
        return result

    def LastKnownState(self):
        '''
        Function to get energy readings from InfluxDB.

        returns:
            dict(): {"last": str(last_entry),
                     "details": list(detailed_table),
                     "watthours": str(watthours)}
        '''
        self.influx_weather_client = config.Conf.influx_weather_client

        # General query
        query1 = "SELECT time, value FROM wind WHERE type = "
        query2 = "AND time > NOW() - 5m ORDER BY time DESC LIMIT 1"

        # now parse the tag in the middle of the two q from above
        wind_speed_q = "{} '{}' {}".format(query1, "speed", query2)
        wind_direction_q = "{} '{}' {}".format(query1, "direction", query2)
        wind_gust_q = "{} '{}' {}".format(query1, "windgust", query2)
        hum_ext_q = "SELECT time, humidity FROM temphumi WHERE type = 'external' {}".format(query2)
        hum_int_q = "SELECT time, humidity FROM temphumi WHERE type = 'internal' {}".format(query2)
        press_q = "SELECT time, pressure FROM temphumi WHERE type = 'adjusted' {}".format(query2)
        presr_q = "SELECT time, pressure FROM temphumi WHERE type = 'raw' {}".format(query2)
        t_ext_q = "SELECT time, temperature FROM temphumi WHERE type = 'external' {}".format(query2)
        t_int_q = "SELECT time, temperature FROM temphumi WHERE type = 'internal' {}".format(query2)


        # the actual query to DB
        wind_speed = self.influx_weather_client.query(wind_speed_q)
        wind_direction = self.influx_weather_client.query(wind_direction_q)
        wind_gust = self.influx_weather_client.query(wind_gust_q)
        hum_ext = self.influx_weather_client.query(hum_ext_q)
        hum_int = self.influx_weather_client.query(hum_int_q)
        press = self.influx_weather_client.query(press_q)
        presr = self.influx_weather_client.query(presr_q)
        t_ext = self.influx_weather_client.query(t_ext_q)
        t_int = self.influx_weather_client.query(t_int_q)


        # returned is a list, in this case, we just need one value [0]
        result_windspeed = [speed for speed in wind_speed][0][0]
        result_winddir = [direction for direction in wind_direction][0][0]
        result_windgust = [gust for gust in wind_gust][0][0]
        result_hum_int = [y for y in hum_int][0][0]
        result_t_int = [c for c in t_int][0][0]
        result_press = [z for z in press][0][0]
        result_presr = [a for a in presr][0][0]
        result_t_ext = [b for b in t_ext][0][0]
        result_hum_ext = [x for x in hum_ext][0][0]

        # Put the time to a uhman readable format, strip nanosecs
        time_stamp = time.strptime(result_windspeed['time'].split('.')[0],
                                       "%Y-%m-%dT%H:%M:%S")
        result = {}

        # Construct the result to return
        result.update({"time": time_stamp})
        result.update({"speed": round(result_windspeed['value'], 1)})
        result.update({"direction": round(result_winddir['value'], 1)})
        result.update({"windgust": round(result_windgust['value'], 1)})
        result.update({"humidity_ext": round(result_hum_ext['humidity'], 1)})
        result.update({"humidity_int": round(result_hum_int['humidity'], 1)})
        result.update({"pressure": round(result_press['pressure'], 1)})
        result.update({"pressure_raw": round(result_presr['pressure'], 1)})
        result.update({"temp_ext": round(result_t_ext['temperature'], 1)})
        result.update({"temp_int": round(result_t_int['temperature'], 1)})
        return result


    def body(self):
        admin_preformat = config.read_html('weather_admin', config._templates)
        current_weather = self.LastKnownState()
        admin_html = admin_preformat.format(
                timestamp = time.strftime("%d.%m.%Y %H:%M:%S",
                                        current_weather['time']),
                w_speed_icon = fs_wind_icon,
                w_speed_km = current_weather['speed'],
                w_speed_ms = round(current_weather['speed'] / 3.6, 1),
                w_gust_icon = fs_windgust_icon,
                w_gust_km = current_weather['windgust'],
                w_gust_ms = round(current_weather['windgust'] / 3.6, 1),
                w_dir_icon = fs_winddirection_icon,
                w_dir_name = self.winddirName(current_weather['direction']),
                w_dir_deg = current_weather['direction'],
                out_temp_icon = fs_out_temperature_icon,
                out_temp = current_weather['temp_ext'],
                in_temp_icon = fs_in_temperature_icon,
                in_temp = current_weather['temp_int'],
                pressure_icon = fs_pressure_icon,
                pressure = current_weather['pressure'],
                raw_pressure = current_weather['pressure_raw']
                )
        return admin_html
