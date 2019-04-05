var hours = 24;
var granularity = '1m';
var end = 0;
var winddata = "https://bastart.spoton.cz/data/wind_monitor?range=24h&granularity=5m&end=0h";
var temphumidata = "https://bastart.spoton.cz/data/temphumi_monitor?range=24h&granularity=5m&end=0h";
var pressuredata = "https://bastart.spoton.cz/data/pressure_monitor?range=168h&granularity=5m&end=0h";
wind = new Dygraph(
// containing div
document.getElementById("wind"),
// CSV or path to a CSV file.
winddata
,{
    //labels: ['time','Speed','Gust', 'Direction'],
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
                valueRange: [0,360],
                independentTicks: true
            }
    },
    rollPeriod: 5,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'Speed': {
            axis: 'y',
            color: '#444444',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'Gusts': {
            axis: 'y',
            color: '#ff5555'
        },
        'Direction': {
            axis: 'y2',
            color: '#999999'
        }

    },
        ylabel: '<span style="color:#444444;">Speed<span style="color:#444444;"> / <span style="color:#ff5555;">Gusts</span> [km/h]',
        y2label: '<span style="color:#999999;">Direction [&deg;]</span>',
        labelsDiv: 'wind_labels',
        legend: 'always'
    }
);

temphumi_out = new Dygraph(
// containing div
document.getElementById("temphumi"),
// CSV or path to a CSV file.
temphumidata
,{
    //labels: [time,T(ins),T(out),Humi(ins),Humi(out)],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : false
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
    visibility: [false, true, false, true],
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'T(out)': {
            axis: 'y',
            color: '#705555',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'T(ins)': {
            axis: 'y',
            color: '#705555',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'Humi(out)': {
            axis: 'y2',
            color: '#222288'
        },
        'Humi(ins)': {
            axis: 'y2',
            color: '#222288'
        }

    },
        ylabel: '<span style="color:#555555;">Outside [&deg;C]</span>',
        y2label: '<span style="color:#222288;">Humidity [%]</span>',
        labelsDiv: 'temphumi_labels',
        legend: 'always'
    }
);

temphumi_in = new Dygraph(
// containing div
document.getElementById("temphumi_in"),
// CSV or path to a CSV file.
temphumidata
,{
    //labels: [time,T(ins),T(out),Humi(ins),Humi(out)],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [10,35]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                independentTicks: true,
                valueRange: [0,100]
            }
    },
    rollPeriod: 5,
    visibility: [true, false, true, false],
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'T(out)': {
            axis: 'y',
            color: '#705555',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'T(ins)': {
            axis: 'y',
            color: '#705555',
            fillGraph: true,
            fillAlpha: 0.2
        },
        'Humi(out)': {
            axis: 'y2',
            color: '#222288'
        },
        'Humi(ins)': {
            axis: 'y2',
            color: '#222288'
        }

    },
        ylabel: '<span style="color:#555555;">Inside [&deg;C]</span>',
        y2label: '<span style="color:#222288;">Humidity [%]</span>',
        labelsDiv: 'temphumi_labels_in',
        legend: 'always'
    }
);

pressure = new Dygraph(
// containing div
document.getElementById("pressure"),
// CSV or path to a CSV file.
pressuredata
,{
    //labels: [time,Pressure],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [970,1055]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                valueRange: [970,1055]
            }
    },
    rollPeriod: 20,
    interactionModel: {},
    connectSeparatedPoints: true,
    visibility: [true, false],
    series:{
        'Pressure': {
            axis: 'y',
            color: '#557070',
            fillGraph: true,
            fillAlpha: 0.5
        },
        'Pressure': {
            axis: 'y2',
            color: '#557070',
            fillGraph: true,
            fillAlpha: 0.5
        }

    },
        ylabel: '<span style="color:#555555;">Pressure [hPa]</span>',
        labelsDiv: 'pressure_labels',
        legend: 'always'
    }
);


function refreshGraph(source){
  graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h";
  if(source == 'wind_monitor'){
      wind.updateOptions({'file': graphdata});
  }
  if(source == 'temphumi_monitor'){
      temphumi_out.updateOptions({'file': graphdata});
      temphumi_in.updateOptions({'file': graphdata});
  }
  if(source == 'pressure_monitor'){
      pressure.updateOptions({'file': graphdata});
  }
  //document.getElementById('xxx').innerHTML = source;
  //power.updateOptions({'file': graphdata});
}

function setHours(hours_to_set, target){
  hours = hours_to_set;
  switch(hours){
      case '1':
        granularity = '1m';
        if(target == 'temphumi_monitor'){ granularity = '2m';}
        break;
      case '6':
        granularity = '2m';
        if(target == 'temphumi_monitor'){ granularity = '2m';}
        break;
      case '12':
        granularity = '5m';
        if(target == 'temphumi_monitor'){ granularity = '2m';}
        break;
      case '24':
        granularity = '5m';
        if(target == 'temphumi_monitor'){ granularity = '2m';}
        break;
      case '168':
        granularity = '30m';
        break;
      case '720':
        granularity = '3h';
        break;
      case '4320':
        granularity = '1d';
        break;
      case '8640':
        granularity = '7d';
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
