var hours = 168;
var granularity = '30m';
var end = 0;
var tea_temphumidata = "https://bastart.spoton.cz/data/usense_temphumi_monitor?range=168h&granularity=30m&end=0h&type=Tea";

tea_temphum = new Dygraph(
// containing div
document.getElementById("tea_temphum"),
// CSV or path to a CSV file.
tea_temphumidata
,{
    //labels: ['time','Temperature','Humidity'],
    axes : {
            x : {
                drawGrid: true,
                drawAxis : true
            },
            y : {
                drawGrid: false,
                drawAxis : true,
                valueRange: [0,40]
            },
            y2 : {
                drawGrid: false,
                drawAxis: true,
                valueRange: [20,80],
                independentTicks: true
            }
    },
    rollPeriod: 20,
    interactionModel: {},
    connectSeparatedPoints: true,
    series:{
        'T(tea)': {
            axis: 'y',
            color: '#55ff00',
            fillGraph: true,
            fillAlpha: 0.4
        },
        'Humi(tea)': {
            axis: 'y2',
            color: '#0088ff'
        }

    },
        ylabel: '<span style="color:#55ff00;">Temperature [&deg;C]</span>',
        y2label: '<span style="color:#0088ff;">Humidity [%]</span>',
        labelsDiv: 'tea_labels',
        legend: 'always'
    }
);



function refreshGraph(source){
  //graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h&type=" + type;
  if(source == 'usense_temphumi_monitor'){
      type = "Tea"
      graphdata = "https://bastart.spoton.cz/data/" + source + "?range=" + hours + "h&granularity=" + granularity + "&end=" + end + "h&type=" + type;
      tea_temphum.updateOptions({'file': graphdata});
  }
  //document.getElementById('xxx').innerHTML = graphdata;
}

function setHours(hours_to_set, target){
  hours = hours_to_set;
  switch(hours){
      case '6':
        granularity = '10m';
        break;
      case '12':
        granularity = '10m';
        break;
      case '24':
        granularity = '10m';
        break;
      case '168':
        granularity = '30m';
        break;
      case '720':
        granularity = '1h';
        break;
      case '4320':
        granularity = '3h';
        break;
      case '8640':
        granularity = '12h';
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
