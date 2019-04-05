#!/usr/bin/python3
import cherrypy
import time
import datetime
import json
from pprint import pprint
from cherrypy.lib.httputil import parse_query_string
import config


# Universal variables
height_above_sea_level = 452
variables_known = ["range",
                   "granularity",
                   "start",
                   "end",
                   "type"]
default_variables = {"range": "1h",
                     "granularity": "30s",
                     "end": "1s",
                     "type": "none"}


#------------------------------------------------------------------------------
# Generic Functions
#------------------------------------------------------------------------------

def check_GET(arguments):
    '''Validates html query

    Takes the key-val pairs and evaluates them against those variables, that
    are defined as known to be safe to be parsed.

    Args:
        str(arguments):
        "A string of options to be directly evaluated as a dictionary"

    Returns:
        list(str(variable)):
        "List of strings, occupied by variables validated to be safe"

    '''
    _q = eval(str(arguments))
    keys_to_process = {
        key:_q[key] for key in _q.keys() if key in variables_known}
    resulting_variables = default_variables.copy()
    resulting_variables.update(keys_to_process)
    return resulting_variables


#------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------
class Helper(object):
    def __init__(self):
        '''Helping calculations and functions

        Some generic helpers, that do additional calculations, such as
        percentages, predictions etc.
        '''
        pass

    def pressure_to_std_atm(self, raw_pressure, temperature, hasl):
        a2ts = raw_pressure \
             + ((raw_pressure * 9.80665 * hasl)\
             / (287 * (273 + temperature + (hasl/400))))

        #a2ts = raw_pressure + hasl/10
        return a2ts

    def percentageCalc(self, voltage, system):
        ''' Turns current charge for lead acid batteries into a human
        readable %

        Args:
            float(voltage): Voltage in V
            int(system): nominal system voltage, e.g. 12, 24, 48 etc

        Returns:
            float(percentage): Two decimal state of battery in percentage
        '''
        if system is 12:
            percentage = round(24.5724168782\
                       * voltage * voltage - 521.9890329784 * voltage\
                       + 2771.1828105637, 1)
        elif system is 24:
            percentage = 2.4442 * voltage * voltage\
                      - 82.004 * voltage + 602.91
        elif system is 48:
            # percentage = round((voltage - 46.5) * 18.87, 2)
            percentage = round((voltage - 46.5) * 23.26, 2)
        percentage = 100.00 if percentage > 100.00 else percentage
        percentage = 0 if percentage <= 0 else percentage
        return percentage


