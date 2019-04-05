#!/usr/bin/python3
'''
Generic, system-wide variables and functions to be used in any / every module
Global variables are defined with _variable_name schema, to be quickly
identified in the project. 
'''
import os
import influxdb
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
_templates = '/templates/'


# Functions
def read_html(filename, _STATIC_DIR):
    '''Read a html file

    Reads a file from a selected static directory - needs to be set as static
    in the cherrypy (chttpd.py).

    Args:
        ``filename`` *str()*, plain filename, without any path specification,
        without extension 
        ``_STATIC_DIR`` *str()*, path relative to the project root,
        where chttpd.py resides

    Returns:
        *str()*, parsed html code from the read file, or a HTML
        formatted error if file cannot be read for any reason

    Exceptions:
        On file read fail, string with Exception text is returned
        
    '''
    read_path = SCRIPT_PATH + _STATIC_DIR + filename + '.html'
    try:
        with open(read_path, 'r') as handle:
            return handle.read()
    except Exception as e:
        return """<div>ERROR: {}!</div><br>{}""".format(e, read_path)


#Classes
class serverConfiguration(object):
    '''Sets up Conf with appropriate values

    Creates an object that holds the configuration to the whole web server,
    is available throughout the project. This separates the .ini style config
    and the config.py script, that uses additional logic.
    '''
    def __init__(self):
        '''Init Conf values

        Sets up all values in config.Conf.val['option']=value

        Args:
            N/A

        Returns:
            N/A

        Sets:
            dict(self.val[option]): Set via read_config() method,
            does some additional calculations and parsing.
        '''
        if self.read_config('plutonium'):
            print("INFO: Config read success")
            print(self.val)
            self.val['_server_uri'] = \
                "{}://{}".format(
                    self.val['_server_protocol'],
                    self.val['_server_name']
                )
            self.val['_server_port'] = int(self.val['_server_port'])
            self.val['_influx_port'] = int(self.val['_influx_port'])
        else:
            print("ERROR: In reading config")

        self.influx_connectors()

    def influx_connectors(self):
        '''Set up client objects for InfluxDB

        All DB connector objects in one place. Callable from other modules

        Args:
            None

        Sets:
            ``self.influx_weather_client``,
            ``self.influx_voltage_client``,
            ``self.influx_iot_client``,
            ``self.influx_status_client``: Influx client connector objects
            
        Returns:
            N/A
            
        '''
        
        self.influx_weather_client = influxdb.client.InfluxDBClient(
            self.val['_influx_host'],
            self.val['_influx_port'],
            self.val['_influx_user'],
            self.val['_influx_pwd'],
            self.val['_influx_weather_db']
        )
        self.influx_voltage_client = influxdb.client.InfluxDBClient(
            self.val['_influx_host'],
            self.val['_influx_port'],
            self.val['_influx_user'],
            self.val['_influx_pwd'],
            self.val['_influx_voltage_db']
        )
        self.influx_iot_client = influxdb.client.InfluxDBClient(
            self.val['_influx_host'],
            self.val['_influx_port'],
            self.val['_influx_user'],
            self.val['_influx_pwd'],
            self.val['_influx_IoT_db']
        )
        self.influx_status_client = influxdb.client.InfluxDBClient(
            self.val['_influx_host'],
            self.val['_influx_port'],
            self.val['_influx_user'],
            self.val['_influx_pwd'],
            self.val['_influx_status_db']
        )
            
        
    def read_config(self, conf_filename):
        '''Reads configuration file
    
        Read and parse the configuration options into a dictionary
        Why not using configparser? No idea, subject to change.
        This method is called on class init. 
    
        Args:
            ``conf_filename``, *str()* file name without the .ini extension,
            residing in ./config directory
    
        Returns:
            *dict()*, On success
            
            *bool(False)*, On failure

        Sets:
            ``self.dict()`` of name_value_pairs read from the config file
        
        '''
        read_path = SCRIPT_PATH + '/config/' + conf_filename + '.ini'
        try:
            with open(read_path, 'r') as conf_file:
                config_list = conf_file.readlines()
        except OSError as e:
            print("ERROR: {}".format(e))
            return False
        self.val = {}
        for line in config_list:
            if line.strip() != '':
                try:
                    line = line.split("=")
                    option = line[0].strip().strip("'")
                    value = line[1].strip().strip("'")
                except:
                    exit("WARNING: Wrong format of config option")
                    return False
                self.val.update({option:value})
            else:
                pass
        return self.val 

Conf = serverConfiguration()
