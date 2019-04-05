#!/usr/bin/python3
import cherrypy
import influxdb

from modules import dynamic
import config


class EnergyInfo(object):
    def __init__(self):
        base_url = 'https://bastart.spoton.cz/static'
        self.array_full = base_url + '/img/battery_full.png' #100-90
        self.array_80 =  base_url + '/img/battery_80.png'     # 90-70
        self.array_60 =  base_url + '/img/battery_60.png'     # 70-50
        self.array_40 =  base_url + '/img/battery_40.png'     # 50-30
        self.array_20 =  base_url + '/img/battery_20.png'     # 30-10
        self.array_0 =  base_url + '/img/battery_0.png'       # 10-0
        self.array_ch =  base_url + '/img/battery_charging.png'
        self.charge_current_icon =  base_url + '/img/battery_current.png'
        self.solar_power_icon =  base_url + '/img/solar_power.png'
        self.battery_icon = self.array_full
        self.measures_obj = dynamic.DynamicEnergy()

    @cherrypy.expose
    def index(self):
        header = config.read_html('header', config._templates)
        menu_raw = config.read_html('top_menu', config._templates)
        menu = menu_raw.format(energy = 'active',
                               weather = '',
                               status = '',
                               temphumi = '')
        body = self.body()
        footer = config.read_html('footer', config._templates)
        result = header\
               + menu\
               + body\
               + footer
        return result

    def set_battery_icon(self, percentage, state):
        ''' Interprets % of battery state in icon changes

            expects:
                float(percentage): Percentage -> battery icon

            sets:
                str(self.battery_icon): the path to appropriate icon image
        '''
        if state == 1:
            self.battery_icon = self.array_ch
        else:
            if percentage > 70.0 and percentage < 89.9:
                self.battery_icon = self.array_80
            if percentage > 50.0 and percentage < 69.9:
                self.battery_icon = self.array_60
            if percentage > 30.0 and percentage < 49.9:
                self.battery_icon = self.array_40
            if percentage > 10.0 and percentage < 29.9:
                self.battery_icon = self.array_20
            if percentage > 0.0 and percentage < 9.9:
                self.battery_icon = self.array_0

    def tableConstructor(self, header, body):
        ''' The idea behind is to have a method of constructing <table> html
        element and to separate data and html code.

        expects:
            list(header): [str(header1), str(header2), ...]
            list(body): [str(td1), str(td2), ...], row2, row3, ...]

        returns:
            str(html_table)
        '''
        table_header = ''
        table_body = ''
        table_begin = '<table class="table table-striped">'
        thead = '<thead>'
        thead_end = '</thead>'
        tbody = '<tbody>'
        tbody_end = '</tbody>'
        table_end = '</table>'
        table_header = '</tr>'
        for th in header:
            table_header = table_header + '<th>' + th + '</th>'
        table_header = table_header + '</tr>'
        for tr in body:
            table_body = table_body + '<tr>'
            for td in tr:
                table_body = table_body + '<td>' + str(td) + '</td>'
            table_body = table_body + '</tr>'

        html_table = "{} {} {} {} {}".format(
            table_begin + thead,
            table_header,
            thead_end + tbody,
            table_body,
            tbody_end + table_end
        )
        return html_table

    def body(self):
        current_values = self.measures_obj.FreshValues(type='dict')
        fresh_voltage_array = float(current_values['V_array'])
        self.set_battery_icon(current_values['perc_array'], 0)
        # Table with statistical values
        stat_header = ['Date',
                       'Pmax [W]',
                       'Pday [Wh]']
        stats_content = self.measures_obj.stat_values(days = 7)
        stats_table = self.tableConstructor(stat_header, stats_content)
        # Format and output HTML fot he whole page
        admin_preformat = config.read_html('voltage_admin', config._templates)
        admin_html = admin_preformat.format(
            timestamp = current_values['time'],
            array_voltage = fresh_voltage_array,
            charge_current = current_values['ChCurr'],
            solar_power = current_values['Psol'],
            pmax_day = current_values['Pmax_day'],
            charge_current_icon = self.charge_current_icon,
            solar_power_icon = self.solar_power_icon,
            array_voltage_icon = self.battery_icon,
            array_percent = current_values['perc_array'],
            stats_table = stats_table
        )
        return admin_html