class DynamicEnergy(object):
    def __init__(self):
        ''' Parse readings from victron MPPT via Ve.Direct stored in
        InfluxDB
        '''
        self.influx_voltage_client = config.Conf.influx_voltage_client
        self.helpers = Helper()

    def FreshValues(self, **kwargs):
        ''' Get most up-to-date energy reading.

            returns:
                dict(): {'state': str(),
                         'time': 'YYYY-mm-DDTHH:MM:SS.149636706Z',
                         'V_unit1': float(mV),
                         'Psol': fint(W),
                         'V_array': int(mV),
                         'ChCurr': int(mV)}
        '''
        bat_query = "SELECT voltage FROM mppt WHERE type = 'bat'" \
                  + "ORDER BY time DESC LIMIT 1"
        voltage_battery = self.influx_voltage_client.query(bat_query)

        query = "SELECT last(*) "\
              + "FROM mppt "\
              + "WHERE time > now() - 10m "\
              + "GROUP BY type fill(0)"
        state_query = "SELECT voltage,state FROM mppt "\
                    + "ORDER BY time DESC LIMIT 1"
        state_db_result = self.influx_voltage_client.query(state_query)
        state = state_db_result.get_points(measurement='mppt')
        states = state.send(None)
        
        db_result = self.influx_voltage_client.query(query)
        bat = db_result.get_points(measurement='mppt',
                                   tags={'type': 'bat'})
        day = db_result.get_points(measurement='mppt',
                                   tags={'type': 'day'})
        prev_day = db_result.get_points(measurement='mppt',
                                   tags={'type': 'prev_day'})                           
        solar = db_result.get_points(measurement='mppt',
                                   tags={'type': 'solar'})
        total = db_result.get_points(measurement='mppt',
                                   tags={'type': 'total'})                           
        bats = bat.send(None)
        solars = solar.send(None)
        days = day.send(None)
        prev_days = prev_day.send(None)
        totals = total.send(None)

        result = {}
        t_stamp = time.strptime(bats['time'].split('.')[0],
                                       "%Y-%m-%dT%H:%M:%S")
        result['time'] = time.strftime("%d.%m.%Y %H:%M:%S", t_stamp)
        result['state'] = states['state']
        result['ChCurr'] = bats['last_current']
        result['V_array'] = bats['last_voltage']
        result['perc_array'] = self.helpers.percentageCalc(
            bats['last_voltage'],
            48)
        result['Psol'] = solars['last_power']
        result['Vsol'] = solars['last_voltage']
        result['Wh_day'] = days['last_Wh']
        result['Pmax_prev_day'] = days['last_Pmax']
        result['Wh_prev_day'] = prev_days['last_Wh']
        result['Pmax_day'] = prev_days['last_Pmax']
        result['total_Wh'] = totals['last_Wh']

        return result

    def stat_values(self, **kwargs):
        '''Max power and daily generation.
        '''
        # GET variables now set, ready to reference them
        _days = kwargs['days'] + 1
        date = datetime.datetime.strftime(datetime.datetime.now(),"%Y-%m-%d")
        measures = []
        result = []
        query = "SELECT mean(power)*24 as DayWh, max(Pmax) AS Pmax "\
              + "FROM mppt WHERE type='solar' OR type='day' "\
              + "AND time > '{} 00:00:00' - {}d "\
              + "GROUP BY time(1d) fill(previous)"\
              + "ORDER BY time DESC"
        query = query.format(date, _days)
        measure = self.influx_voltage_client.query(query)
        tm = []
        P_max = []
        Wh_sol = []

        for datapoint in measure['mppt']:
            row = []
            tstamp = datapoint['time']
            Pmax = datapoint["Pmax"] - 10
            DayWh = datapoint["DayWh"]
            result.append([tstamp[:10], Pmax, int(DayWh)])
        return result[:-1]

    def solar_graph_data(self, **q):
        '''
        Function to get solar readings from InfluxDB.
        These parsed into a CSV

        yields: csv in raw, text format
            time,V_solar,I_solar,P_solar,V_array
        '''
        mppt_query_str = "SELECT min(power) AS Pmin, max(power) AS Pmax," \
                       + "mean(power) AS Pavg "\
                       + "FROM mppt WHERE type='solar' "\
                       + "AND time > now() - {} "\
                       + "AND time > now() - {} "\
                       + "GROUP BY time({}) fill(previous)"\
                       + "ORDER BY time ASC"
        mppt_query = mppt_query_str.format(q['range'],
                                           q['end'],
                                           q['granularity'])
        query = "SELECT mean(voltage) as Usol, " \
              + "mean(power) as Psol, mean(power)/mean(voltage) as Isol " \
              + "FROM mppt WHERE type='solar' " \
              + "AND time > NOW() - {} " \
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}) fill(previous) ORDER BY time DESC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])                                   
        bat_volt_query = "SELECT mean(voltage) as Varr "\
                       + "FROM mppt WHERE type='bat' "\
                       + "AND time > NOW() - {} "\
                       + "AND time < NOW() - {} "\
                       + "GROUP BY time({}) "\
                       + "FILL(previous) "\
                       + "ORDER BY time ASC"
        bat_volt_query = bat_volt_query.format(q['range'],
                                               q['end'],
                                               q['granularity'])
        bat_measures = self.influx_voltage_client.query(bat_volt_query)
        measures = self.influx_voltage_client.query(query)
        mppt_measures = self.influx_voltage_client.query(mppt_query)
        header = "time,V_solar,I_solar,P_solar,V_array\n"
        yield header
        volt_dict = {}
        for voltage in bat_measures["mppt"]:
            volt_dict.update({voltage["time"]: voltage["Varr"]})
        for datapoint in measures["mppt"]:
            tm = str(datapoint["time"]).strip()
            solar_voltage = str(datapoint["Usol"]).strip()
            solar_current = str(datapoint["Isol"]).strip()
            try:
                solar_power = int(datapoint["Psol"])
                solar_power = solar_power - 11 if solar_power > 11 else 0
                solar_power = str(solar_power).strip()
            except:
                solar_power = str(datapoint["Psol"])
            array_voltage = str(volt_dict[tm])
            yield "{},{},{},{},{}\n".format(tm, solar_voltage,
                                             solar_current, solar_power,
                                             array_voltage)


