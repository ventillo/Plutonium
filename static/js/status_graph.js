var hours = 24;
var granularity = '2m';
var end = 0;
var network_type='wlan0'
var iot_type='Tea'
var solcapdata = "https://bastart.spoton.cz/data/solcap_monitor?range=24h&granularity=2m&end=0h";
var cpumemdata = "https://bastart.spoton.cz/data/cpumem_monitor?range=24h&granularity=2m&end=0h";
var networkdata = "https://bastart.spoton.cz/data/network_monitor?range=24h&granularity=2m&end=0h&type=wlan0";
var espbattdata = "https://bastart.spoton.cz/data/esp_battery_monitor?range=4320h&granularity=5h&end=0h&type=Tea";

solcap = new Dygraph(
// containing div
document.getElementById("solcap"),
// CSV or path to a CSV file.
solcapdata
,{
    //labels: ['time','Solar','Capacitor'],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [0,4.6]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                valueRange: [0,8.6],
                independentTicks: true
            }
    },
    rollPeriod: 5,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'Solar': {
            axis: 'y',
            color: '#888844',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'Capacitor': {
            axis: 'y2',
            color: '#884444'
        }

    },
        ylabel: '<span style="color:#888844;">Solar Irradiance</span>',
        y2label: '<span style="color:#884444;">Capacitor [V]</span>',
        labelsDiv: 'solcap_labels',
        legend: 'always'
    }
);


cpumem = new Dygraph(
// containing div
document.getElementById("cpumem"),
// CSV or path to a CSV file.
cpumemdata
,{
    //labels: ['time','Cpu','Mem','Disk'],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [0,100]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                valueRange: [0,100],
                independentTicks: true
            }
    },
    rollPeriod: 5,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'Cpu': {
            axis: 'y',
            color: '#888844',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'Mem': {
            axis: 'y2',
            color: '#884444'
        },
        'Disk': {
            axis: 'y2',
            color: '#448844'
        }

    },
        ylabel: '<span style="color:#888844;">CPU [%]</span>',
        y2label: '<span style="color:#884444;">MEM / DISK [%]</span>',
        labelsDiv: 'cpumem_labels',
        legend: 'always'
    }
);

network = new Dygraph(
// containing div
document.getElementById("network"),
// CSV or path to a CSV file.
networkdata
,{
    //labels: ['time','Bin, Bout','Din', 'Dout', 'Ein','Eout'],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                independentTicks: true
            }
    },
    rollPeriod: 5,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'Bin': {
            axis: 'y',
            color: '#888844',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'Bout': {
            axis: 'y',
            color: '#448888',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'Din': {
            axis: 'y2',
            color: '#ff5500'
        },
        'Dout': {
            axis: 'y2',
            color: '#ff5500'
        },
        'Ein': {
            axis: 'y2',
            color: '#ff2233',
            fillAlpha: 0.5
        },
        'Eout': {
            axis: 'y2',
            color: '#ff2233',
            fillAlpha: 0.5
        }

    },
        ylabel: '<span style="color:#888844;">kBytes</span>',
        y2label: '<span style="color:#ff2233;">Drop / Error</span>',
        labelsDiv: 'network_labels',
        legend: 'always'
    }
);

esp_battery = new Dygraph(
// containing div
document.getElementById("esp_battery"),
// CSV or path to a CSV file.
espbattdata
,{
    //labels: ['time','batt(Tea)'],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [2.5,4.5]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                valueRange: [2.5,4.5],
                independentTicks: true
            }
    },
    rollPeriod: 5,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'batt(Tea)': {
            axis: 'y',
            color: '#888844',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'batt_perc(Tea)': {
            axis: 'y2',
            color: '#884444'
        }

    },
        ylabel: '<span style="color:#888844;">Battery (Tea) [V]</span>',
        y2label: '<span style="color:#884444;">Top charge [V]</span>',
        labelsDiv: 'esp_battery_labels',
        legend: 'always'
    }
);

function refreshGraph(source){
  graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h";
  if(source == 'solcap_monitor'){
    solcap.updateOptions({'file': graphdata});
  }
  if(source == 'cpumem_monitor'){
    cpumem.updateOptions({'file': graphdata});
  }
  if(source == 'esp_battery_monitor'){
    graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h&type=" + iot_type;
    esp_battery.updateOptions({'file': graphdata});
  }
  if(source == 'network_monitor'){
    graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h&type=" + network_type;
    network.updateOptions({'file': graphdata});
  }
  //document.getElementById('xxx').innerHTML = source;
  //power.updateOptions({'file': graphdata});
}

function setHours(hours_to_set, target){
  hours = hours_to_set;
  switch(hours){
      case '1':
        granularity = '20s';
        break;
      case '6':
        granularity = '30s';
        break;
      case '12':
        granularity = '1m';
        break;
      case '24':
        granularity = '2m';
        break;
      case '168':
        granularity = '10m';
        break;
      case '720':
        granularity = '1h';
        break;
      case '4320':
        granularity = '3h';
        break;
      case '8640':
        granularity = '1d';
        break;
      default:
        granularity = '10m';
  }
  end = 0;
  //document.getElementById('xxx').innerHTML = target;
  refreshGraph(target);
}

function setBack(target){
    // range=1h -> range=2h&end=1h
    disp_range = hours*1 - end*1;
    hours = hours*1 + disp_range;
    end = end*1 + disp_range;
    //document.getElementById('xxx').innerHTML = graphdata;
    refreshGraph(target);
}

function setForth(target){
    disp_range = hours*1 - end*1;
    hours = hours*1 - disp_range;
    if(hours < disp_range){
        hours = disp_range;
    }
    end = end*1 - disp_range;
    if(end < 0){
        end = 0;
    }
    //document.getElementById('xxx').innerHTML = graphdata;
    refreshGraph(target);
}