class Expose(object):
    def __init__(self):
        ''' Default expose class. Takes other classes and exposes them
        via html. GET checks should be defined here.
        Function args and kwargs don't need to be checked, as they are internal
        and not exposed.
        '''
        self.energy = DynamicEnergy()
        self.weather = DynamicWeather()
        self.status = DynamicStatus()
        self.iot = DynamicIoT()
        self.helpers = Helper()
        
    @cherrypy.expose
    def index(self):
        return "Index, MOFO"

    @cherrypy.expose
    def solar_realtime_data(self, **kwargs):
        q = check_GET(kwargs)
        res_type = q['type']
        result = self.energy.FreshValues()
        if res_type == 'json':
            return json.dumps(result)
        else:
            return result
        
    @cherrypy.expose
    def solar_monitor(self, **kwargs):
        q = check_GET(kwargs)
        sol_monitor = self.energy.solar_graph_data(**q)
        return sol_monitor
        
    @cherrypy.expose
    def wind_monitor(self, **kwargs):
        q = check_GET(kwargs)
        wind_monitor = self.weather.wind_graph_data(**q)
        header = "time,Speed,Gusts,Direction\n"
        yield header
        for speed, gust, direction in zip(wind_monitor['w_speeds'],
                                          wind_monitor['w_gusts'],
                                          wind_monitor['w_dirs']):
            yield "{},{},{},{}\n".format(speed['time'],
                                         speed['value'],
                                         gust['value'],
                                         direction['value'])  

    @cherrypy.expose
    def temphumi_monitor(self, **kwargs):
        q = check_GET(kwargs)
        temphumi_monitor = self.weather.temphumi_graph_data(**q)
        header = "time,T(ins),T(out),Humi(ins),Humi(out)\n"
        yield header
        for Thin, Thout in zip(temphumi_monitor['th_ins'],
                               temphumi_monitor['th_outs']):
            tm_temp = str(Thin["time"]).strip()
            temp_in_val = str(Thin["Temp"]).strip()
            temp_out_val = str(Thout["Temp"]).strip()
            hum_in_val = str(Thin["Hum"]).strip()
            hum_out_val = str(Thout["Hum"]).strip()
            yield "{},{},{},{},{}\n".format(tm_temp,
                                            temp_in_val,
                                            temp_out_val,
                                            hum_in_val,
                                            hum_out_val)

    @cherrypy.expose
    def usense_temphumi_monitor(self, **kwargs):
        q = check_GET(kwargs)
        usense_temphumi_monitor = self.iot.usense_temphumi_graph_data(**q)
        header = "time,T(tea),Humi(tea)\n"
        yield header
        for temp_humi in usense_temphumi_monitor['temphumis']:
            tm_temp = temp_humi["time"]
            temp_tea_val = temp_humi["temp"]
            hum_tea_val = temp_humi["hum"]
            yield "{},{},{}\n".format(tm_temp, temp_tea_val, hum_tea_val)

    @cherrypy.expose
    def pressure_monitor(self, **kwargs):
        q = check_GET(kwargs)
        pressure_monitor = self.weather.pressure_graph_data(**q)
        header = "time,Pressure\n"
        yield header
        for Press, Tout in zip(pressure_monitor["press_raws"],
                             pressure_monitor["Touts"]):
            tm = str(Press["time"]).strip()
            pressure = self.helpers.pressure_to_std_atm(Press["pressure"],
                                                        Tout["Tout"],
                                                        height_above_sea_level)
            yield "{},{}\n".format(tm, pressure)

    @cherrypy.expose
    def cpumem_monitor(self, **kwargs):
        q = check_GET(kwargs)
        cpumem_monitor = self.status.cpumem_graph_data(**q)
        header = "time,Cpu,Mem,Disk\n"
        yield header
        for cpu, disk, mem in zip(cpumem_monitor["cpus"],
                                  cpumem_monitor["disks"],
                                  cpumem_monitor["mems"]):
            tm = str(cpu["time"]).strip()
            cpu = str(cpu["usage"]).strip()
            mem = str(mem["usage"]).strip()
            disk = str(disk["usage"]).strip()
            yield "{},{},{},{}\n".format(tm, cpu, mem, disk)

    @cherrypy.expose
    def network_monitor(self, **kwargs):
        q = check_GET(kwargs)
        network_monitor = self.status.network_graph_data(**q)
        header = "time,Bin,Bout,Din,Dout,Ein,Eout\n"
        yield header
        for traf in network_monitor["traffic"]:
            tm = str(traf["time"]).strip()
            Bin = str(traf["traffic_b_in"]/1024).strip()
            Bout = str(traf["traffic_b_out"]/1024).strip()
            Din = str(traf["traffic_drop_in"]).strip()
            Dout = str(traf["traffic_drop_out"]).strip()
            Ein = str(traf["traffic_e_in"]).strip()
            Eout = str(traf["traffic_e_out"]).strip()
            yield "{},{},{},{},{},{},{}\n".format(
                tm,
                Bin,
                Bout,
                Din,
                Dout,
                Ein,
                Eout
            )

    @cherrypy.expose
    def solcap_monitor(self, **kwargs):
        q = check_GET(kwargs)
        solcap_monitor = self.status.solcap_graph_data(**q)
        header = "time,Solar,Capacitor\n"
        yield header
        for Sol, Cap in zip(solcap_monitor['sols'],
                            solcap_monitor['caps']):
            tm = str(Sol["time"]).strip()
            solar_value = float(str(Sol["voltage"]).strip()) / 100
            cap_value = float(str(Cap["voltage"]).strip())
            yield "{},{},{}\n".format(tm, solar_value, cap_value)

    @cherrypy.expose
    def esp_battery_monitor(self, **kwargs):
        q = check_GET(kwargs)
        place_tag = q['type']
        esp_bat_monitor = self.iot.esp_battery_graph_data(**q)
        header = "time,batt({_place_tag}),batt_perc({_place_tag})\n".format(
            _place_tag=place_tag
        )
        yield header
        for batt in esp_bat_monitor['volts']:
            tm_batt = str(batt["time"]).strip()
            try:
                batt_val = str(float(batt["voltage"]) / 1023).strip()
            except:
                batt_val = 0
            batt_perc = 4.39
            yield "{},{},{}\n".format(tm_batt, batt_val, batt_perc)
                

class DynamicStatus(object):
    def __init__(self):
        self.influx_status_client = config.Conf.influx_status_client
        
    def cpumem_graph_data(self, **q):
        '''
        Function to get RasPi value readings from InfluxDB.
        These parsed into a CSV
        '''
        query = "SELECT mean(usage) AS usage "\
              + "FROM RasPI "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_status_client.query(query)
        cpu = db_results.get_points(measurement='RasPI',
                                        tags={'type': 'cpu'})
        disk = db_results.get_points(measurement='RasPI',
                                      tags={'type': 'disk'})
        mem = db_results.get_points(measurement='RasPI',
                                       tags={'type': 'mem'})
        cpus = [cpu_use for cpu_use in cpu]
        disks = [disks_use for disks_use in disk]
        mems = [mems_use for mems_use in mem]
        # Let's get the data from DB
        result = {'cpus':cpus, 'disks':disks, 'mems':mems}
        return result

    def network_graph_data(self, **q):
        '''
        Function to get RasPi value readings from InfluxDB.
        These parsed into a CSV
        '''
        query = "SELECT derivative(max(*)) AS traffic "\
              + "FROM net "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_status_client.query(query)
        traffic = db_results.get_points(measurement='net',
                                        tags={'type': q['type']})

        traffics = [traf for traf in traffic]
        result = {'traffic': traffics}
        return result

    def solcap_graph_data(self, **q):
        '''
        Function to get RasPi value readings from InfluxDB.
        These parsed into a CSV
        '''
        query = "SELECT mean(voltage) as voltage "\
              + "FROM iss "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_status_client.query(query)
        sol = db_results.get_points(measurement='iss',
                                      tags={'type': 'solar'})
        cap = db_results.get_points(measurement='iss',
                                      tags={'type': 'capcaitor'})

        sols = [solar for solar in sol]
        caps = [capacitor for capacitor in cap]
        result = {'sols': sols, 'caps': caps}
        return result



class DynamicIoT(object):
    ''' All IoT related methods. Currently, this goes to the weatherDB,
    but is subject to change in the future. 
    '''
    def __init__(self):
        self.influx_iot_client = config.Conf.influx_iot_client

    def esp_battery_graph_data(self, **q):
        '''
        Function to get RasPi value readings from InfluxDB.
        These parsed into a CSV
        '''
        query = "SELECT mean(battery) as voltage "\
              + "FROM usense "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_iot_client.query(query)
        volt = db_results.get_points(measurement='usense',
                                      tags={'type': q['type']})

        volts = [bat_volt for bat_volt in volt]
        result = {'volts': volts}
        return result

    def usense_temphumi_graph_data(self, **q):
        '''
        Function to get RasPi value readings from InfluxDB.
        These parsed into a CSV
        '''
        query = "SELECT mean(temperature) as temp, "\
              + "mean(humidity) as hum "\
              + "FROM usense "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_iot_client.query(query)
        temphumi = db_results.get_points(measurement='usense',
                                      tags={'type': q['type']})

        temphumis = [temp_humi for temp_humi in temphumi]
        result = {'temphumis': temphumis}
        return result


class DynamicWeather(object):
    '''Weather reports, taken dynamically from InfluxDB.
    All measurements tailored to suit the Davis Vantage Vue weather
    station'''
    def __init__(self):
        self.influx_weather_client = config.Conf.influx_weather_client
        
    def wind_graph_data(self, **q):
        '''Function to get wind value readings from InfluxDB.
        These parsed into a CSV

        yields: csv in raw, text format
            time, Speed, Gusts, Direction
        '''
        query = "SELECT mean(value) AS value FROM wind "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_weather_client.query(query)
        w_speed = db_results.get_points(measurement='wind',
                                        tags={'type': 'speed'})
        w_dir = db_results.get_points(measurement='wind',
                                      tags={'type': 'direction'})
        w_gust = db_results.get_points(measurement='wind',
                                       tags={'type': 'windgust'})
        w_speeds = [speed for speed in w_speed]
        w_dirs = [direction for direction in w_dir]
        w_gusts = [gust for gust in w_gust]
        # Let's get the data from DB
        result = {'w_speeds':w_speeds, 'w_dirs':w_dirs, 'w_gusts':w_gusts}
        return result

    def temphumi_graph_data(self, **q):
        '''Function to get ttmper and humidity value readings from InfluxDB.
        These parsed into a CSV

        yields: csv in raw, text format
            time, Speed, Gusts, Direction
        '''
        query = "SELECT mean(humidity) AS Hum, "\
              + "mean(temperature) AS Temp "\
              + "FROM temphumi "\
              + "WHERE time > NOW() - {} "\
              + "AND time < NOW() - {} " \
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_weather_client.query(query)
        th_in = db_results.get_points(measurement='temphumi',
                                        tags={'type': 'internal'})
        th_out = db_results.get_points(measurement='temphumi',
                                      tags={'type': 'external'})

        th_ints = [temphumi_in for temphumi_in in th_in]
        th_outs = [temphumi_out for temphumi_out in th_out]
        # Let's get the data from DB
        result = {'th_ins':th_ints, 'th_outs':th_outs}
        return result 

    def pressure_graph_data(self, **q):
        '''
        Function to get pressure readings from InfluxDB.
        These parsed into a CSV

        yields: csv in raw, text format
            time, Pressure

        '''
        query = "SELECT mean(pressure) AS pressure, "\
              + "mean(temperature) as Tout "\
              + "FROM temphumi "\
              + "WHERE type = 'raw' OR type='external' "\
              + "AND time > NOW() - {} "\
              + "AND time < NOW() - {} "\
              + "GROUP BY time({}), type "\
              + "FILL(previous) "\
              + "ORDER BY time ASC"
              
        query = query.format(q['range'],
                             q['end'],
                             q['granularity'])
        db_results = self.influx_weather_client.query(query)
        press_raws = db_results.get_points(measurement='temphumi',
                                          tags={'type': 'raw'})
        Touts = db_results.get_points(measurement='temphumi',
                                          tags={'type': 'external'})                                  
        result = {'press_raws': press_raws, 'Touts': Touts}
        return result 
